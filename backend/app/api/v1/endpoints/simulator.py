import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import get_db
from backend.app.schemas.simulator import SimulatorScenarioRequest, SimulatorComparisonResponse
from backend.app.ml.predictor import predict_transaction_risk
from backend.app.engine.scorer import compute_composite_risk
from backend.app.utils.geo import normalize_to_utc

router = APIRouter()


@router.post("/evaluate", response_model=SimulatorComparisonResponse, status_code=status.HTTP_200_OK)
async def evaluate_simulator_scenario(
    payload: SimulatorScenarioRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluates a What-If Risk Simulation scenario:
    Compares baseline transaction against user-modified parameters,
    identifying exact score deltas, category transitions, and primary drivers.
    """
    b_in = payload.baseline_transaction
    m_in = payload.modified_transaction

    b_time = normalize_to_utc(b_in.transaction_timestamp) or datetime.now(timezone.utc)
    m_time = normalize_to_utc(m_in.transaction_timestamp) or datetime.now(timezone.utc)

    # 1. Evaluate Baseline
    b_xgb, b_iforest, b_shap = predict_transaction_risk(
        amount=b_in.amount,
        payment_method=b_in.payment_method,
        merchant_category=b_in.advanced_details.merchant_category if b_in.advanced_details else "general",
        is_device_familiar=b_in.is_device_familiar,
        hour=b_time.hour
    )
    b_res = compute_composite_risk(
        amount=b_in.amount,
        payment_method=b_in.payment_method,
        location_city=b_in.location_city,
        is_device_familiar=b_in.is_device_familiar,
        curr_timestamp=b_time,
        xgb_fraud_prob=b_xgb,
        iforest_outlier_score=b_iforest,
        raw_shap_list=b_shap,
        transaction_ref=f"SIM-BASE-{uuid.uuid4().hex[:6].upper()}"
    )

    # 2. Evaluate Modified
    m_xgb, m_iforest, m_shap = predict_transaction_risk(
        amount=m_in.amount,
        payment_method=m_in.payment_method,
        merchant_category=m_in.advanced_details.merchant_category if m_in.advanced_details else "general",
        is_device_familiar=m_in.is_device_familiar,
        hour=m_time.hour
    )
    m_res = compute_composite_risk(
        amount=m_in.amount,
        payment_method=m_in.payment_method,
        location_city=m_in.location_city,
        is_device_familiar=m_in.is_device_familiar,
        curr_timestamp=m_time,
        xgb_fraud_prob=m_xgb,
        iforest_outlier_score=m_iforest,
        raw_shap_list=m_shap,
        transaction_ref=f"SIM-MOD-{uuid.uuid4().hex[:6].upper()}"
    )

    score_delta = round(m_res.overall_risk_score - b_res.overall_risk_score, 1)
    cat_changed = b_res.risk_category != m_res.risk_category
    action_changed = b_res.recommended_action != m_res.recommended_action

    # Identify primary driver
    drivers = []
    if m_in.amount != b_in.amount:
        amt_diff = m_in.amount - b_in.amount
        drivers.append(f"Amount adjusted by {amt_diff:+,.2f} USD")
    if m_in.is_device_familiar != b_in.is_device_familiar:
        status_text = "known verified device" if m_in.is_device_familiar else "unfamiliar device"
        drivers.append(f"Device switched to {status_text}")
    if m_in.location_city != b_in.location_city:
        drivers.append(f"Location moved from {b_in.location_city} to {m_in.location_city}")
    if m_in.payment_method != b_in.payment_method:
        drivers.append(f"Payment method switched to {m_in.payment_method}")

    primary_driver = "; ".join(drivers) if drivers else "No parameter variance detected."

    # Narrative takeaway
    if score_delta < 0:
        takeaway = (
            f"Risk decreased by {abs(score_delta)} points (from {b_res.overall_risk_score} to {m_res.overall_risk_score}). "
            f"Action transitioned to {m_res.recommended_action}."
        )
    elif score_delta > 0:
        takeaway = (
            f"Risk increased by {score_delta} points (from {b_res.overall_risk_score} to {m_res.overall_risk_score}). "
            f"Action escalated to {m_res.recommended_action}."
        )
    else:
        takeaway = "Modifications produced neutral net risk change."

    return SimulatorComparisonResponse(
        baseline=b_res,
        modified=m_res,
        score_delta=score_delta,
        category_changed=cat_changed,
        action_changed=action_changed,
        primary_influencing_change=primary_driver,
        takeaway_summary=takeaway
    )
