import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id: Mapped[str] = mapped_column(String(36), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)

    severity: Mapped[str] = mapped_column(String(16), default="WARNING")  # WARNING, CRITICAL
    alert_type: Mapped[str] = mapped_column(String(64), nullable=False)   # e.g., VELOCITY_SPIKE, OUTLIER_AMOUNT, IMPOSSIBLE_TRAVEL
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="OPEN", index=True)  # OPEN, ACKNOWLEDGED, RESOLVED, FALSE_POSITIVE
    assigned_analyst: Mapped[str] = mapped_column(String(128), default="Security Ops")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    resolved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="alerts")
