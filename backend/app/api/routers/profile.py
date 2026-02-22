import json
import uuid
from pathlib import Path
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from backend.app.db.database import JobDatabase
from backend.app.db.models import UserProfile
from backend.app.core import config
from backend.app.api.dependencies import get_db
from backend.app.core.queue_manager import queue_manager
from backend.app.services.ai.tasks import process_profile_update

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
    """Upload resume and queue a background task to populate profile."""
    file_ext = Path(file.filename).suffix
    if file_ext.lower() not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, DOCX, and TXT are allowed.")
    
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    uploads_dir = config.DATA_DIR / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = uploads_dir / unique_filename
    
    # Async file writing
    async with aiofiles.open(file_path, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)
        
    # Queue the background parsing and update task
    await queue_manager.add_task(
        "profile_update",
        process_profile_update,
        file_path=file_path
    )
    
    return {
        "status": "queued", 
        "message": "Resume upload successful. Background profile update started.",
        "file_path": str(file_path)
    }
