from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from backend.app.api.models import Job
from backend.app.api.dependencies import get_db
from backend.app.db.database import JobDatabase

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/", response_model=List[Job])
async def list_jobs(
    status: Optional[str] = None,
    min_score: Optional[float] = None,
    source: Optional[str] = None,
    query: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    limit: int = 100,
    db: JobDatabase = Depends(get_db)
):
    jobs = db.get_jobs(
        status=status,
        min_score=min_score,
        source=source,
        query=query,
        location=location,
        job_type=job_type,
        limit=limit
    )
    return jobs

@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: int, db: JobDatabase = Depends(get_db)):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/{job_id}/applied")
async def mark_applied(job_id: int, db: JobDatabase = Depends(get_db)):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    success = db.update_status(job_id, "applied")
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update status")
    
    return {"status": "success", "message": f"Job {job_id} marked as applied"}
