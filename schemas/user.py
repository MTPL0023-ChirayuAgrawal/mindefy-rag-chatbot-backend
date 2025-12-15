from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: str
    username: str
    email: EmailStr
    gender: Optional[str] = None
    dob: Optional[date] = None
    userType: str
    isActive: bool
    isApproved: str
    createdAt: datetime
    updatedAt: datetime


class AdminUpdateRequestStatus(BaseModel):
    isApproved: str


