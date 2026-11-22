import io
import csv
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from typing import Optional

from backend.app.database.session import get_db
from backend.app.database.models.transaction import Transaction
from backend.app.database.models.user_profile import User
from backend.app.core.auth import get_optional_current_user
from backend.app.utils.pdf_builder import generate_pdf_risk_report

router = APIRouter()


@router.get("/export/csv")
async def export_transactions_csv(
    limit: int = Query(500, ge=1, le=5000),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Generates downloadable CSV of audited transactions. Scoped to user if authenticated."""
    q = (
        select(Transaction)
        .options(selectinload(Transaction.risk_assessment))
        .order_by(desc(Transaction.transaction_timestamp))
    )
    if current_user:
        q = q.where(Transaction.user_id == current_user.id)
    else:
        q = q.where(Transaction.user_id.is_(None))
    q = q.limit(limit)
    res = await db.execute(q)
    transactions = res.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Transaction Ref", "Amount", "Currency", "Payment Method",
        "Location City", "Device Familiar", "Risk Score",
        "Risk Category", "Recommended Action", "Timestamp"
    ])

    for tx in transactions:
        risk = tx.risk_assessment
        writer.writerow([
            tx.transaction_ref,
            float(tx.amount),
            tx.currency,
            tx.payment_method,
            tx.location_city,
            tx.is_device_familiar,
            float(risk.overall_risk_score) if risk else 0.0,
            risk.risk_category if risk else "UNKNOWN",
            risk.recommended_action if risk else "APPROVE",
            tx.transaction_timestamp.isoformat()
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=transaction_risk_audit_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"}
    )


@router.get("/export/pdf")
async def export_transactions_pdf(
    ref: Optional[str] = Query(None, description="Specific transaction reference"),
    limit: int = Query(40, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Generates official institutional PDF risk audit report. Scoped to user if authenticated."""
    q = (
        select(Transaction)
        .options(selectinload(Transaction.risk_assessment))
        .order_by(desc(Transaction.transaction_timestamp))
    )
    if ref:
        q = q.where(Transaction.transaction_ref == ref)
    elif current_user:
        q = q.where(Transaction.user_id == current_user.id)
    else:
        q = q.where(Transaction.user_id.is_(None))
    q = q.limit(limit)
    res = await db.execute(q)
    transactions = res.scalars().all()

    tx_list = []
    total_score = 0.0
    low_count = 0
    high_count = 0

    for tx in transactions:
        risk = tx.risk_assessment
        score = float(risk.overall_risk_score) if risk else 0.0
        cat = risk.risk_category if risk else "LOW"
        action = risk.recommended_action if risk else "APPROVE"

        total_score += score
        if cat == "LOW":
            low_count += 1
        elif cat in ("HIGH", "CRITICAL"):
            high_count += 1

        tx_list.append({
            "transaction_ref": tx.transaction_ref,
            "amount": float(tx.amount),
            "payment_method": tx.payment_method,
            "location_city": tx.location_city,
            "risk_score": score,
            "risk_category": cat,
            "recommended_action": action
        })

    stats = {
        "total": len(tx_list),
        "avg_score": (total_score / max(len(tx_list), 1)),
        "low_count": low_count,
        "high_count": high_count
    }

    pdf_bytes = generate_pdf_risk_report(tx_list, stats)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=transaction_risk_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.pdf"}
    )


@router.get("/export/pdf/{transaction_ref}")
async def export_single_transaction_pdf(
    transaction_ref: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Generates official institutional PDF risk audit report for a specific transaction."""
    q = (
        select(Transaction)
        .options(selectinload(Transaction.risk_assessment))
        .where(Transaction.transaction_ref == transaction_ref)
    )
    if current_user:
        q = q.where(Transaction.user_id == current_user.id)
    else:
        q = q.where(Transaction.user_id.is_(None))
    res = await db.execute(q)
    tx = res.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found or access denied.")

    risk = tx.risk_assessment
    score = float(risk.overall_risk_score) if risk else 0.0
    cat = risk.risk_category if risk else "LOW"
    action = risk.recommended_action if risk else "APPROVE"

    tx_list = [{
        "transaction_ref": tx.transaction_ref,
        "amount": float(tx.amount),
        "payment_method": tx.payment_method,
        "location_city": tx.location_city,
        "risk_score": score,
        "risk_category": cat,
        "recommended_action": action
    }]

    stats = {
        "total": 1,
        "avg_score": score,
        "low_count": 1 if cat == "LOW" else 0,
        "high_count": 1 if cat in ("HIGH", "CRITICAL") else 0
    }

    pdf_bytes = generate_pdf_risk_report(tx_list, stats)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=risk_report_{transaction_ref}.pdf"}
    )
