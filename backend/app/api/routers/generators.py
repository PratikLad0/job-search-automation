from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
import os
import logging

from backend.app.db.database import JobDatabase
from backend.app.api.dependencies import get_db
from backend.app.core.queue_manager import queue_manager
from backend.app.services.ai.tasks import (
    process_resume_generation, 
    process_cover_letter_generation,
    process_job_application,
    process_job_scoring,
    process_bulk_scoring
)

logger = logging.getLogger("jobsearch.generators")

router = APIRouter(prefix="/generators", tags=["generators"])

class GenerateResponse(BaseModel):
    status: str
    message: str
    document_path: Optional[str] = None
    format: str = "pdf"


@router.post("/{job_id}/resume", response_model=GenerateResponse)
async def generate_resume(
    job_id: int, 
    format: str = "pdf", 
    db: JobDatabase = Depends(get_db)
):
    """Queue resume generation task."""
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    await queue_manager.add_task(
        "resume_generation",
        process_resume_generation,
        job_id=job_id,
        format=format
    )
    
    return GenerateResponse(status="queued", message=f"Resume {format.upper()} generation queued")


@router.post("/{job_id}/cover_letter", response_model=GenerateResponse)
async def generate_cover_letter(
    job_id: int, 
    format: str = "pdf", 
    db: JobDatabase = Depends(get_db)
):
    """Queue cover letter generation task."""
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    await queue_manager.add_task(
        "cover_letter_generation",
        process_cover_letter_generation,
        job_id=job_id,
        format=format
    )
    
    return GenerateResponse(status="queued", message=f"Cover letter {format.upper()} generation queued")


@router.post("/{job_id}/apply", response_model=GenerateResponse)
async def apply_to_job(
    job_id: int, 
    db: JobDatabase = Depends(get_db)
):
    """Queue automated job application task."""
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.resume_path:
        raise HTTPException(status_code=400, detail="Resume must be generated before applying")
        
    await queue_manager.add_task(
        "job_application",
        process_job_application,
        job_id=job_id
    )
    
    return GenerateResponse(status="queued", message="Automated application queued")

@router.post("/{job_id}/score", response_model=GenerateResponse)
async def score_job_endpoint(
    job_id: int, 
    db: JobDatabase = Depends(get_db)
):
    """Queue scoring task for a specific job."""
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    await queue_manager.add_task(
        "job_scoring",
        process_job_scoring,
        job_id=job_id
    )
    
    return GenerateResponse(status="queued", message="Job scoring queued")


@router.post("/score_all", response_model=GenerateResponse)
async def score_all_jobs_endpoint():
    """Queue scoring task for all unscored jobs."""
    await queue_manager.add_task(
        "bulk_scoring",
        process_bulk_scoring
    )
    
    return GenerateResponse(status="queued", message="Bulk scoring queued")


from fastapi.responses import FileResponse

@router.get("/download")
async def download_file(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=os.path.basename(path))

