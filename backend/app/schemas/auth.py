from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


class UserSignupRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Secure account password (minimum 8 characters)")
    full_name: Optional[str] = Field(None, max_length=128, description="User full name")

    @field_validator("password")
    @classmethod
    def validate_password_byte_length(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password cannot exceed 72 bytes when UTF-8 encoded.")
        return v


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Account password")

    @field_validator("password")
    @classmethod
    def validate_password_byte_length(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password cannot exceed 72 bytes when UTF-8 encoded.")
        return v


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_identifier: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: str = "user"
    created_at: Optional[datetime] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfileResponse
