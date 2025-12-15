from typing import List
from fastapi import APIRouter, Depends, HTTPException

from dependencies.auth import require_admin
from schemas.user import UserOut, AdminUpdateRequestStatus
from services import users as user_service
from services.email import email_service


router = APIRouter()


@router.get("/users", response_model=List[UserOut])
async def list_users(_: dict = Depends(require_admin)):
    docs = await user_service.list_users()
    return [
        {
            "id": str(doc["_id"]),
            "username": doc["username"],
            "email": doc["email"],
            "gender": doc.get("gender"),
            "dob": doc.get("dob"),
            "userType": doc.get("userType", "user"),
            "isActive": doc.get("isActive", True),
            "isApproved": doc.get("isApproved", "pending"),
            "createdAt": doc.get("createdAt"),
            "updatedAt": doc.get("updatedAt"),
        }
        for doc in docs
    ]


@router.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: str, _: dict = Depends(require_admin)):
    doc = await user_service.get_user_by_id(user_id)
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": str(doc["_id"]),
        "username": doc["username"],
        "email": doc["email"],
        "gender": doc.get("gender"),
        "dob": doc.get("dob"),
        "userType": doc.get("userType", "user"),
        "isActive": doc.get("isActive", True),
        "isApproved": doc.get("isApproved", "pending"),
        "createdAt": doc.get("createdAt"),
        "updatedAt": doc.get("updatedAt"),
    }


@router.post("/users/{user_id}/approval", response_model=UserOut)
async def update_approval(user_id: str, payload: AdminUpdateRequestStatus, _: dict = Depends(require_admin)):
    # Get user data before updating for notifications
    user_before = await user_service.get_user_by_id(user_id)
    if not user_before:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if approval status is actually changing
    current_approved = user_before.get("isApproved", "pending")
    if current_approved == payload.isApproved:
        # No change needed, return current data
        return {
            "id": str(user_before["_id"]),
            "username": user_before["username"],
            "email": user_before["email"],
            "gender": user_before.get("gender"),
            "dob": user_before.get("dob"),
            "userType": user_before.get("userType", "user"),
            "isActive": user_before.get("isActive", True),
            "isApproved": user_before.get("isApproved", "pending"),
            "createdAt": user_before.get("createdAt"),
            "updatedAt": user_before.get("updatedAt"),
        }
    
    ok = await user_service.set_approval(user_id, payload.isApproved)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    
    doc = await user_service.get_user_by_id(user_id)
    
    # Send notification to user about approval/rejection
    try:
        if payload.isApproved.strip().lower() == "approved":
            # Send approval notification
            await email_service.send_approval_notification(doc, True)
            # Send welcome email
            await email_service.send_welcome_email(doc)
        else:
            # Send rejection notification
            await email_service.send_approval_notification(doc, False)
    except Exception as e:
        print(f"Failed to send approval notification: {e}")
    
    return {
        "id": str(doc["_id"]),
        "username": doc["username"],
        "email": doc["email"],
        "gender": doc.get("gender"),
        "dob": doc.get("dob"),
        "userType": doc.get("userType", "user"),
        "isActive": doc.get("isActive", True),
        "isApproved": doc.get("isApproved", "pending"),
        "createdAt": doc.get("createdAt"),
        "updatedAt": doc.get("updatedAt"),
    }


