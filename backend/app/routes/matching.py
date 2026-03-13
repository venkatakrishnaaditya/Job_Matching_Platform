"""
Matching API Routes
Endpoints for calculating match scores between resumes and jobs
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from bson import ObjectId
from app.db.mongo import get_db
from app.utils.jwt import get_current_user
from app.utils.skill_matcher import SkillMatcher
from app.utils.match_calculator import MatchCalculator

router = APIRouter(prefix="/matching", tags=["Matching"])

# Initialize matchers
skill_matcher = SkillMatcher()
match_calculator = MatchCalculator()


@router.get("/job/{job_id}")
def get_job_match(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate match score between current candidate and a specific job
    
    Returns:
        - Match score (0-100%)
        - Breakdown by component (skills, experience, education)
        - Matching skills and missing skills
    """
    
    # Only candidates can use this endpoint
    if current_user["role"] != "CANDIDATE":
        raise HTTPException(
            status_code=403,
            detail="Only candidates can view job matches"
        )
    
    db = get_db()
    
    # Validate job ID
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job ID")
    
    # Get job
    job = db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get candidate's resume
    resume = db.resumes.find_one(
        {"candidateId": str(current_user["_id"])},
        sort=[("createdAt", -1)]  # Most recent
    )
    
    if not resume:
        raise HTTPException(
            status_code=404,
            detail="No resume found. Please upload your resume first."
        )
    
    # Extract data
    resume_skills = resume.get("skills", [])
    resume_experience_years = resume.get("totalExperienceYears")
    resume_education = resume.get("education", [])
    
    job_required_skills = job.get("requiredSkills", [])
    job_preferred_skills = job.get("preferredSkills", [])
    job_min_experience = job.get("minExperience")
    job_education_level = job.get("educationLevel")
    
    # Calculate component scores
    
    # 1. Skills similarity (TF-IDF + Cosine Similarity)
    skills_similarity = skill_matcher.calculate_similarity(
        resume_skills=resume_skills,
        job_required_skills=job_required_skills,
        job_preferred_skills=job_preferred_skills
    )
    
    # 2. Experience score (numeric comparison)
    experience_score = match_calculator.calculate_experience_score(
        candidate_years=resume_experience_years,
        job_min_years=job_min_experience
    )
    
    # 3. Education score (ordinal comparison)
    candidate_edu_level = match_calculator.extract_education_level(resume_education)
    required_edu_level = match_calculator.EDUCATION_LEVELS.get(job_education_level, 1)
    
    education_score = match_calculator.calculate_education_score(
        candidate_level=candidate_edu_level,
        required_level=required_edu_level
    )
    
    # Calculate final weighted score
    final_result = match_calculator.calculate_final_score(
        skills_similarity=skills_similarity,
        experience_score=experience_score,
        education_score=education_score
    )
    
    # Get matching and missing skills
    all_job_skills = job_required_skills + job_preferred_skills
    matching_skills = skill_matcher.get_matching_skills(resume_skills, all_job_skills)
    missing_skills = skill_matcher.get_missing_skills(resume_skills, job_required_skills)
    
    # Build response
    overall_score = final_result['overall_score']
    
    return {
        "jobId": str(job["_id"]),
        "jobTitle": job.get("title"),
        "company": job.get("company"),
        "overallScore": overall_score,
        "matchLabel": match_calculator.get_match_label(overall_score),
        "matchColor": match_calculator.get_match_color(overall_score),
        "breakdown": final_result['breakdown'],
        "details": {
            "matchingSkills": matching_skills,
            "missingSkills": missing_skills,
            "candidateExperience": resume_experience_years,
            "requiredExperience": job_min_experience,
            "candidateEducation": resume_education[0].get('description') if resume_education else 'Not specified',
            "requiredEducation": job_education_level or 'Not Required'
        }
    }


