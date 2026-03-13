from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
from typing import Optional
import secrets
from app.db.mongo import get_db
from app.models.user import UserCreate
from app.utils.jwt import create_access_token
from app.utils.email_service import email_service

router = APIRouter(prefix="/auth", tags=["Auth"])


# ---------- REQUEST MODELS ----------
class LoginRequest(BaseModel):
    email: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# ---------- PASSWORD HELPERS ----------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_reset_token() -> str:
    """Generate a secure random token for password reset"""
    return secrets.token_urlsafe(32)


# ---------- REGISTER ----------
@router.post("/register")
def register_user(user: UserCreate):
    db = get_db()

    if db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_dict = {
        "name": user.name,
        "email": user.email,
        "password": hash_password(user.password),
        "role": user.role,
        "company": user.company if user.role == "RECRUITER" else None,
        "isActive": True,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }

    db.users.insert_one(user_dict)
    return {"message": "User registered successfully"}


# ---------- LOGIN + JWT ----------
@router.post("/login")
def login_user(credentials: LoginRequest):
    db = get_db()

    user = db.users.find_one({"email": credentials.email})

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(
        data={
            "sub": str(user["_id"]),
            "email": user["email"],
            "role": user["role"]
        }
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }


# ---------- FORGOT PASSWORD ----------
@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest):
    """
    Initiate password reset process.
    Generates a secure token and sends reset email.
    """
    db = get_db()
    
    # Find user by email
    user = db.users.find_one({"email": request.email.lower()})
    
    # Always return success message to prevent email enumeration
    success_message = {
        "message": "If an account with that email exists, we've sent password reset instructions."
    }
    
    if not user:
        # Don't reveal that email doesn't exist
        return success_message
    
    # Generate secure token
    reset_token = generate_reset_token()
    token_expiry = datetime.utcnow() + timedelta(hours=1)
    
    # Store token in database
    db.password_resets.delete_many({"email": request.email.lower()})  # Remove old tokens
    db.password_resets.insert_one({
        "email": request.email.lower(),
        "token": reset_token,
        "expiresAt": token_expiry,
        "createdAt": datetime.utcnow(),
        "used": False
    })
    
    # Send email
    user_name = user.get("name", "User")
    email_sent = email_service.send_password_reset_email(
        to_email=request.email,
        reset_token=reset_token,
        user_name=user_name
    )
    
    if not email_sent:
        # Log error but still return success for security
        print(f"Warning: Failed to send reset email to {request.email}")
    
    return success_message


# ---------- RESET PASSWORD ----------
@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest):
    """
    Reset password using token from email.
    Validates token and updates password.
    """
    db = get_db()
    
    # Find valid token
    reset_record = db.password_resets.find_one({
        "token": request.token,
        "used": False,
        "expiresAt": {"$gt": datetime.utcnow()}
    })
    
    if not reset_record:
        raise HTTPException(
            status_code=400, 
            detail="Invalid or expired reset token. Please request a new password reset."
        )
    
    # Validate password strength
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters long"
        )
    
    # Update user password
    result = db.users.update_one(
        {"email": reset_record["email"]},
        {
            "$set": {
                "password": hash_password(request.new_password),
                "updatedAt": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update password")
    
    # Mark token as used
    db.password_resets.update_one(
        {"_id": reset_record["_id"]},
        {"$set": {"used": True}}
    )
    
    # Clean up old tokens for this user
    db.password_resets.delete_many({
        "email": reset_record["email"],
        "_id": {"$ne": reset_record["_id"]}
    })
    
    return {"message": "Password has been reset successfully. You can now login with your new password."}


# ---------- VERIFY RESET TOKEN ----------
@router.get("/verify-reset-token")
def verify_reset_token(token: str):
    """
    Verify if a reset token is valid (used by frontend before showing reset form).
    """
    db = get_db()
    
    reset_record = db.password_resets.find_one({
        "token": token,
        "used": False,
        "expiresAt": {"$gt": datetime.utcnow()}
    })
    
    if not reset_record:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token"
        )
    
    return {"valid": True, "email": reset_record["email"]}

