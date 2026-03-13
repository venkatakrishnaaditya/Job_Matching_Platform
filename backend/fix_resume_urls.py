"""
Fix existing resume URLs in MongoDB by adding missing file extensions and versions
"""
from app.db.mongo import get_db
import os
from dotenv import load_dotenv

load_dotenv()

def fix_resume_urls():
    db = get_db()
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    
    # Fix resumes collection
    resumes = db.resumes.find({})
    fixed_count = 0
    
    for resume in resumes:
        needs_update = False
        update_fields = {}
        
        # Get version from existing URL or use a default
        file_url = resume.get("resumeFileUrl", "")
        if "/v" in file_url:
            version = file_url.split("/v")[1].split("/")[0]
        else:
            print(f"⚠️  No version found for resume {resume.get('_id')}, using default")
            version = "1"
        
        # Get file extension
        original_filename = resume.get("original_filename", "resume.pdf")
        file_ext = original_filename.split(".")[-1].lower()
        
        # Get public_id
        public_id = f"resumes/resume_{resume.get('candidateId')}"
        
        # Fix storage URL
        if "resumeFileUrl" in resume:
            correct_storage_url = f"https://res.cloudinary.com/{cloud_name}/raw/upload/v{version}/{public_id}.{file_ext}"
            if resume["resumeFileUrl"] != correct_storage_url:
                update_fields["resumeFileUrl"] = correct_storage_url
                needs_update = True
        
        # Fix download URL
        if "resumeDownloadUrl" in resume:
            correct_download_url = f"https://res.cloudinary.com/{cloud_name}/raw/upload/fl_attachment:{original_filename}/v{version}/{public_id}.{file_ext}"
            if resume["resumeDownloadUrl"] != correct_download_url:
                update_fields["resumeDownloadUrl"] = correct_download_url
                needs_update = True
        
        # Fix preview URL (only for PDFs)
        if file_ext == "pdf" and "resumePreviewUrl" in resume:
            correct_preview_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/f_pdf/v{version}/{public_id}.pdf"
            if resume["resumePreviewUrl"] != correct_preview_url:
                update_fields["resumePreviewUrl"] = correct_preview_url
                needs_update = True
        
        if needs_update:
            db.resumes.update_one(
                {"_id": resume["_id"]},
                {"$set": update_fields}
            )
            fixed_count += 1
            print(f"✅ Fixed resume for candidate {resume.get('candidateId')}")
    
    # Fix applications collection (they have resume file snapshots)
    applications = db.applications.find({})
    fixed_apps = 0
    
    for app in applications:
        needs_update = False
        update_fields = {}
        
        resume_files = app.get("resumeFiles", {})
        
        # Get candidate's resume to get correct URLs
        candidate_id = app.get("candidateId")
        candidate_resume = db.resumes.find_one({"candidateId": candidate_id})
        
        if candidate_resume:
            if resume_files.get("resumeFileUrl") != candidate_resume.get("resumeFileUrl"):
                update_fields["resumeFiles.resumeFileUrl"] = candidate_resume.get("resumeFileUrl")
                needs_update = True
            
            if resume_files.get("resumeDownloadUrl") != candidate_resume.get("resumeDownloadUrl"):
                update_fields["resumeFiles.resumeDownloadUrl"] = candidate_resume.get("resumeDownloadUrl")
                needs_update = True
            
            if resume_files.get("resumePreviewUrl") != candidate_resume.get("resumePreviewUrl"):
                update_fields["resumeFiles.resumePreviewUrl"] = candidate_resume.get("resumePreviewUrl")
                needs_update = True
        
        if needs_update:
            db.applications.update_one(
                {"_id": app["_id"]},
                {"$set": update_fields}
            )
            fixed_apps += 1
            print(f"✅ Fixed application {app.get('_id')}")
    
    print(f"\n✅ Migration complete!")
    print(f"   Fixed {fixed_count} resumes")
    print(f"   Fixed {fixed_apps} applications")

if __name__ == "__main__":
    print("🔧 Starting resume URL migration...")
    fix_resume_urls()
