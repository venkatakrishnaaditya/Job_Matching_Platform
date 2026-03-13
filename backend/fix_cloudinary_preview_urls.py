"""
Fix Cloudinary Preview URLs - Remove /f_pdf/ from paths
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.db.mongo import get_db

def fix_preview_urls():
    """Fix preview URLs in resumes and applications collections"""
    
    db = get_db()
    
    # Fix resumes collection
    resumes = list(db.resumes.find({"resumePreviewUrl": {"$exists": True}}))
    print(f"Found {len(resumes)} resumes to check")
    
    resume_fixed = 0
    for resume in resumes:
        preview_url = resume.get("resumePreviewUrl")
        if preview_url and "/image/upload/" in preview_url:
            # Change from /image/upload/ to /raw/upload/
            new_url = preview_url.replace("/image/upload/", "/raw/upload/")
            
            db.resumes.update_one(
                {"_id": resume["_id"]},
                {"$set": {"resumePreviewUrl": new_url}}
            )
            resume_fixed += 1
            print(f"✅ Fixed resume {resume['_id']}")
    
    print(f"\n✅ Fixed {resume_fixed} resumes")
    
    # Fix applications collection
    applications = list(db.applications.find({"resumeFiles.resumePreviewUrl": {"$exists": True}}))
    print(f"\nFound {len(applications)} applications to check")
    
    app_fixed = 0
    for app in applications:
        resume_files = app.get("resumeFiles", {})
        preview_url = resume_files.get("resumePreviewUrl")
        
        if preview_url and "/image/upload/" in preview_url:
            # Change from /image/upload/ to /raw/upload/
            new_url = preview_url.replace("/image/upload/", "/raw/upload/")
            
            db.applications.update_one(
                {"_id": app["_id"]},
                {"$set": {"resumeFiles.resumePreviewUrl": new_url}}
            )
            app_fixed += 1
            print(f"✅ Fixed application {app['_id']}")
    
    print(f"\n✅ Fixed {app_fixed} applications")
    print(f"\n🎉 Migration complete! Total fixed: {resume_fixed + app_fixed}")

if __name__ == "__main__":
    fix_preview_urls()
