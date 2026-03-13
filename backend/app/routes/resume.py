from fastapi import APIRouter, UploadFile, File, Depends
from datetime import datetime
from app.db.mongo import get_db
from app.utils.cloudinary import upload_resume_to_cloudinary
from app.utils.jwt import get_current_user
from app.utils.resume_parser import ResumeParser

router = APIRouter(prefix="/resumes", tags=["Resumes"])

# Initialize parser
resume_parser = ResumeParser()


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)  
):
    user_id = str(current_user["_id"]) 
    db = get_db()

    # Read file content for parsing
    file_content = await file.read()
    
    # Reset file pointer for Cloudinary upload
    await file.seek(0)

    # Upload to Cloudinary
    upload_result = upload_resume_to_cloudinary(
        file=file.file,
        user_id=user_id,
        original_filename=file.filename
    )
    
    # Parse resume content
    file_ext = upload_result["file_ext"].lower()
    parsed_data = resume_parser.parse(file_content, file_ext)

    # Update download URL with candidate name if available
    download_url = upload_result["download_url"]
    if parsed_data.get("candidateName"):
        candidate_name = parsed_data["candidateName"].replace(" ", "_").replace("-", "_")
        download_filename = f"{candidate_name}_Resume"  # No extension - Cloudinary adds it automatically
        if "/upload/" in upload_result["storage_url"]:
            download_url = upload_result["storage_url"].replace("/upload/", f"/upload/fl_attachment:{download_filename}/")

    # Deactivate old resumes for this candidate (single active resume rule)
    db.resumes.update_many(
        {"candidateId": user_id, "isActive": True},
        {"$set": {"isActive": False}}
    )

    resume_doc = {
        "candidateId": user_id,  # Changed from userId to candidateId for consistency
        "isActive": True,  # Mark as active resume

        # Cloudinary URLs
        "resumeFileUrl": upload_result["storage_url"],
        "resumeDownloadUrl": download_url,  # Use updated download URL with candidate name
        "resumePreviewUrl": upload_result["preview_url"],
        "original_filename": file.filename,
        "cloudinary_public_id": upload_result["public_id"],



        "fileType": upload_result["file_ext"],
        "sourceType": "UPLOADED",
        "resumeStatus": parsed_data.get("parsing_status", "UPLOADED"),

        # Parsed data (Regex + spaCy hybrid)
        "rawText": parsed_data.get("rawText", ""),
        "email": parsed_data.get("email"),
        "phone": parsed_data.get("phone"),
        "skills": parsed_data.get("skills", []),
        "experience": parsed_data.get("experience", []),
        "education": parsed_data.get("education", []),
        "projects": parsed_data.get("projects", []),
        "certifications": parsed_data.get("certifications", []),
        
        # spaCy extracted fields
        "candidateName": parsed_data.get("candidateName"),
        "totalExperienceYears": parsed_data.get("totalExperienceYears"),
        "currentJobTitle": parsed_data.get("currentJobTitle"),

        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }

    db.resumes.insert_one(resume_doc)

    return {
        "message": "Resume uploaded and parsed successfully",
        "previewUrl": upload_result["preview_url"],
        "downloadUrl": download_url,  # Use updated download URL with candidate name
        "resume_url": upload_result["storage_url"],
        "filename": file.filename,
        "parsed": {
            "candidate_name": parsed_data.get("candidateName"),
            "total_experience_years": parsed_data.get("totalExperienceYears"),
            "current_job_title": parsed_data.get("currentJobTitle"),
            "skills_found": len(parsed_data.get("skills", [])),
            "experience_entries": len(parsed_data.get("experience", [])),
            "education_entries": len(parsed_data.get("education", [])),
            "parsing_status": parsed_data.get("parsing_status")
        }
    }


@router.get("/status")
def get_resume_status(current_user: dict = Depends(get_current_user)):
    """Get user's resume status"""
    user_id = str(current_user["_id"])
    db = get_db()
    
    # Find the most recent resume for this user
    resume = db.resumes.find_one(
        {"candidateId": user_id},
        sort=[("createdAt", -1)]  # Most recent first
    )
    
    if not resume:
        return {"message": "No resume found", "resume": None}
    
    return {
        "message": "Resume found",
        "resume": {
            "filename": resume.get("original_filename") or resume.get("resumeFileUrl", "").split("/")[-1] if resume.get("resumeFileUrl") else "resume.pdf",
            "uploaded_at": resume.get("createdAt"),
            "resume_url": resume.get("resumeFileUrl"),
            "download_url": resume.get("resumeDownloadUrl"),
            "preview_url": resume.get("resumePreviewUrl"),
            "status": resume.get("resumeStatus", "UPLOADED"),
            "skills": resume.get("skills", []),
            "experience_count": len(resume.get("experience", [])),
            "education_count": len(resume.get("education", []))
        }
    }


@router.get("/parsed-data")
def get_parsed_resume_data(current_user: dict = Depends(get_current_user)):
    """Get detailed parsed resume data"""
    user_id = str(current_user["_id"])
    db = get_db()
    
    # Find the most recent resume
    resume = db.resumes.find_one(
        {"candidateId": user_id},
        sort=[("createdAt", -1)]
    )
    
    if not resume:
        return {"message": "No resume found", "data": None}
    
    return {
        "message": "Parsed data retrieved",
        "data": {
            "candidateName": resume.get("candidateName"),
            "email": resume.get("email"),
            "phone": resume.get("phone"),
            "currentJobTitle": resume.get("currentJobTitle"),
            "totalExperienceYears": resume.get("totalExperienceYears"),
            "skills": resume.get("skills", []),
            "experience": resume.get("experience", []),
            "education": resume.get("education", []),
            "projects": resume.get("projects", []),
            "rawText": resume.get("rawText", "")[:500] + "..." if len(resume.get("rawText", "")) > 500 else resume.get("rawText", ""),  # First 500 chars
            "parsing_status": resume.get("resumeStatus"),
            "uploaded_at": resume.get("createdAt")
        }
    }


@router.delete("/remove")
def delete_resume(current_user: dict = Depends(get_current_user)):
    """Delete user's resume"""
    user_id = str(current_user["_id"])
    db = get_db()
    
    # Find and delete the most recent resume
    result = db.resumes.delete_many({"candidateId": user_id})
    
    if result.deleted_count == 0:
        return {"message": "No resume found to delete"}
    
    return {
        "message": "Resume deleted successfully",
        "deleted_count": result.deleted_count
    }