@router.get("/jobs/ranked")
def get_ranked_jobs(
    current_user: dict = Depends(get_current_user),
    min_score: int = 0
):
    """
    Get all OPEN jobs ranked by match score for current candidate
    
    Query params:
        - min_score: Minimum match score to include (0-100, default 0)
    
    Returns:
        List of jobs with match scores, sorted by score (highest first)
    """
    
    # Only candidates can use this endpoint
    if current_user["role"] != "CANDIDATE":
        raise HTTPException(
            status_code=403,
            detail="Only candidates can view ranked jobs"
        )
    
    db = get_db()
    
    # Get candidate's resume
    resume = db.resumes.find_one(
        {"candidateId": str(current_user["_id"])},
        sort=[("createdAt", -1)]
    )
    
    if not resume:
        raise HTTPException(
            status_code=404,
            detail="No resume found. Please upload your resume first."
        )
    
    # Extract resume data
    resume_skills = resume.get("skills", [])
    resume_experience_years = resume.get("totalExperienceYears")
    resume_education = resume.get("education", [])
    candidate_edu_level = match_calculator.extract_education_level(resume_education)
    
    # Get all OPEN jobs (exclude deleted/archived)
    jobs = list(db.jobs.find({
        "status": "Open",
        "deleted": {"$ne": True}
    }))
    
    if not jobs:
        return {
            "jobs": [],
            "count": 0,
            "message": "No open jobs available"
        }
    
    # Calculate match score for each job
    ranked_jobs = []
    
    for job in jobs:
        job_required_skills = job.get("requiredSkills", [])
        job_preferred_skills = job.get("preferredSkills", [])
        job_min_experience = job.get("minExperience")
        job_education_level = job.get("educationLevel")
        
        # Calculate scores
        skills_similarity = skill_matcher.calculate_similarity(
            resume_skills=resume_skills,
            job_required_skills=job_required_skills,
            job_preferred_skills=job_preferred_skills
        )
        
        experience_score = match_calculator.calculate_experience_score(
            candidate_years=resume_experience_years,
            job_min_years=job_min_experience
        )
        
        required_edu_level = match_calculator.EDUCATION_LEVELS.get(job_education_level, 1)
        education_score = match_calculator.calculate_education_score(
            candidate_level=candidate_edu_level,
            required_level=required_edu_level
        )
        
        # Calculate final score
        final_result = match_calculator.calculate_final_score(
            skills_similarity=skills_similarity,
            experience_score=experience_score,
            education_score=education_score
        )
        
        overall_score = final_result['overall_score']
        
        # Filter by min_score
        if overall_score >= min_score:
            ranked_jobs.append({
                "jobId": str(job["_id"]),
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location"),
                "jobType": job.get("jobType"),
                "workplaceType": job.get("workplaceType"),
                "description": job.get("description", ""),
                "requiredSkills": job.get("requiredSkills", []),
                "salary": f"{job.get('currency', 'INR')} {job.get('salaryMin', 0):,} - {job.get('salaryMax', 0):,}" if job.get('salaryMin') else None,
                "experience": f"{job.get('minExperience', 0)} years" if job.get('minExperience') is not None else None,
                "education": job.get("educationLevel"),
                "status": job.get("status", "Open"),
                "matchScore": overall_score,
                "matchLabel": match_calculator.get_match_label(overall_score),
                "matchColor": match_calculator.get_match_color(overall_score),
                "breakdown": final_result['breakdown'],
                "createdAt": job.get("createdAt").isoformat() if job.get("createdAt") else None
            })
    
    # Sort by match score (highest first)
    ranked_jobs.sort(key=lambda x: x['matchScore'], reverse=True)
    
    return {
        "matches": ranked_jobs,
        "count": len(ranked_jobs),
        "resumeId": str(resume["_id"])
    }


