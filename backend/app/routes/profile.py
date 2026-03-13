from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from app.db.mongo import get_db
from app.utils.jwt import get_current_user
from app.utils.cloudinary import upload_to_cloudinary

router = APIRouter(prefix="/users", tags=["Profile"])


# ===== Pydantic Models =====

class CandidateProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    bio: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=100)
    
    # Professional details
    skills: Optional[List[str]] = None
    experienceLevel: Optional[str] = Field(None, pattern="^(Fresher|0-1 years|1-3 years|3-5 years|5-10 years|10+ years)$")
    currentCompany: Optional[str] = Field(None, max_length=200)
    currentRole: Optional[str] = Field(None, max_length=200)
    linkedIn: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    
    # Education (stored as list of objects)
    education: Optional[List[dict]] = None  # {degree, institution, year, field}
    
    # Experience (stored as list of objects)
    experience: Optional[List[dict]] = None  # {company, role, from, to, description}


class RecruiterProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    
    # Company details
    companyName: Optional[str] = Field(None, max_length=200)
    companyIndustry: Optional[str] = Field(None, max_length=100)
    companySize: Optional[str] = Field(None, pattern="^(1-10|10-50|50-200|200-500|500-1000|1000\\+)$")
    companyWebsite: Optional[str] = None
    companyLinkedIn: Optional[str] = None
    companyDescription: Optional[str] = Field(None, max_length=1000)


# ===== Endpoints =====

@router.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's profile"""
    
    # Remove sensitive data
    profile = {
        "userId": str(current_user["_id"]),
        "email": current_user.get("email"),
        "name": current_user.get("name"),
        "role": current_user.get("role"),
        "phone": current_user.get("phone"),
        "profilePhoto": current_user.get("profilePhoto"),
        "createdAt": current_user.get("createdAt").isoformat() if current_user.get("createdAt") else None,
    }
    
    # Add role-specific fields
    if current_user["role"] == "CANDIDATE":
        profile.update({
            "bio": current_user.get("bio"),
            "location": current_user.get("location"),
            "skills": current_user.get("skills", []),
            "experienceLevel": current_user.get("experienceLevel"),
            "currentCompany": current_user.get("currentCompany"),
            "currentRole": current_user.get("currentRole"),
            "linkedIn": current_user.get("linkedIn"),
            "github": current_user.get("github"),
            "portfolio": current_user.get("portfolio"),
            "education": current_user.get("education", []),
            "experience": current_user.get("experience", []),
        })
    elif current_user["role"] == "RECRUITER":
        profile.update({
            "companyName": current_user.get("companyName"),
            "companyIndustry": current_user.get("companyIndustry"),
            "companySize": current_user.get("companySize"),
            "companyWebsite": current_user.get("companyWebsite"),
            "companyLinkedIn": current_user.get("companyLinkedIn"),
            "companyDescription": current_user.get("companyDescription"),
            "companyLogo": current_user.get("companyLogo"),
        })
    
    return profile


@router.put("/profile")
def update_profile(
    profile_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update current user's profile"""
    
    db = get_db()
    user_id = current_user["_id"]
    
    # Validate based on role
    if current_user["role"] == "CANDIDATE":
        update_data = CandidateProfileUpdate(**profile_data)
    elif current_user["role"] == "RECRUITER":
        update_data = RecruiterProfileUpdate(**profile_data)
    else:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Build update document (only include non-None fields)
    update_doc = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if not update_doc:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Add updated timestamp
    update_doc["updatedAt"] = datetime.utcnow()
    
    # Update in database
    result = db.users.update_one(
        {"_id": user_id},
        {"$set": update_doc}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "message": "Profile updated successfully",
        "updatedFields": list(update_doc.keys())
    }


@router.post("/upload-photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload profile photo to Cloudinary"""
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG, PNG, and WebP images are allowed"
        )
    
    try:
        # Upload to Cloudinary
        file_content = await file.read()
        cloudinary_url = upload_to_cloudinary(
            file_content,
            folder="profile_photos",
            resource_type="image"
        )
        
        # Update user document
        db = get_db()
        db.users.update_one(
            {"_id": current_user["_id"]},
            {"$set": {
                "profilePhoto": cloudinary_url,
                "updatedAt": datetime.utcnow()
            }}
        )
        
        return {
            "message": "Profile photo uploaded successfully",
            "photoUrl": cloudinary_url
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Photo upload failed: {str(e)}"
        )


@router.delete("/remove-photo")
def remove_profile_photo(current_user: dict = Depends(get_current_user)):
    """Remove profile photo"""
    try:
        db = get_db()
        
        # Check if user has a photo
        user = db.users.find_one({"_id": current_user["_id"]})
        if not user or not user.get("profilePhoto"):
            raise HTTPException(
                status_code=404,
                detail="No profile photo found"
            )
        
        # Remove photo from database (not deleting from Cloudinary to save API calls)
        db.users.update_one(
            {"_id": current_user["_id"]},
            {"$unset": {"profilePhoto": ""}, "$set": {"updatedAt": datetime.utcnow()}}
        )
        
        return {"message": "Profile photo removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to remove photo: {str(e)}"
        )


@router.post("/upload-company-logo")
async def upload_company_logo(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload company logo (RECRUITER only)"""
    
    if current_user["role"] != "RECRUITER":
        raise HTTPException(
            status_code=403,
            detail="Only recruiters can upload company logos"
        )
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG, PNG, and WebP images are allowed"
        )
    
    try:
        # Upload to Cloudinary
        file_content = await file.read()
        cloudinary_url = upload_to_cloudinary(
            file_content,
            folder="company_logos",
            resource_type="image"
        )
        
        # Update user document
        db = get_db()
        db.users.update_one(
            {"_id": current_user["_id"]},
            {"$set": {
                "companyLogo": cloudinary_url,
                "updatedAt": datetime.utcnow()
            }}
        )
        
        return {
            "message": "Company logo uploaded successfully",
            "logoUrl": cloudinary_url
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Logo upload failed: {str(e)}"
        )
