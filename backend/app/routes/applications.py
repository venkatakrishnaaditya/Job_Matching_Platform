from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from bson import ObjectId
from datetime import datetime

from app.models.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationStatusUpdate,
    ResumeSnapshot,
    ResumeFiles,
    SnapshotBreakdown
)
from app.utils.jwt import get_current_user
from app.db.mongo import get_db
from app.utils.match_calculator import MatchCalculator
from app.utils.application_validator import (
    is_valid_status_transition,
    can_candidate_withdraw,
    is_terminal_status
)

router = APIRouter()


@router.post("/apply", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply_to_job(
    application_data: ApplicationCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Apply to a job (Candidate only)
    
    Business Rules:
    - One application per job per candidate
    - Job must exist and be Open
    - Candidate must have active resume
    - Stores resume snapshot + match score snapshot
    """
    # Verify user is a candidate
    if current_user.get("role") != "CANDIDATE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can apply to jobs"
        )
    
    db = get_db()
    candidate_id = str(current_user["_id"])  # Convert ObjectId to string
    job_id = application_data.jobId
    
    # Validate ObjectId format
    if not ObjectId.is_valid(job_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format"
        )
    
    # Check if job exists and is Open
    job = db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.get("status") != "Open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot apply to a closed job"
        )
    
    # Check for duplicate application
    existing_application = db.applications.find_one({
        "candidateId": candidate_id,
        "jobId": job_id
    })
    
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already applied to this job"
        )
    
    # Get candidate's active resume
    resume = db.resumes.find_one({
        "candidateId": candidate_id,
        "isActive": True
    })
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a resume before applying"
        )
    
    # Extract data directly from resume document (not nested in parsedData)
    # Get education - stored as array of dicts, extract description from first entry
    education_list = resume.get("education", [])
    if education_list and isinstance(education_list, list) and len(education_list) > 0:
        first_edu = education_list[0]
        if isinstance(first_edu, dict):
            education_str = first_edu.get("description", "Not Specified")
        else:
            education_str = str(first_edu)
    else:
        education_str = "Not Specified"
    
    # Get experience years - handle None case
    experience_years = resume.get("totalExperienceYears")
    if experience_years is None:
        experience_years = 0
    
    # Create resume snapshot
    resume_snapshot = ResumeSnapshot(
        skills=resume.get("skills", []),
        exp=experience_years,
        edu=education_str
    )
    
    # Calculate match score using MatchCalculator
    calculator = MatchCalculator()
    
    # Import SkillMatcher for skills calculation
    from app.utils.skill_matcher import SkillMatcher
    skill_matcher = SkillMatcher()
    
    # Get job requirements
    job_parsed = job.get("parsedData", {})
    job_required_skills = job.get("requiredSkills", [])
    job_preferred_skills = job.get("preferredSkills", [])
    job_min_experience = job.get("minExperience", 0)
    job_education = job.get("educationLevel", "")
    
    # Convert education strings to integer levels
    candidate_edu_level = calculator.extract_education_level(resume.get("education", []))
    required_edu_level = calculator.EDUCATION_LEVELS.get(job_education, 1)
    
    # Calculate individual scores
    skills_score = skill_matcher.calculate_similarity(
        resume_snapshot.skills,
        job_required_skills,
        job_preferred_skills
    )
    
    experience_score = calculator.calculate_experience_score(
        resume_snapshot.exp,
        job_min_experience
    )
    
    education_score = calculator.calculate_education_score(
        candidate_edu_level,
        required_edu_level
    )
    
    # Calculate final weighted score
    match_result = calculator.calculate_final_score(
        skills_similarity=skills_score,
        experience_score=experience_score,
        education_score=education_score
    )
    
    # Create snapshot breakdown
    snapshot_breakdown = SnapshotBreakdown(
        skillsScore=match_result["breakdown"]["skills"]["percentage"],
        experienceScore=match_result["breakdown"]["experience"]["percentage"],
        educationScore=match_result["breakdown"]["education"]["percentage"]
    )
    
    # Extract resume file URLs from Cloudinary
    resume_files = ResumeFiles(
        resumeFileUrl=resume.get("resumeFileUrl"),
        resumeDownloadUrl=resume.get("resumeDownloadUrl"),
        resumePreviewUrl=resume.get("resumePreviewUrl")
    )
    
    # Create application document
    application = {
        "candidateId": candidate_id,
        "jobId": job_id,
        "resumeSnapshot": resume_snapshot.model_dump(),
        "resumeFiles": resume_files.model_dump(),
        "snapshotMatchScore": match_result["overall_score"],
        "snapshotBreakdown": snapshot_breakdown.model_dump(),
        "status": "Applied",
        "appliedAt": datetime.utcnow()
    }
    
    # Insert application
    result = db.applications.insert_one(application)
    application["_id"] = str(result.inserted_id)
    
    return ApplicationResponse(**application)


@router.get("/my-applications")
async def get_my_applications(current_user: dict = Depends(get_current_user)):
    """
    Get all applications for logged-in candidate with job details
    
    Returns applications sorted by appliedAt (newest first)
    Includes job title, company, location for display
    """
    # Verify user is a candidate
    if current_user.get("role") != "CANDIDATE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can view their applications"
        )
    
    db = get_db()
    candidate_id = str(current_user["_id"])  # Convert ObjectId to string
    
    # Get all applications for this candidate
    applications = list(db.applications.find(
        {"candidateId": candidate_id}
    ).sort("appliedAt", -1))
    
    # Enrich applications with job details
    enriched_applications = []
    for app in applications:
        # Get job details
        job = db.jobs.find_one({"_id": ObjectId(app["jobId"])})
        
        if not job:
            # Skip if job was deleted
            continue
        
        # Transform to frontend-friendly format
        enriched_app = {
            "application_id": str(app["_id"]),
            "job_id": app["jobId"],
            "job_title": job.get("title", "Unknown Position"),
            "company": job.get("company", "Unknown Company"),
            "job_location": job.get("location", "Not specified"),
            "job_type": job.get("jobType", "Full-time"),
            "status": app.get("status", "Applied"),
            "applied_at": app.get("appliedAt").isoformat() if app.get("appliedAt") else None,
            "match_score": app.get("snapshotMatchScore", 0),
            "breakdown": {
                "skills_score": app.get("snapshotBreakdown", {}).get("skillsScore", 0),
                "experience_score": app.get("snapshotBreakdown", {}).get("experienceScore", 0),
                "education_score": app.get("snapshotBreakdown", {}).get("educationScore", 0)
            }
        }
        
        enriched_applications.append(enriched_app)
    
    return {"applications": enriched_applications}


@router.delete("/{application_id}/withdraw", status_code=status.HTTP_200_OK)
async def withdraw_application(
    application_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Withdraw an application (Candidate only)
    
    Business Rules:
    - Only candidate who owns the application can withdraw
    - Can only withdraw if status = "Applied"
    """
    # Verify user is a candidate
    if current_user.get("role") != "CANDIDATE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can withdraw applications"
        )
    
    db = get_db()
    
    # Validate ObjectId format
    if not ObjectId.is_valid(application_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid application ID format"
        )
    
    candidate_id = str(current_user["_id"])  # Convert ObjectId to string
    
    # Get application
    application = db.applications.find_one({"_id": ObjectId(application_id)})
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Verify ownership
    if application["candidateId"] != candidate_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only withdraw your own applications"
        )
    
    # Check if withdrawal is allowed
    current_status = application["status"]
    
    if not can_candidate_withdraw(current_status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot withdraw application with status '{current_status}'. Only 'Applied' applications can be withdrawn."
        )
    
    # Update status to Withdrawn
    db.applications.update_one(
        {"_id": ObjectId(application_id)},
        {"$set": {"status": "Withdrawn"}}
    )
    
    return {"message": "Application withdrawn successfully"}


