from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from app.db.mongo import get_db
from app.utils.jwt import get_current_user
from app.utils.jd_parser import JDParser

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# Initialize JD Parser
jd_parser = JDParser()


# ===== Pydantic Models =====

class JobCreate(BaseModel):
    # Mandatory Fields (Always Required)
    title: str = Field(..., min_length=3, max_length=200)
    company: str = Field(..., min_length=2, max_length=200)
    numberOfOpenings: int = Field(default=1, ge=1)
    jobType: str = Field(..., pattern="^(Full-time|Part-time|Contract|Internship|Temporary)$")
    workplaceType: str = Field(..., pattern="^(On-site|Remote|Hybrid)$")
    location: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=50)
    
    # Semi-Optional Fields (Can be auto-parsed from description if not provided)
    requiredSkills: Optional[List[str]] = Field(default=None)
    minExperience: Optional[int] = Field(default=None, ge=0, le=50)
    maxExperience: Optional[int] = Field(default=None, ge=0, le=50)
    educationLevel: Optional[str] = Field(default=None, min_length=2)
    
    # Optional Fields
    salaryMin: Optional[int] = Field(None, ge=0)
    salaryMax: Optional[int] = Field(None, ge=0)
    currency: Optional[str] = Field(default="INR", pattern="^(INR|USD|EUR|GBP)$")
    preferredSkills: Optional[List[str]] = Field(default=[])
    applicationDeadline: Optional[str] = None  # ISO date string
    jobLevel: Optional[str] = Field(None, pattern="^(Entry Level|Mid-Senior Level|Senior Level|Lead/Manager|Executive)$")
    department: Optional[str] = Field(None, max_length=100)


class JobResponse(BaseModel):
    jobId: str
    recruiterId: str
    title: str
    company: str
    location: str
    jobType: str
    workplaceType: str
    status: str
    createdAt: str


class JDParseRequest(BaseModel):
    description: str = Field(..., min_length=50)


# ===== Endpoints =====

