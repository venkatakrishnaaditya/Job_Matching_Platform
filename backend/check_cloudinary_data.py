"""
Check the actual Cloudinary data stored in database
"""
from app.db.mongo import get_db
from dotenv import load_dotenv

load_dotenv()

def check_cloudinary_data():
    db = get_db()
    
    # Check resume with all Cloudinary fields
    resume = db.resumes.find_one({"candidateId": "696c81fa3a1f271db6404633"})
    
    if resume:
        print("📄 Full resume document:")
        print(f"   Candidate ID: {resume.get('candidateId')}")
        print(f"   Original filename: {resume.get('original_filename')}")
        print(f"   Cloudinary public_id: {resume.get('cloudinary_public_id')}")
        print(f"   Storage URL: {resume.get('resumeFileUrl')}")
        print(f"   Download URL: {resume.get('resumeDownloadUrl')}")
        print(f"   Preview URL: {resume.get('resumePreviewUrl')}")
        print()
        
        # Check if there are other cloudinary fields
        print("All fields in resume document:")
        for key in resume.keys():
            if 'cloudinary' in key.lower() or 'url' in key.lower() or 'public' in key.lower():
                print(f"   {key}: {resume.get(key)}")

if __name__ == "__main__":
    check_cloudinary_data()
