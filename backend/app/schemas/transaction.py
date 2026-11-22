from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, timezone
import uuid

VALID_PAYMENT_METHODS = {"credit_card", "debit_card", "upi", "net_banking", "wire_transfer"}
VALID_CURRENCIES = {"USD", "EUR", "GBP", "INR", "AED", "JPY", "CAD", "AUD", "SGD", "CHF", "CNY"}


class AdvancedTransactionDetails(BaseModel):
    user_identifier: Optional[str] = Field(default=None, description="Unique account or user ID")
    currency: str = Field(default="USD", max_length=8)
    card_network: Optional[str] = Field(default="Visa", description="Visa, Mastercard, Amex, etc.")
    merchant_category: str = Field(default="general", description="grocery, electronics, luxury, etc.")
    latitude: Optional[float] = Field(default=None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(default=None, ge=-180.0, le=180.0)
    device_id: Optional[str] = Field(default=None, description="Hardware or browser fingerprint hash")
    ip_address: Optional[str] = Field(default="127.0.0.1", description="Client IP address")

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("Currency is required.")
        norm = v.strip().upper()
        if norm not in VALID_CURRENCIES:
            raise ValueError(f"Invalid currency code '{v}'. Supported currencies: {', '.join(sorted(VALID_CURRENCIES))}.")
        return norm


class TransactionAnalyzeRequest(BaseModel):
    """
    Dual-mode input schema:
    Everyday users provide the 5 core fields.
    Advanced analysts can provide the nested advanced_details object.
    """
    amount: float = Field(..., description="Transaction amount in major currency units (e.g. 150.00)")
    currency: Optional[str] = Field(default="USD", description="Currency code (e.g. USD, EUR, INR)")
    payment_method: str = Field(default="credit_card", description="credit_card, debit_card, upi, wire_transfer")
    location_city: str = Field(default="Mumbai", description="City where the transaction is initiated")
    is_device_familiar: bool = Field(default=True, description="Whether this device has been used by this account before")
    transaction_timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), description="ISO timestamp")
    
    # Optional advanced details for analysts / full context
    advanced_details: Optional[AdvancedTransactionDetails] = None
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Transaction amount must be strictly greater than 0.")
        if v > 100_000_000:
            raise ValueError("Transaction amount exceeds maximum allowable transaction ceiling ($100M).")
        return round(v, 2)

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("Payment method is required.")
        norm = v.strip().lower()
        if norm not in VALID_PAYMENT_METHODS:
            raise ValueError(f"Invalid payment method '{v}'. Supported payment methods: {', '.join(sorted(VALID_PAYMENT_METHODS))}.")
        return norm

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: Optional[str]) -> str:
        if v is None:
            return "USD"
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Currency cannot be empty.")
        norm = v.strip().upper()
        if norm not in VALID_CURRENCIES:
            raise ValueError(f"Invalid currency code '{v}'. Supported currencies: {', '.join(sorted(VALID_CURRENCIES))}.")
        return norm

    @field_validator("location_city")
    @classmethod
    def validate_location_city(cls, v: str) -> str:
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("Transaction city cannot be empty.")
        return v.strip()


class TransactionHistoryFilter(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    risk_category: Optional[str] = None
    min_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    max_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    search_query: Optional[str] = None
