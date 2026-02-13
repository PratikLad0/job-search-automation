import json
import uuid
from pathlib import Path
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from backend.app.db.database import JobDatabase
from backend.app.db.models import UserProfile
from backend.app.services.parsers.cv_parser import parse_cv
from backend.app.core import config
from backend.app.api.dependencies import get_db
from backend.app.core.logger import logger

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/", response_model=dict)
async def get_profile(db: JobDatabase = Depends(get_db)):
    """Get the current user profile."""
    profile = db.get_profile()
    if not profile:
        # Return default empty profile
        return UserProfile().to_dict()
    
    # Parse JSON strings back to lists/dicts for response
    data = profile.to_dict()
    for field in UserProfile.COMPLEX_FIELDS:
        try:
            if isinstance(data.get(field), str):
                data[field] = json.loads(data[field])
            elif data.get(field) is None:
                data[field] = []
        except:
            data[field] = []
            
    return data

@router.put("/", response_model=dict)
async def update_profile(data: dict, db: JobDatabase = Depends(get_db)):
    """Update user profile."""
    # Convert lists/dicts to JSON strings for storage
    storage_data = data.copy()
    for field in UserProfile.COMPLEX_FIELDS:
        if field in storage_data:
            if not isinstance(storage_data[field], str):
                storage_data[field] = json.dumps(storage_data[field], ensure_ascii=False)
            
    updated_profile = db.create_or_update_profile(storage_data)
    
    # Return parsed data
    resp_data = updated_profile.to_dict()
    for field in UserProfile.COMPLEX_FIELDS:
        try:
            if isinstance(resp_data.get(field), str):
                resp_data[field] = json.loads(resp_data[field])
        except:
            resp_data[field] = []
            
    return resp_data

@router.delete("/", response_model=dict)
async def delete_profile(db: JobDatabase = Depends(get_db)):
    """Delete user profile for GDPR compliance."""
    db.delete_profile()
    return {"status": "success", "message": "Profile deleted successfully"}

@router.post("/upload-resume", response_model=dict)
async def upload_resume(file: UploadFile = File(...)):
    """Upload resume and parse it to populate profile."""
    # Sanitize filename to prevent path traversal and collisions
    # We use UUID to ensure uniqueness and strip the filename to prevent traversal
    file_ext = Path(file.filename).suffix
    if file_ext.lower() not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, DOCX, and TXT are allowed.")
    
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    uploads_dir = config.DATA_DIR / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = uploads_dir / unique_filename
    
    # Verify the path is within the uploads directory (extra safety)
    if not str(file_path.resolve()).startswith(str(uploads_dir.resolve())):
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Async file writing
    async with aiofiles.open(file_path, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)
        
    # Parse resume
    try:
        logger.info(f"📄 Parsing resume: {file_path}")
        cv_data = parse_cv(file_path, force_refresh=True)
        logger.info(f"✅ Resume parsed successfully for: {cv_data.name}")
    except Exception as e:
        logger.error(f"❌ Failed to parse resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")
        
    # Convert CVData to Profile format
    profile_update = {
        "full_name": cv_data.name,
        "email": cv_data.email,
        "phone": cv_data.phone,
        "location": cv_data.location,
        "about_me": cv_data.summary,
        "skills": cv_data.skills,
        "experience": cv_data.experience,
        "education": cv_data.education,
        "projects": cv_data.projects,
        "certifications": cv_data.certifications,
        "achievements": cv_data.achievements,
        "hobbies": cv_data.hobbies,
        "interests": cv_data.interests,
        "languages": cv_data.languages,
        "volunteering": cv_data.volunteering,
        "publications": cv_data.publications,
        "awards": cv_data.awards,
        "references": cv_data.references,
        "resume_path": str(file_path)
    }
    
    # Auto-save to DB or return data to frontend to review?
    # Let's auto-save but return data for frontend to display
    
    # Note: We are NOT calling db.create_or_update_profile here 
    # because we want the user to review the parsed data in the form first.
    # The frontend should pre-fill the form with this response.
    
    return profile_update
