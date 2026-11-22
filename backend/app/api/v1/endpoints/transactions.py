import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List

from backend.app.database.session import get_db
from backend.app.database.models.transaction import Transaction, RiskAssessment
from backend.app.database.models.user_profile import User, UserBaseline
from backend.app.database.models.alert import Alert
from backend.app.schemas.transaction import TransactionAnalyzeRequest
from backend.app.schemas.risk_result import RiskAssessmentResponse
from backend.app.ml.predictor import predict_transaction_risk
from backend.app.engine.scorer import compute_composite_risk
from backend.app.utils.geo import resolve_city_coordinates, normalize_to_utc
from backend.app.core.auth import get_optional_current_user

router = APIRouter()


@router.post("/analyze", response_model=RiskAssessmentResponse, status_code=status.HTTP_200_OK)
async def analyze_transaction(
    payload: TransactionAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Evaluates a financial transaction in real-time.
    Supports both simple 5-field submissions (everyday user) and advanced payloads (risk analyst).
    Automatically associates transaction with the authenticated user if logged in.
    """
    # 1. Extract parameters
    amount = payload.amount
    payment_method = payload.payment_method
    location_city = payload.location_city
    is_device_familiar = payload.is_device_familiar
    tx_timestamp = normalize_to_utc(payload.transaction_timestamp) or datetime.now(timezone.utc)
    
    # User resolution: prioritize authenticated user, then advanced_details override
    user_obj = current_user
    user_id = current_user.user_identifier if current_user else (
        payload.advanced_details.user_identifier if payload.advanced_details else None
    )
    currency = (
        payload.advanced_details.currency
        if payload.advanced_details and payload.advanced_details.currency
        else (payload.currency or "USD")
    )
    merchant_category = payload.advanced_details.merchant_category if payload.advanced_details else "general"
    ip_address = payload.advanced_details.ip_address if payload.advanced_details else "127.0.0.1"
    
    # 2. Retrieve user baseline if available
    user_baseline = None
    prev_city = None
    prev_time = None
    
    if not user_obj and user_id:
        user_query = await db.execute(
            select(User).options(selectinload(User.baseline)).where(User.user_identifier == user_id)
        )
        user_obj = user_query.scalar_one_or_none()
        
    if user_obj:
        baseline_q = await db.execute(select(UserBaseline).where(UserBaseline.user_id == user_obj.id))
        b = baseline_q.scalar_one_or_none()

        if b:
            user_baseline = {
                "avg_amount_30d": float(b.avg_amount_30d),
                "std_amount_30d": float(b.std_amount_30d),
                "common_locations": b.common_locations or [],
                "usual_hours": b.usual_hour_distribution or list(range(8, 23))
            }
        # Find user's last transaction for velocity check
        last_tx_q = await db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_obj.id)
            .order_by(desc(Transaction.transaction_timestamp))
            .limit(1)
        )
        last_tx = last_tx_q.scalar_one_or_none()
        if last_tx:
            prev_city = last_tx.location_city
            prev_time = normalize_to_utc(last_tx.transaction_timestamp)

    user_avg = float(user_baseline["avg_amount_30d"]) if user_baseline else 350.0

    # 3. Execute Real ML Inference (XGBoost, Isolation Forest, SHAP)
    xgb_prob, iforest_score, top_shap = predict_transaction_risk(
        amount=amount,
        payment_method=payment_method,
        merchant_category=merchant_category,
        is_device_familiar=is_device_familiar,
        hour=tx_timestamp.hour,
        user_avg_amount=user_avg
    )

    # 4. Multi-Layer Composite Risk Evaluation
    tx_ref = f"TX-{uuid.uuid4().hex[:8].upper()}"
    assessment = compute_composite_risk(
        amount=amount,
        payment_method=payment_method,
        location_city=location_city,
        is_device_familiar=is_device_familiar,
        curr_timestamp=tx_timestamp,
        xgb_fraud_prob=xgb_prob,
        iforest_outlier_score=iforest_score,
        raw_shap_list=top_shap,
        transaction_ref=tx_ref,
        user_identifier=user_id,
        ip_address=ip_address,
        user_baseline=user_baseline,
        prev_location_city=prev_city,
        prev_timestamp=prev_time,
        currency=currency
    )

    # 5. Persist to Database for Auditing & History
    try:
        lat, lon = resolve_city_coordinates(location_city)
        db_tx = Transaction(
            transaction_ref=tx_ref,
            user_id=user_obj.id if user_obj else None,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            merchant_category=merchant_category,
            location_city=location_city,
            latitude=lat,
            longitude=lon,
            is_device_familiar=is_device_familiar,
            ip_address=ip_address,
            transaction_timestamp=tx_timestamp
        )
        db.add(db_tx)
        await db.flush()

        db_risk = RiskAssessment(
            transaction_id=db_tx.id,
            overall_risk_score=assessment.overall_risk_score,
            risk_category=assessment.risk_category,
            recommended_action=assessment.recommended_action,
            xgb_fraud_probability=assessment.risk_analyst.model_signals.xgb_fraud_probability,
            iforest_anomaly_score=assessment.risk_analyst.model_signals.iforest_anomaly_score,
            rule_penalty_score=assessment.risk_analyst.model_signals.rule_penalty_score,
            behavioral_deviation_score=assessment.risk_analyst.model_signals.behavioral_deviation_score,
            top_shap_features=[f.model_dump() for f in assessment.risk_analyst.top_shap_contributions],
            simple_explanation="; ".join(assessment.everyday_user.simple_reasons),
            technical_summary=assessment.risk_analyst.technical_summary,
            confidence_score=assessment.risk_analyst.model_signals.confidence_score,
            evaluated_at=tx_timestamp
        )
        db.add(db_risk)

        # Trigger security alert if High or Critical
        if assessment.risk_category in ("HIGH", "CRITICAL"):
            alert = Alert(
                transaction_id=db_tx.id,
                severity="CRITICAL" if assessment.risk_category == "CRITICAL" else "WARNING",
                alert_type="HIGH_RISK_TRANSACTION",
                message=f"Flagged {assessment.risk_category} risk ({assessment.overall_risk_score}/100) on {tx_ref} (${amount:,.2f}).",
                status="OPEN"
            )
            db.add(alert)

        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transaction persistence failed: {str(e)}"
        )

    return assessment


@router.get("/history", response_model=dict)
async def get_transaction_history(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    risk_category: Optional[str] = None,
    min_score: Optional[float] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Retrieves paginated audit log of analyzed transactions.
    When authenticated, isolates transactions to the logged-in user only.
    """
    query = (
        select(Transaction)
        .options(selectinload(Transaction.risk_assessment))
        .order_by(desc(Transaction.transaction_timestamp))
    )
    
    # User isolation: If logged in, show only the user's transactions
    if current_user:
        query = query.where(Transaction.user_id == current_user.id)
    else:
        query = query.where(Transaction.user_id.is_(None))
        
    if risk_category and risk_category.upper() != "ALL":
        query = query.join(Transaction.risk_assessment).where(RiskAssessment.risk_category == risk_category.upper())
        
    if min_score is not None:
        if not risk_category or risk_category.upper() == "ALL":
            query = query.join(Transaction.risk_assessment)
        query = query.where(RiskAssessment.overall_risk_score >= min_score)
    
    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    transactions = result.scalars().all()
    
    rows = []
    for tx in transactions:
        risk = tx.risk_assessment
        rows.append({
            "id": tx.id,
            "transaction_ref": tx.transaction_ref,
            "amount": float(tx.amount),
            "currency": tx.currency,
            "payment_method": tx.payment_method,
            "location_city": tx.location_city,
            "is_device_familiar": tx.is_device_familiar,
            "timestamp": (
                tx.transaction_timestamp.isoformat()
                if hasattr(tx.transaction_timestamp, "isoformat")
                else str(tx.transaction_timestamp or "")
            ),
            "risk_score": float(risk.overall_risk_score) if risk else 0.0,
            "risk_category": risk.risk_category if risk else "UNKNOWN",
            "recommended_action": risk.recommended_action if risk else "APPROVE"
        })
        
    return {
        "page": page,
        "limit": limit,
        "total": len(rows),
        "is_user_scoped": current_user is not None,
        "records": rows
    }
