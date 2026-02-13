from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional
from pydantic import BaseModel
import sys
import os



try:
    from backend.app.db.database import JobDatabase
    from backend.app.api.dependencies import get_db
    # Dynamic import for generators to avoid issues if not needed immediately
except ImportError:
    pass

router = APIRouter(prefix="/generate", tags=["generators"])

class GenerateResponse(BaseModel):
    status: str
    message: str
    resume_path: Optional[str] = None
    cover_letter_path: Optional[str] = None
    format: str = "pdf"

def run_generation_task(job_id: int, format: str = "pdf"):
    try:
        # Import generators dynamically
        from backend.app.services.generators.resume_generator import generate_all as generate_pdf
        from backend.app.services.generators.docx_generator import generate_resume_docx, generate_cover_letter_docx
        from backend.app.db.database import JobDatabase
        
        db = JobDatabase()
        job = db.get_job(job_id)
        if not job:
            return
            
        # Fetch User Profile
        profile = db.get_profile(1) # Default profile ID
        cv_data = profile.to_cv_data() if profile else None

        print(f"Generating {format.upper()} documents for job {job_id}...")
        
        resume_path = None
        cover_letter_path = None

        if format.lower() == "pdf":
            result = generate_pdf(job, cv_data)
            resume_path = result.get("resume_path")
            cover_letter_path = result.get("cover_letter_path")
        elif format.lower() == "docx":
            r_path = generate_resume_docx(job, cv_data)
            c_path = generate_cover_letter_docx(job, cv_data)
            resume_path = str(r_path) if r_path else None
            cover_letter_path = str(c_path) if c_path else None

        if resume_path:
            db.update_job(job_id, resume_path=resume_path, status="resume_generated")
        if cover_letter_path:
            db.update_job(job_id, cover_letter_path=cover_letter_path)
            
        print(f"Generation complete for job {job_id}")
    except Exception as e:
        print(f"Error generating documents: {e}")

@router.post("/{job_id}", response_model=GenerateResponse)
async def generate_docs(
    job_id: int, 
    format: str = "pdf", 
    background_tasks: BackgroundTasks = None, 
    db: JobDatabase = Depends(get_db)
):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if background_tasks:
        background_tasks.add_task(run_generation_task, job_id, format)
    else:
        run_generation_task(job_id, format)
    
    return GenerateResponse(status="started", message=f"{format.upper()} generation started in background")

from fastapi.responses import FileResponse

@router.get("/download")
async def download_file(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=os.path.basename(path))
