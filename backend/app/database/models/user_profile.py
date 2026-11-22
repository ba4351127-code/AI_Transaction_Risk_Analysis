import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Numeric, Integer, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_identifier: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String(32), default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    baseline: Mapped["UserBaseline"] = relationship("UserBaseline", back_populates="user", uselist=False, cascade="all, delete-orphan")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="user")


class UserBaseline(Base):
    __tablename__ = "user_baselines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    avg_amount_30d: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    std_amount_30d: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    max_amount_recorded: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    total_transactions_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Behavioral patterns stored as JSON
    common_locations: Mapped[dict] = mapped_column(JSON, default=list)       # List of {"city": str, "lat": float, "lon": float}
    known_device_hashes: Mapped[dict] = mapped_column(JSON, default=list)    # List of device_id strings
    usual_hour_distribution: Mapped[dict] = mapped_column(JSON, default=list)# List of active hours e.g. [9, 10, 11, ...]
    
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="baseline")