@router.post("/parse-jd")
def parse_job_description(
    request: JDParseRequest
):
    """
    Public helper endpoint to parse a job description.
    No auth required - this is just a preview/analysis tool.
    Returns extracted fields that can be used to pre-fill the job creation form.
    
    **Scope: Only extracts fields NOT provided by the form**
    
    Extracts:
    - requiredSkills: Technical skills mentioned
    - minExperience: Minimum years of experience  
    - educationLevel: Degree requirement (Bachelor, Master, PhD, etc.)
    - optionalSkills: Nice-to-have skills
    
    Does NOT extract (form already provides):
    - Location (recruiter enters in form)
    - Job Type (recruiter selects from dropdown)
    - Work Mode (recruiter selects from dropdown)
    - Salary (recruiter enters in form)
    """
    try:
        # Parse the job description
        parsed_data = jd_parser.parse(request.description)
        
        return {
            "success": True,
            "message": "Job description parsed successfully",
            "parsedData": parsed_data,
            "suggestions": {
                "requiredSkills": parsed_data.get("requiredSkills", []),
                "minExperience": parsed_data.get("minExperience", 0),
                "educationLevel": parsed_data.get("educationLevel"),
                "preferredSkills": parsed_data.get("optionalSkills", [])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing JD: {str(e)}")


@router.post("/create")
def create_job(
    job_data: JobCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new job posting (RECRUITER only)
    
    Hybrid Approach:
    - If manual fields (requiredSkills, minExperience, educationLevel) are provided, use them
    - If manual fields are missing, auto-parse from description
    - Manual input always takes priority over AI-parsed data
    """
    # 🔒 Allow only RECRUITERs
    if current_user["role"] != "RECRUITER":
        raise HTTPException(
            status_code=403,
            detail="Only RECRUITERs can create job postings"
        )

    db = get_db()
    
    # Use form data directly - recruiter's input is authoritative after AI pre-fill
    required_skills = job_data.requiredSkills or []
    min_experience = job_data.minExperience if job_data.minExperience is not None else 0
    education_level = job_data.educationLevel or ""
    preferred_skills = job_data.preferredSkills or []
    
    # Calculate maxExperience if only minExperience is provided
    max_experience = job_data.maxExperience if job_data.maxExperience is not None else (min_experience + 5 if min_experience else 5)

    # Validate experience range
    if max_experience < min_experience:
        raise HTTPException(
            status_code=400,
            detail="maxExperience must be greater than or equal to minExperience"
        )

    # Validate salary range if provided
    if job_data.salaryMin and job_data.salaryMax:
        if job_data.salaryMax < job_data.salaryMin:
            raise HTTPException(
                status_code=400,
                detail="salaryMax must be greater than or equal to salaryMin"
            )

    job_doc = {
        "recruiterId": current_user["_id"],
        
        # Mandatory fields
        "title": job_data.title,
        "company": job_data.company,
        "numberOfOpenings": job_data.numberOfOpenings,
        "jobType": job_data.jobType,
        "workplaceType": job_data.workplaceType,
        "location": job_data.location,
        "description": job_data.description,
        
        # Hybrid fields (manual or auto-parsed)
        "requiredSkills": required_skills,
        "minExperience": min_experience,
        "maxExperience": max_experience,
        "educationLevel": education_level,
        "preferredSkills": preferred_skills,
        
        # Optional fields
        "salaryMin": job_data.salaryMin,
        "salaryMax": job_data.salaryMax,
        "currency": job_data.currency,
        "applicationDeadline": job_data.applicationDeadline,
        "jobLevel": job_data.jobLevel,
        "department": job_data.department,
        
        # Metadata
        "status": "Open",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }

    result = db.jobs.insert_one(job_doc)

    return {
        "message": "Job created successfully",
        "jobId": str(result.inserted_id)
    }


@router.get("/")
def get_all_jobs(
    current_user: dict = Depends(get_current_user)
):
    """Get all OPEN jobs (for browsing and candidate dashboard)"""
    db = get_db()
    
    jobs = list(db.jobs.find({"status": "Open"}).sort("createdAt", -1))
    
    # Convert ObjectId to string and format response
    result = []
    for job in jobs:
        result.append({
            "jobId": str(job["_id"]),
            "recruiterId": str(job.get("recruiterId")) if job.get("recruiterId") else None,
            "title": job.get("title"),
            "company": job.get("company"),
            "location": job.get("location"),
            "jobType": job.get("jobType"),
            "workplaceType": job.get("workplaceType"),
            "description": job.get("description"),
            "requiredSkills": job.get("requiredSkills", []),
            "minExperience": job.get("minExperience"),
            "maxExperience": job.get("maxExperience"),
            "educationLevel": job.get("educationLevel"),
            "salaryMin": job.get("salaryMin"),
            "salaryMax": job.get("salaryMax"),
            "currency": job.get("currency"),
            "preferredSkills": job.get("preferredSkills", []),
            "applicationDeadline": job.get("applicationDeadline"),
            "jobLevel": job.get("jobLevel"),
            "department": job.get("department"),
            "numberOfOpenings": job.get("numberOfOpenings", 1),
            "status": job.get("status"),
            "createdAt": job.get("createdAt").isoformat() if job.get("createdAt") else None,
            "updatedAt": job.get("updatedAt").isoformat() if job.get("updatedAt") else None
        })
    
    return {
        "jobs": result,
        "count": len(result)
    }


@router.get("/my-jobs")
def get_my_jobs(
    current_user: dict = Depends(get_current_user)
):
    """Get all jobs posted by the current RECRUITER"""
    # 🔒 Allow only RECRUITERs
    if current_user["role"] != "RECRUITER":
        raise HTTPException(
            status_code=403,
            detail="Only RECRUITERs can access this endpoint"
        )
    
    try:
        db = get_db()
        
        # Query using string comparison (recruiterId is stored as string)
        # Exclude archived/deleted jobs
        jobs = list(db.jobs.find({
            "recruiterId": current_user["_id"],
            "$or": [
                {"deleted": {"$exists": False}},
                {"deleted": False}
            ]
        }).sort("createdAt", -1))
        
        # Convert ObjectId to string and format response
        result = []
        for job in jobs:
            job_id = str(job["_id"])
            
            # Count applicants for this job
            applicant_count = db.applications.count_documents({"jobId": job_id})
            
            result.append({
                "jobId": job_id,
                "recruiterId": str(job.get("recruiterId")) if job.get("recruiterId") else None,
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location"),
                "jobType": job.get("jobType"),
                "workplaceType": job.get("workplaceType"),
                "description": job.get("description"),
                "requiredSkills": job.get("requiredSkills", []),
                "minExperience": job.get("minExperience"),
                "maxExperience": job.get("maxExperience"),
                "educationLevel": job.get("educationLevel"),
                "salaryMin": job.get("salaryMin"),
                "salaryMax": job.get("salaryMax"),
                "currency": job.get("currency"),
                "preferredSkills": job.get("preferredSkills", []),
                "applicationDeadline": job.get("applicationDeadline"),
                "jobLevel": job.get("jobLevel"),
                "department": job.get("department"),
                "numberOfOpenings": job.get("numberOfOpenings", 1),
                "status": job.get("status"),
                "applicantCount": applicant_count,
                "createdAt": job.get("createdAt").isoformat() if job.get("createdAt") else None,
                "updatedAt": job.get("updatedAt").isoformat() if job.get("updatedAt") else None
            })
        
        return {
            "jobs": result,
            "count": len(result)
        }
    except Exception as e:
        print(f"Error in get_my_jobs: {str(e)}")  # Debug logging
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch jobs: {str(e)}"
        )


@router.get("/archived")
def get_archived_jobs(
    current_user: dict = Depends(get_current_user)
):
    """Get all archived jobs for the current RECRUITER"""
    # 🔒 Allow only RECRUITERs
    if current_user["role"] != "RECRUITER":
        raise HTTPException(
            status_code=403,
            detail="Only RECRUITERs can access this endpoint"
        )
    
    try:
        db = get_db()
        
        # Query for archived jobs only
        jobs = list(db.jobs.find({
            "recruiterId": current_user["_id"],
            "deleted": True
        }).sort("deletedAt", -1))  # Most recently archived first
        
        # Convert ObjectId to string and format response
        result = []
        for job in jobs:
            job_id = str(job["_id"])
            
            # Count applicants for this job
            applicant_count = db.applications.count_documents({"jobId": job_id})
            
            result.append({
                "jobId": job_id,
                "recruiterId": str(job.get("recruiterId")) if job.get("recruiterId") else None,
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location"),
                "jobType": job.get("jobType"),
                "workplaceType": job.get("workplaceType"),
                "description": job.get("description"),
                "requiredSkills": job.get("requiredSkills", []),
                "minExperience": job.get("minExperience"),
                "maxExperience": job.get("maxExperience"),
                "educationLevel": job.get("educationLevel"),
                "salaryMin": job.get("salaryMin"),
                "salaryMax": job.get("salaryMax"),
                "currency": job.get("currency"),
                "preferredSkills": job.get("preferredSkills", []),
                "applicationDeadline": job.get("applicationDeadline"),
                "jobLevel": job.get("jobLevel"),
                "department": job.get("department"),
                "numberOfOpenings": job.get("numberOfOpenings", 1),
                "status": job.get("status"),
                "applicantCount": applicant_count,
                "createdAt": job.get("createdAt").isoformat() if job.get("createdAt") else None,
                "updatedAt": job.get("updatedAt").isoformat() if job.get("updatedAt") else None,
                "deletedAt": job.get("deletedAt").isoformat() if job.get("deletedAt") else None
            })
        
        return {
            "jobs": result,
            "count": len(result)
        }
    except Exception as e:
        print(f"Error in get_archived_jobs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch archived jobs: {str(e)}"
        )


@router.get("/{job_id}")
def get_job_by_id(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get single job details by ID"""
    db = get_db()
    
    # Validate ObjectId format
    if not ObjectId.is_valid(job_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid job ID format"
        )
    
    job = db.jobs.find_one({"_id": ObjectId(job_id)})
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    return {
        "jobId": str(job["_id"]),
        "recruiterId": str(job.get("recruiterId")) if job.get("recruiterId") else None,
        "title": job.get("title"),
        "company": job.get("company"),
        "location": job.get("location"),
        "jobType": job.get("jobType"),
        "workplaceType": job.get("workplaceType"),
        "description": job.get("description"),
        "requiredSkills": job.get("requiredSkills", []),
        "minExperience": job.get("minExperience"),
        "maxExperience": job.get("maxExperience"),
        "educationLevel": job.get("educationLevel"),
        "salaryMin": job.get("salaryMin"),
        "salaryMax": job.get("salaryMax"),
        "currency": job.get("currency"),
        "preferredSkills": job.get("preferredSkills", []),
        "applicationDeadline": job.get("applicationDeadline"),
        "jobLevel": job.get("jobLevel"),
        "department": job.get("department"),
        "numberOfOpenings": job.get("numberOfOpenings", 1),
        "status": job.get("status"),
        "createdAt": job.get("createdAt").isoformat() if job.get("createdAt") else None,
        "updatedAt": job.get("updatedAt").isoformat() if job.get("updatedAt") else None
    }


@router.put("/{job_id}")
def update_job(
    job_id: str,
    job_data: JobCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing job posting (RECRUITER only, own jobs only)"""
    # 🔒 Allow only RECRUITERs
    if current_user["role"] != "RECRUITER":
        raise HTTPException(
            status_code=403,
            detail="Only RECRUITERs can update job postings"
        )
    
    db = get_db()
    
    # Validate ObjectId format
    if not ObjectId.is_valid(job_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid job ID format"
        )
    
    # Check if job exists and belongs to current recruiter
    existing_job = db.jobs.find_one({"_id": ObjectId(job_id)})
    
    if not existing_job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    # Verify ownership
    if str(existing_job.get("recruiterId")) != str(current_user["_id"]):
        raise HTTPException(
            status_code=403,
            detail="You can only update your own job postings"
        )
    
    # 🤖 AUTO-PARSE DESCRIPTION (Hybrid Approach for updates too)
    parsed_data = jd_parser.parse(job_data.description)
    
    # Use manual input if provided, otherwise use parsed data
    required_skills = job_data.requiredSkills if job_data.requiredSkills else parsed_data.get("requiredSkills", [])
    min_experience = job_data.minExperience if job_data.minExperience is not None else parsed_data.get("minExperience", 0)
    max_experience = job_data.maxExperience if job_data.maxExperience is not None else (min_experience + 5 if min_experience else 5)
    education_level = job_data.educationLevel if job_data.educationLevel else parsed_data.get("educationLevel", "Not Specified")
    preferred_skills = job_data.preferredSkills if job_data.preferredSkills else parsed_data.get("optionalSkills", [])
    
    # Validate experience range
    if max_experience < min_experience:
        raise HTTPException(
            status_code=400,
            detail="maxExperience must be greater than or equal to minExperience"
        )
    
    # Validate salary range if provided
    if job_data.salaryMin and job_data.salaryMax:
        if job_data.salaryMax < job_data.salaryMin:
            raise HTTPException(
                status_code=400,
                detail="salaryMax must be greater than or equal to salaryMin"
            )
    
    # Update job document
    update_doc = {
        "title": job_data.title,
        "company": job_data.company,
        "numberOfOpenings": job_data.numberOfOpenings,
        "jobType": job_data.jobType,
        "workplaceType": job_data.workplaceType,
        "location": job_data.location,
        "description": job_data.description,
        "requiredSkills": required_skills,
        "minExperience": min_experience,
        "maxExperience": max_experience,
        "educationLevel": education_level,
        "salaryMin": job_data.salaryMin,
        "salaryMax": job_data.salaryMax,
        "currency": job_data.currency,
        "preferredSkills": preferred_skills,
        "applicationDeadline": job_data.applicationDeadline,
        "jobLevel": job_data.jobLevel,
        "department": job_data.department,
        "parsedData": parsed_data,  # Store updated parsed data
        "updatedAt": datetime.utcnow()
    }
    
    db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": update_doc}
    )
    
    return {
        "message": "Job updated successfully",
        "jobId": job_id
    }


@router.patch("/{job_id}/status")
def toggle_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Toggle job status between OPEN and CLOSED (RECRUITER only, own jobs only)"""
    # 🔒 Allow only RECRUITERs
    if current_user["role"] != "RECRUITER":
        raise HTTPException(
            status_code=403,
            detail="Only RECRUITERs can change job status"
        )
    
    db = get_db()
    
    # Validate ObjectId format
    if not ObjectId.is_valid(job_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid job ID format"
        )
    
    # Check if job exists and belongs to current recruiter
    existing_job = db.jobs.find_one({"_id": ObjectId(job_id)})
    
    if not existing_job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    # Verify ownership
    if str(existing_job.get("recruiterId")) != str(current_user["_id"]):
        raise HTTPException(
            status_code=403,
            detail="You can only update your own job postings"
        )
    
    # Toggle status
    current_status = existing_job.get("status", "Open")
    new_status = "Closed" if current_status == "Open" else "Open"
    
    db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"status": new_status, "updatedAt": datetime.utcnow()}}
    )
    
    return {
        "message": f"Job status changed to {new_status}",
        "jobId": job_id,
        "status": new_status
    }


@router.delete("/{job_id}/archive")
def archive_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Archive (soft delete) a job posting (RECRUITER only, own jobs only)
    
    Rules:
    - Job must be Closed before archiving
    - Cannot archive Open jobs
    - Soft delete: sets deleted=True, preserves data
    - Applications are preserved for candidates
    """
    # 🔒 Allow only RECRUITERs
    if current_user["role"] != "RECRUITER":
        raise HTTPException(
            status_code=403,
            detail="Only RECRUITERs can archive jobs"
        )
    
    db = get_db()
    
    # Validate ObjectId format
    if not ObjectId.is_valid(job_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid job ID format"
        )
    
    # Check if job exists and belongs to current recruiter
    existing_job = db.jobs.find_one({"_id": ObjectId(job_id)})
    
    if not existing_job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    # Verify ownership
    if str(existing_job.get("recruiterId")) != str(current_user["_id"]):
        raise HTTPException(
            status_code=403,
            detail="You can only archive your own job postings"
        )
    
    # Check if job is closed
    if existing_job.get("status") != "Closed":
        raise HTTPException(
            status_code=400,
            detail="Only closed jobs can be archived. Please close the job first."
        )
    
    # Soft delete: mark as deleted
    db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"deleted": True, "deletedAt": datetime.utcnow()}}
    )
    
    return {
        "message": "Job archived successfully",
        "jobId": job_id
    }


@router.patch("/{job_id}/restore")
def restore_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Restore an archived job (RECRUITER only, own jobs only)
    
    Rules:
    - Removes deleted flag
    - Sets status back to Closed
    - Job becomes visible in active jobs
    """
    # 🔒 Allow only RECRUITERs
    if current_user["role"] != "RECRUITER":
        raise HTTPException(
            status_code=403,
            detail="Only RECRUITERs can restore jobs"
        )
    
    db = get_db()
    
    # Validate ObjectId format
    if not ObjectId.is_valid(job_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid job ID format"
        )
    
    # Check if job exists and belongs to current recruiter
    existing_job = db.jobs.find_one({"_id": ObjectId(job_id)})
    
    if not existing_job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    # Verify ownership
    if str(existing_job.get("recruiterId")) != str(current_user["_id"]):
        raise HTTPException(
            status_code=403,
            detail="You can only restore your own job postings"
        )
    
    # Check if job is actually archived
    if not existing_job.get("deleted"):
        raise HTTPException(
            status_code=400,
            detail="Job is not archived"
        )
    
    # Restore: remove deleted flag and deletedAt timestamp
    db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {
            "$set": {"updatedAt": datetime.utcnow()},
            "$unset": {"deleted": "", "deletedAt": ""}
        }
    )
    
    return {
        "message": "Job restored successfully",
        "jobId": job_id
    }