@router.get("/candidates/{job_id}")
def get_ranked_candidates(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    min_score: int = 0
):
    """
    Get all candidates ranked by match score for a specific job
    (RECRUITER only - for viewing applicants)
    
    Query params:
        - min_score: Minimum match score to include (0-100, default 0)
    
    Returns:
        List of candidates with match scores, sorted by score (highest first)
    """
    
    # Only recruiters can use this endpoint
    if current_user["role"] != "RECRUITER":
        raise HTTPException(
            status_code=403,
            detail="Only recruiters can view candidate matches"
        )
    
    db = get_db()
    
    # Validate job ID
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job ID")
    
    # Get job and verify ownership
    job = db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if str(job.get("recruiterId")) != str(current_user["_id"]):
        raise HTTPException(
            status_code=403,
            detail="You can only view candidates for your own jobs"
        )
    
    # Extract job data
    job_required_skills = job.get("requiredSkills", [])
    job_preferred_skills = job.get("preferredSkills", [])
    job_min_experience = job.get("minExperience")
    job_education_level = job.get("educationLevel")
    required_edu_level = match_calculator.EDUCATION_LEVELS.get(job_education_level, 1)
    
    # Get all resumes
    resumes = list(db.resumes.find({}))
    
    if not resumes:
        return {
            "candidates": [],
            "count": 0,
            "message": "No candidates found"
        }
    
    # Calculate match score for each candidate
    ranked_candidates = []
    
    for resume in resumes:
        resume_skills = resume.get("skills", [])
        resume_experience_years = resume.get("totalExperienceYears")
        resume_education = resume.get("education", [])
        candidate_edu_level = match_calculator.extract_education_level(resume_education)
        
        # Calculate scores
        skills_similarity = skill_matcher.calculate_similarity(
            resume_skills=resume_skills,
            job_required_skills=job_required_skills,
            job_preferred_skills=job_preferred_skills
        )
        
        experience_score = match_calculator.calculate_experience_score(
            candidate_years=resume_experience_years,
            job_min_years=job_min_experience
        )
        
        education_score = match_calculator.calculate_education_score(
            candidate_level=candidate_edu_level,
            required_level=required_edu_level
        )
        
        # Calculate final score
        final_result = match_calculator.calculate_final_score(
            skills_similarity=skills_similarity,
            experience_score=experience_score,
            education_score=education_score
        )
        
        overall_score = final_result['overall_score']
        
        # Filter by min_score
        if overall_score >= min_score:
            # Get candidate user info
            user = db.users.find_one({"_id": ObjectId(resume.get("userId"))})
            
            matching_skills = skill_matcher.get_matching_skills(
                resume_skills, 
                job_required_skills + job_preferred_skills
            )
            
            ranked_candidates.append({
                "candidateId": resume.get("userId"),
                "candidateName": resume.get("candidateName") or user.get("name", "Unknown"),
                "email": resume.get("email") or user.get("email"),
                "skills": resume_skills,
                "matchingSkills": matching_skills,
                "experienceYears": resume_experience_years,
                "matchScore": overall_score,
                "matchLabel": match_calculator.get_match_label(overall_score),
                "breakdown": final_result['breakdown'],
                "resumeUrl": resume.get("resumeDownloadUrl")
            })
    
    # Sort by match score (highest first)
    ranked_candidates.sort(key=lambda x: x['matchScore'], reverse=True)
    
    return {
        "jobId": str(job["_id"]),
        "jobTitle": job.get("title"),
        "candidates": ranked_candidates,
        "count": len(ranked_candidates)
    }


@router.get("/skill-recommendations")
async def get_skill_recommendations(
    current_user: dict = Depends(get_current_user)
):
    """
    Get skill recommendations based on job market demand.
    Only recommends skills the candidate truly doesn't have.
    """
    if current_user["role"] != "CANDIDATE":
        raise HTTPException(status_code=403, detail="Only candidates can access this")
    
    try:
        db = get_db()
        
        # Get candidate's current skills from resume
        resume = db.resumes.find_one(
            {"candidateId": str(current_user["_id"])},
            sort=[("createdAt", -1)]  # Most recent resume
        )
        
        # NORMALIZE candidate skills for comparison (lowercase, strip)
        candidate_skills_normalized = set()
        if resume:
            candidate_skills_normalized = {
                skill.lower().strip() 
                for skill in resume.get("skills", [])
            }
        
        # Get all active jobs
        jobs = list(db.jobs.find({"status": "Open"}))
        
        # Count skills across all jobs that candidate doesn't have
        skill_counts = {}
        skill_display_names = {}  # Store original casing for display
        
        for job in jobs:
            for skill in job.get("requiredSkills", []):
                # NORMALIZE job skill for comparison
                skill_normalized = skill.lower().strip()
                
                # Only recommend if candidate truly doesn't have it
                if skill_normalized not in candidate_skills_normalized:
                    # Count and store display name
                    if skill_normalized not in skill_counts:
                        skill_counts[skill_normalized] = 0
                        skill_display_names[skill_normalized] = skill  # Keep original casing
                    skill_counts[skill_normalized] += 1
        
        # Sort by job count and take top 6
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:6]
        
        recommendations = [
            {
                "skill": skill_display_names[skill_norm],  # Use original casing for display
                "jobCount": count
            }
            for skill_norm, count in sorted_skills
        ]
        
        return {"recommendations": recommendations}
    except Exception as e:
        print(f"Error in skill recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate skill recommendations")