@router.get("/job/{job_id}/applicants", response_model=List[ApplicationResponse])
async def get_job_applicants(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all applicants for a job (Recruiter only)
    
    Returns applications sorted by snapshotMatchScore (highest first)
    Includes withdrawn applications (will be grayed out in frontend)
    """
    # Verify user is a recruiter
    if current_user.get("role") != "RECRUITER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can view applicants"
        )
    
    db = get_db()
    
    # Validate ObjectId format
    if not ObjectId.is_valid(job_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format"
        )
    
    # Verify job exists and belongs to recruiter
    job = db.jobs.find_one({"_id": ObjectId(job_id)})
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job["recruiterId"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view applicants for your own jobs"
        )
    
    # Get all applications for this job
    applications = list(db.applications.find(
        {"jobId": job_id}
    ).sort("snapshotMatchScore", -1))  # Highest match score first
    
    # Enrich with candidate details
    for app in applications:
        app["_id"] = str(app["_id"])
        
        # Fetch candidate details from users collection
        candidate = db.users.find_one({"_id": ObjectId(app["candidateId"])})
        if candidate:
            app["candidateDetails"] = {
                "name": candidate.get("name", "Unknown"),
                "email": candidate.get("email", "")
            }
        else:
            app["candidateDetails"] = {
                "name": "Unknown",
                "email": ""
            }
    
    return [ApplicationResponse(**app) for app in applications]


@router.patch("/{application_id}/status", response_model=ApplicationResponse)
async def update_application_status(
    application_id: str,
    status_update: ApplicationStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update application status (Recruiter only)
    
    Business Rules:
    - Only recruiter who owns the job can update status
    - Cannot update Withdrawn applications
    - Must follow valid status transitions
    """
    # Verify user is a recruiter
    if current_user.get("role") != "RECRUITER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can update application status"
        )
    
    db = get_db()
    
    # Validate ObjectId format
    if not ObjectId.is_valid(application_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid application ID format"
        )
    
    # Get application
    application = db.applications.find_one({"_id": ObjectId(application_id)})
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Get associated job
    job = db.jobs.find_one({"_id": ObjectId(application["jobId"])})
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated job not found"
        )
    
    # Verify job ownership
    if job["recruiterId"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update applications for your own jobs"
        )
    
    # Check if application is withdrawn
    current_status = application["status"]
    new_status = status_update.status
    
    if current_status == "Withdrawn":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update status of withdrawn applications"
        )
    
    # Validate status transition
    if not is_valid_status_transition(current_status, new_status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from '{current_status}' to '{new_status}'"
        )
    
    # Update status
    db.applications.update_one(
        {"_id": ObjectId(application_id)},
        {"$set": {"status": new_status}}
    )
    
    # Get updated application
    updated_application = db.applications.find_one({"_id": ObjectId(application_id)})
    updated_application["_id"] = str(updated_application["_id"])
    
    return ApplicationResponse(**updated_application)
