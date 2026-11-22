from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List

from backend.app.database.session import get_db
from backend.app.database.models.alert import Alert
from backend.app.database.models.transaction import Transaction
from backend.app.database.models.user_profile import User
from backend.app.core.auth import get_optional_current_user

router = APIRouter()


class AlertStatusUpdate(BaseModel):
    status: str = Field(..., description="OPEN, ACKNOWLEDGED, RESOLVED, FALSE_POSITIVE")
    analyst_notes: Optional[str] = Field(default=None)


@router.get("/feed", response_model=List[dict])
async def get_alerts_feed(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Returns security incidents sorted by timestamp descending.
    When authenticated, strictly filters alerts to transactions belonging to the current user.
    """
    try:
        query = (
            select(Alert)
            .options(selectinload(Alert.transaction))
            .order_by(desc(Alert.created_at))
        )

        # Enforce user isolation: Authenticated users only see alerts for their transactions
        if current_user:
            query = query.join(Alert.transaction).where(Transaction.user_id == current_user.id)
        else:
            query = query.join(Alert.transaction).where(Transaction.user_id.is_(None))

        if status_filter and status_filter.upper() != "ALL":
            query = query.where(Alert.status == status_filter.upper())

        result = await db.execute(query.limit(limit))
        alerts = result.scalars().all()

        feed = []
        for a in alerts:
            tx = a.transaction
            created_str = (
                a.created_at.isoformat()
                if hasattr(a.created_at, "isoformat")
                else str(a.created_at)
            )
            resolved_str = (
                a.resolved_at.isoformat()
                if a.resolved_at and hasattr(a.resolved_at, "isoformat")
                else (str(a.resolved_at) if a.resolved_at else None)
            )
            feed.append({
                "id": a.id,
                "transaction_id": a.transaction_id,
                "transaction_ref": tx.transaction_ref if tx else "N/A",
                "amount": float(tx.amount) if tx else 0.0,
                "severity": a.severity,
                "alert_type": a.alert_type,
                "message": a.message,
                "status": a.status,
                "assigned_analyst": a.assigned_analyst,
                "created_at": created_str,
                "resolved_at": resolved_str
            })

        return feed
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to retrieve security alerts: {str(e)}"
        )


@router.patch("/{alert_id}/status", response_model=dict)
async def update_alert_status(
    alert_id: str,
    payload: AlertStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Updates security alert status (e.g., mark as RESOLVED or FALSE_POSITIVE)."""
    q = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = q.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")

    alert.status = payload.status.upper()
    if alert.status in ("RESOLVED", "FALSE_POSITIVE"):
        alert.resolved_at = datetime.now(timezone.utc)

    await db.commit()
    return {
        "success": True,
        "alert_id": alert.id,
        "new_status": alert.status,
        "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
    }
