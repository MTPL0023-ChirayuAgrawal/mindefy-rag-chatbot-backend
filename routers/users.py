from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from dependencies.auth import get_current_user
from schemas.user import UserOut
from schemas.auth import SignupRequest
from services import users as user_service

from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    gender: Optional[str] = None
    dob: Optional[date] = None

router = APIRouter()


@router.get("/profile", response_model=UserOut)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's profile details"""
    return {
        "id": str(current_user["_id"]),
        "username": current_user["username"],
        "email": current_user["email"],
        "gender": current_user.get("gender"),
        "dob": current_user.get("dob"),
        "userType": current_user.get("userType", "user"),
        "isActive": current_user.get("isActive", True),
        "isApproved": current_user.get("isApproved", "pending"),
        "createdAt": current_user.get("createdAt"),
        "updatedAt": current_user.get("updatedAt"),
    }


@router.put("/profile", response_model=UserOut)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update current user's profile details"""
    update_data = {}

    # Username update
    if user_update.username is not None:
        existing_user = await user_service.find_by_email_or_username(user_update.username)
        if existing_user and str(existing_user["_id"]) != str(current_user["_id"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        update_data["username"] = user_update.username

    # Email update
    if user_update.email is not None:
        existing_user = await user_service.find_by_email_or_username(user_update.email)
        if existing_user and str(existing_user["_id"]) != str(current_user["_id"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        update_data["email"] = user_update.email

    # Gender update
    if user_update.gender is not None:
        if user_update.gender not in ["male", "female", "other"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid gender. Must be 'male', 'female', or 'other'"
            )
        update_data["gender"] = user_update.gender

    # DOB update
    if user_update.dob is not None:
         # convert `date` to full datetime (midnight UTC)
        update_data["dob"] = datetime.combine(user_update.dob, datetime.min.time())

    # If nothing to update
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    # Update user in DB
    success = await user_service.update_user(str(current_user["_id"]), update_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )

    # Fetch updated user
    updated_user = await user_service.get_user_by_id(str(current_user["_id"]))
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated user data"
        )

    return {
        "id": str(updated_user["_id"]),
        "username": updated_user.get("username"),
        "email": updated_user.get("email"),
        "gender": updated_user.get("gender"),
        "dob": updated_user.get("dob"),
        "userType": updated_user.get("userType", "user"),
        "isActive": updated_user.get("isActive", True),
        "isApproved": updated_user.get("isApproved", "pending"),
        "createdAt": updated_user.get("createdAt"),
        "updatedAt": updated_user.get("updatedAt"),
    }

@router.get("/{user_id}", response_model=UserOut)
async def get_user_by_id(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get user details by ID (users can only access their own profile unless they're admin)"""
    # Allow users to access their own profile or admins to access any profile
    if str(current_user["_id"]) != user_id and current_user.get("userType") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own profile"
        )
    
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "gender": user.get("gender"),
        "dob": user.get("dob"),
        "userType": user.get("userType", "user"),
        "isActive": user.get("isActive", True),
        "isApproved": user.get("isApproved", "pending"),
        "createdAt": user.get("createdAt"),
        "updatedAt": user.get("updatedAt"),
    }
