from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string"}


class ResumeSnapshot(BaseModel):
    """Snapshot of resume data at time of application"""
    skills: List[str] = Field(..., description="List of skills from resume")
    exp: float = Field(..., description="Years of experience")
    edu: str = Field(..., description="Education level (e.g., 'Bachelor', 'Master')")


class ResumeFiles(BaseModel):
    """Resume file URLs from Cloudinary"""
    resumeFileUrl: Optional[str] = Field(None, description="Direct URL to resume file")
    resumeDownloadUrl: Optional[str] = Field(None, description="URL for downloading resume")
    resumePreviewUrl: Optional[str] = Field(None, description="URL for previewing resume")


class CandidateDetails(BaseModel):
    """Candidate basic information"""
    name: str = Field(..., description="Candidate name")
    email: str = Field(..., description="Candidate email")


class SnapshotBreakdown(BaseModel):
    """Breakdown of match score components"""
    skillsScore: float = Field(..., ge=0, le=100, description="Skills match score (0-100)")
    experienceScore: float = Field(..., ge=0, le=100, description="Experience match score (0-100)")
    educationScore: float = Field(..., ge=0, le=100, description="Education match score (0-100)")


class ApplicationBase(BaseModel):
    """Base application fields"""
    candidateId: str = Field(..., description="ID of the candidate")
    jobId: str = Field(..., description="ID of the job")
    resumeSnapshot: ResumeSnapshot
    resumeFiles: ResumeFiles = Field(default_factory=lambda: ResumeFiles(), description="Resume file URLs")
    snapshotMatchScore: float = Field(..., ge=0, le=100, description="Overall match score at application time")
    snapshotBreakdown: SnapshotBreakdown
    status: str = Field(default="Applied", description="Application status")
    appliedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True


class ApplicationCreate(BaseModel):
    """Schema for creating a new application"""
    jobId: str = Field(..., description="ID of the job to apply for")

    class Config:
        json_schema_extra = {
            "example": {
                "jobId": "507f1f77bcf86cd799439011"
            }
        }


class ApplicationResponse(ApplicationBase):
    """Schema for application responses"""
    id: str = Field(alias="_id")
    candidateDetails: Optional[CandidateDetails] = Field(None, description="Candidate name and email")

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "candidateId": "507f1f77bcf86cd799439012",
                "jobId": "507f1f77bcf86cd799439013",
                "resumeSnapshot": {
                    "skills": ["Python", "Django", "REST API"],
                    "exp": 2,
                    "edu": "Bachelor"
                },
                "snapshotMatchScore": 87.5,
                "snapshotBreakdown": {
                    "skillsScore": 90.0,
                    "experienceScore": 85.0,
                    "educationScore": 80.0
                },
                "status": "Applied",
                "appliedAt": "2026-01-16T10:30:00Z"
            }
        }


class ApplicationStatusUpdate(BaseModel):
    """Schema for updating application status"""
    status: str = Field(..., description="New status (Reviewed, Shortlisted, Rejected)")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "Reviewed"
            }
        }
