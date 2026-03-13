from pymongo import MongoClient
import json

client = MongoClient('mongodb+srv://venkatakrishnaaditya2003_db_user:5Gu549XOunnxkgR5@cluster0.jefxvin.mongodb.net/ai_resume_matching?appName=Cluster0')
db = client['ai_resume_matching']

# Get most recent resume
resume = db.resumes.find_one({}, sort=[("createdAt", -1)])

print("=== MOST RECENT RESUME ===")
print(f"Name: {resume.get('candidateName')}")
print(f"Skills: {resume.get('skills', [])}")

# Get Junior Data Analyst job
job = db.jobs.find_one({"title": {"$regex": "Junior", "$options": "i"}})

print(f"\n=== JOB: {job.get('title')} ===")
print(f"Required Skills: {job.get('requiredSkills', [])}")

# Manual match check
resume_skills = resume.get('skills', [])
job_required = job.get('requiredSkills', [])

print("\n=== MANUAL MATCH CHECK ===")
resume_set = {s.lower().strip() for s in resume_skills}
required_set = {s.lower().strip() for s in job_required}

print(f"Resume skills (normalized): {resume_set}")
print(f"Required skills (normalized): {required_set}")

matched = resume_set & required_set
print(f"\nMatched: {matched}")
print(f"Match score: {len(matched)}/{len(required_set)} = {len(matched)/len(required_set)*100:.1f}%")
