import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base


class BatchJob(Base):
    __tablename__ = "batch_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    total_records: Mapped[int] = mapped_column(Integer, default=0)
    processed_records: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    avg_risk_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)
    
    flagged_low_count: Mapped[int] = mapped_column(Integer, default=0)
    flagged_medium_count: Mapped[int] = mapped_column(Integer, default=0)
    flagged_high_count: Mapped[int] = mapped_column(Integer, default=0)
    flagged_critical_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="batch_job")
