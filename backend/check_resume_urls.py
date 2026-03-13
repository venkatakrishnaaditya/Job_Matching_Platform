"""
Check what resume URLs look like after migration
"""
from app.db.mongo import get_db
from dotenv import load_dotenv

load_dotenv()

def check_urls():
    db = get_db()
    
    # Check one resume
    resume = db.resumes.find_one({"candidateId": "696c81fa3a1f271db6404633"})
    
    if resume:
        print("📄 Resume URLs for candidate 696c81fa3a1f271db6404633:")
        print(f"   Storage URL: {resume.get('resumeFileUrl')}")
        print(f"   Download URL: {resume.get('resumeDownloadUrl')}")
        print(f"   Preview URL: {resume.get('resumePreviewUrl')}")
        print()
    
    # Check one application
    app = db.applications.find_one({"candidateId": "696c81fa3a1f271db6404633"})
    
    if app:
        print("📋 Application resume URLs:")
        resume_files = app.get("resumeFiles", {})
        print(f"   Storage URL: {resume_files.get('resumeFileUrl')}")
        print(f"   Download URL: {resume_files.get('resumeDownloadUrl')}")
        print(f"   Preview URL: {resume_files.get('resumePreviewUrl')}")

if __name__ == "__main__":
    check_urls()
