from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    gender: Optional[Literal["male", "female", "other"]] = None
    dob: Optional[datetime] = None
    userType: Literal["user", "admin"] = "user"
    isActive: bool = True


class UserInDB(UserBase):
    id: str
    hashed_password: Optional[str] = None
    isApproved: str
    createdAt: datetime
    updatedAt: datetime
    provider: Literal["credentials", "google", "facebook"] = "credentials"
    providerId: Optional[str] = None


class PublicUser(BaseModel):
    id: str
    username: str
    email: EmailStr
    gender: Optional[str] = None
    dob: Optional[datetime] = None
    userType: str
    isActive: bool
    isApproved: str
    createdAt: datetime
    updatedAt: datetime


