from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from backend.app.config import settings
from backend.app.schemas.risk_result import (
    RiskAssessmentResponse,
    ModelDiagnostics
)
from backend.app.engine.rules import evaluate_deterministic_rules
from backend.app.engine.behavioral import calculate_behavioral_deviation
from backend.app.engine.translator import (
    generate_persona_explanations,
    translate_shap_contributions
)
from backend.app.utils.geo import normalize_to_utc


def compute_composite_risk(
    amount: float,
    payment_method: str,
    location_city: str,
    is_device_familiar: bool,
    curr_timestamp: datetime,
    xgb_fraud_prob: float,
    iforest_outlier_score: float,
    raw_shap_list: List[Dict[str, Any]],
    transaction_ref: str,
    user_identifier: Optional[str] = None,
    ip_address: str = "127.0.0.1",
    user_baseline: Optional[Dict[str, Any]] = None,
    prev_location_city: Optional[str] = None,
    prev_timestamp: Optional[datetime] = None,
    currency: str = "USD"
) -> RiskAssessmentResponse:
    """
    Core Multi-Layer Risk Evaluation Engine:
    Combines Deterministic Rules, Supervised ML (XGBoost), Unsupervised Outliers (Isolation Forest),
    and Personal Behavioral Deviation into a normalized 0-100 risk score and dual-persona output.
    """
    curr_timestamp = normalize_to_utc(curr_timestamp) or datetime.now(timezone.utc)
    if prev_timestamp:
        prev_timestamp = normalize_to_utc(prev_timestamp)

    user_avg = float(user_baseline.get("avg_amount_30d", 350.0)) if user_baseline else 350.0

    # 1. Layer 1: Deterministic Rules
    rule_res = evaluate_deterministic_rules(
        amount=amount,
        location_city=location_city,
        is_device_familiar=is_device_familiar,
        curr_timestamp=curr_timestamp,
        ip_address=ip_address,
        user_avg_amount=user_avg,
        prev_location_city=prev_location_city,
        prev_timestamp=prev_timestamp
    )

    # 2. Layer 4: Behavioral Deviation Engine
    beh_res = calculate_behavioral_deviation(
        amount=amount,
        location_city=location_city,
        is_device_familiar=is_device_familiar,
        timestamp=curr_timestamp,
        baseline=user_baseline
    )

    # Convert inputs to normalized scores
    rule_score = rule_res.penalty_score
    ml_score = xgb_fraud_prob * 100.0
    iforest_score = iforest_outlier_score
    beh_score = beh_res["behavioral_score"]

    # 3. Weighted Fusion
    weighted_composite = (
        settings.WEIGHT_RULE * rule_score +
        settings.WEIGHT_XGB * ml_score +
        settings.WEIGHT_IFOREST * iforest_score +
        settings.WEIGHT_BEHAVIORAL * beh_score
    )

    final_score = min(100.0, max(0.0, weighted_composite))

    # 4. Circuit Breaker Overrides
    if rule_res.hard_override_action == "BLOCK":
        final_score = max(final_score, rule_res.override_score or 95.0)

    # Conservative Low-Risk Protection:
    # If transaction is normal amount, familiar device, and ML prob is near-zero, ensure low score
    if is_device_familiar and amount <= (user_avg * 1.2) and xgb_fraud_prob < 0.05 and not rule_res.rules_triggered:
        final_score = min(final_score, 15.0)

    final_score = round(final_score, 1)

    # 5. Risk Category and Action Determination
    if final_score <= settings.THRESHOLD_LOW:
        risk_category = "LOW"
        recommended_action = "APPROVE"
    elif final_score <= settings.THRESHOLD_MEDIUM:
        risk_category = "MEDIUM"
        recommended_action = "REVIEW"
    elif final_score <= settings.THRESHOLD_HIGH:
        risk_category = "HIGH"
        recommended_action = "BLOCK"
    else:
        risk_category = "CRITICAL"
        recommended_action = "BLOCK"

    # Override action if rule triggered hard block
    if rule_res.hard_override_action == "BLOCK":
        recommended_action = "BLOCK"

    # 6. Translate SHAP and explanations
    top_shap = translate_shap_contributions(raw_shap_list)

    diagnostics = ModelDiagnostics(
        xgb_fraud_probability=round(xgb_fraud_prob, 4),
        iforest_anomaly_score=round(iforest_score, 2),
        rule_penalty_score=round(rule_score, 2),
        behavioral_deviation_score=round(beh_score, 2),
        behavioral_z_score=round(beh_res.get("z_score", 0.0), 2),
        confidence_score=96.5 if final_score > 85 or final_score < 25 else 89.0
    )

    everyday_out, analyst_out = generate_persona_explanations(
        overall_score=final_score,
        risk_category=risk_category,
        recommended_action=recommended_action,
        model_signals=diagnostics,
        rules_triggered=rule_res.rules_triggered,
        rule_details=rule_res.details,
        top_shap=top_shap,
        behavioral_insights=beh_res["insights"],
        amount=amount,
        currency=currency
    )

    return RiskAssessmentResponse(
        transaction_ref=transaction_ref,
        user_identifier=user_identifier,
        overall_risk_score=final_score,
        risk_category=risk_category,
        recommended_action=recommended_action,
        everyday_user=everyday_out,
        risk_analyst=analyst_out,
        evaluated_at=curr_timestamp
    )
