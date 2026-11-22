import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Numeric, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_ref: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    batch_job_id: Mapped[str] = mapped_column(String(36), ForeignKey("batch_jobs.id", ondelete="CASCADE"), nullable=True, index=True)
    
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    payment_method: Mapped[str] = mapped_column(String(32), default="credit_card")
    card_network: Mapped[str] = mapped_column(String(32), nullable=True)
    merchant_category: Mapped[str] = mapped_column(String(64), default="general")
    
    location_city: Mapped[str] = mapped_column(String(128), default="Unknown")
    location_country: Mapped[str] = mapped_column(String(64), default="US")
    latitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=True)
    
    device_id: Mapped[str] = mapped_column(String(128), default="dev_unknown")
    ip_address: Mapped[str] = mapped_column(String(45), default="127.0.0.1")
    is_device_familiar: Mapped[bool] = mapped_column(Boolean, default=True)
    
    transaction_timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="transactions")
    batch_job: Mapped["BatchJob"] = relationship("BatchJob", back_populates="transactions")
    risk_assessment: Mapped["RiskAssessment"] = relationship("RiskAssessment", back_populates="transaction", uselist=False, cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="transaction")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id: Mapped[str] = mapped_column(String(36), ForeignKey("transactions.id", ondelete="CASCADE"), unique=True, nullable=False)

    overall_risk_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, index=True)  # 0.0 - 100.0
    risk_category: Mapped[str] = mapped_column(String(16), nullable=False, index=True)            # LOW, MEDIUM, HIGH, CRITICAL
    recommended_action: Mapped[str] = mapped_column(String(16), nullable=False)                  # APPROVE, REVIEW, BLOCK

    xgb_fraud_probability: Mapped[float] = mapped_column(Numeric(5, 4), default=0.0)
    iforest_anomaly_score: Mapped[float] = mapped_column(Numeric(5, 4), default=0.0)
    rule_penalty_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)
    behavioral_deviation_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)

    top_shap_features: Mapped[dict] = mapped_column(JSON, default=list)
    simple_explanation: Mapped[str] = mapped_column(String(1000), default="")
    technical_summary: Mapped[str] = mapped_column(String(2000), default="")
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 2), default=95.0)

    evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="risk_assessment")
