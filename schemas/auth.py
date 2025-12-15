from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    dob: Optional[date] = None
    gender: Optional[str] = Field(default=None)


class LoginRequest(BaseModel):
    username_or_email: str
    password: str

class UserOut(BaseModel):
    id: str
    username: str
    email: EmailStr
    gender: Optional[str] = None
    dob: Optional[date] = None
    userType: str
    isActive: bool
    isApproved: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional[UserOut] = None


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class SocialLoginRequest(BaseModel):
    provider: str  # "google" | "facebook"
    id_token: str | None = None  # google
    access_token: str | None = None  # facebook

class ChangePasswordRequest(BaseModel):
    """Schema for changing password (requires current password verification)"""
    current_password: str = Field(
        ...,
        min_length=1,
        description="Current password"
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="New password (minimum 8 characters)"
    )