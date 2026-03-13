"""
Re-upload all existing resumes to Cloudinary with resource_type="auto"
This fixes preview and download issues for resumes uploaded as "raw"
"""
import sys
import os
import requests
import tempfile
sys.path.append(os.path.dirname(__file__))

from app.db.mongo import get_db
from app.utils.cloudinary import upload_resume_to_cloudinary

def reupload_all_resumes():
    """Download and re-upload all resumes with correct resource_type"""
    
    db = get_db()
    
    # Get all resumes
    resumes = list(db.resumes.find({}))
    print(f"Found {len(resumes)} resumes to re-upload\n")
    
    success_count = 0
    error_count = 0
    
    for idx, resume in enumerate(resumes, 1):
        resume_id = str(resume["_id"])
        candidate_id = resume.get("candidateId")
        original_filename = resume.get("originalFilename", "resume.pdf")
        old_url = resume.get("resumeFileUrl")
        
        print(f"[{idx}/{len(resumes)}] Processing resume {resume_id}...")
        
        if not old_url:
            print(f"  ⚠️  No resumeFileUrl found, skipping")
            error_count += 1
            continue
        
        try:
            # Download the file from Cloudinary
            print(f"  📥 Downloading from: {old_url}")
            response = requests.get(old_url, timeout=30)
            
            if response.status_code != 200:
                print(f"  ❌ Failed to download: HTTP {response.status_code}")
                error_count += 1
                continue
            
            # Save to temporary file
            file_ext = original_filename.split('.')[-1] if '.' in original_filename else 'pdf'
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            # Re-upload to Cloudinary with resource_type="auto"
            print(f"  📤 Re-uploading to Cloudinary...")
            result = upload_resume_to_cloudinary(
                temp_path,
                candidate_id,
                original_filename
            )
            
            # Update database with new URLs
            update_data = {
                "resumeFileUrl": result["storage_url"],
                "resumeDownloadUrl": result["download_url"],
                "resumePreviewUrl": result["preview_url"]
            }
            
            db.resumes.update_one(
                {"_id": resume["_id"]},
                {"$set": update_data}
            )
            
            # Update all applications that reference this resume
            db.applications.update_many(
                {"candidateId": candidate_id},
                {"$set": {
                    "resumeFiles.resumeFileUrl": result["storage_url"],
                    "resumeFiles.resumeDownloadUrl": result["download_url"],
                    "resumeFiles.resumePreviewUrl": result["preview_url"]
                }}
            )
            
            # Clean up temp file
            os.unlink(temp_path)
            
            print(f"  ✅ Successfully re-uploaded!")
            print(f"     Preview: {result['preview_url']}")
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            error_count += 1
            continue
    
    print(f"\n{'='*60}")
    print(f"🎉 Migration Complete!")
    print(f"   ✅ Success: {success_count}")
    print(f"   ❌ Failed: {error_count}")
    print(f"   Total: {len(resumes)}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    print("="*60)
    print("Resume Re-upload Migration Script")
    print("="*60)
    print("\nThis will:")
    print("1. Download all existing resumes from Cloudinary")
    print("2. Re-upload with resource_type='auto'")
    print("3. Update all database records with new URLs")
    print("\nThis may take a few minutes...\n")
    
    confirm = input("Continue? (yes/no): ")
    if confirm.lower() in ['yes', 'y']:
        reupload_all_resumes()
    else:
        print("Migration cancelled.")
