import cloudinary
import cloudinary.uploader
import os

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
    # secure=True  # Removed - might cause "untrusted customer" error
)

def upload_resume_to_cloudinary(file, user_id: str, original_filename: str):
    """
    Upload resume to Cloudinary - Simple and reliable approach
    """
    
    # Extract file extension
    file_ext = original_filename.split(".")[-1].lower() if "." in original_filename else "pdf"

    result = cloudinary.uploader.upload(
        file,
        resource_type="auto",  # Let Cloudinary auto-detect type
        folder="resumes",
        public_id=f"resume_{user_id}",  # Remove extension - let Cloudinary handle it
        overwrite=True,
        use_filename=True,
        unique_filename=False
    )

    # Get the secure URL directly from Cloudinary response
    secure_url = result["secure_url"]
    
    # Storage URL - keep original
    storage_url = secure_url
    
    # Preview URL - open in browser (keep as-is)
    preview_url = secure_url
    
    # Download URL - add fl_attachment flag to force download with custom filename
    # Extract base filename without extension for cleaner download name
    base_filename = original_filename.rsplit(".", 1)[0] if "." in original_filename else "Resume"
    # Sanitize filename - replace spaces with underscores, remove special chars
    safe_filename = base_filename.replace(" ", "_").replace("-", "_")
    download_filename = f"{safe_filename}_Resume"  # No extension - Cloudinary adds it automatically
    
    # Insert fl_attachment flag into URL
    # Format: /image/upload/fl_attachment:filename/v123/resumes/resume_xxx.pdf
    if "/upload/" in secure_url:
        download_url = secure_url.replace("/upload/", f"/upload/fl_attachment:{download_filename}/")
    else:
        download_url = secure_url  # Fallback

    return {
        "public_id": result["public_id"],
        "storage_url": storage_url,
        "download_url": download_url,
        "preview_url": preview_url,
        "file_ext": file_ext
    }


def upload_to_cloudinary(file_content, folder: str = "uploads", resource_type: str = "image"):
    """
    Generic upload function for profile photos and company logos
    
    Args:
        file_content: File content (bytes)
        folder: Cloudinary folder name
        resource_type: "image" or "raw"
    
    Returns:
        str: Cloudinary secure URL
    """
    result = cloudinary.uploader.upload(
        file_content,
        resource_type=resource_type,
        folder=folder,
        overwrite=True
    )
    
    return result["secure_url"]

