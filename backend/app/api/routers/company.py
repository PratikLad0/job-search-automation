
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional

from backend.app.core.logger import logger
from backend.app.api.dependencies import get_db
from backend.app.db.database import JobDatabase
from backend.app.db.models import UserProfile, Job
from backend.app.services.scrapers.ai_company_scraper import AICompanyScraper

router = APIRouter(prefix="/company", tags=["company"])

class CompanySearchRequest(BaseModel):
    company_name: str
    locations: List[str]
    user_id: Optional[int] = 1

class CompanySearchResponse(BaseModel):
    message: str
    jobs_found: int
    jobs: List[dict]

@router.post("/search", response_model=CompanySearchResponse)
async def search_company_jobs(request: CompanySearchRequest, db: JobDatabase = Depends(get_db)):
    """
    Search for jobs at a specific company and location using AI scraping.
    """
    logger.info(f"Received company search request: {request.company_name} in {request.locations}")
    
    # Get User Profile
    user_profile = db.get_profile(request.user_id)
    if not user_profile:
        # Fallback to default/empty profile if not found
        user_profile = UserProfile()
        
    scraper = AICompanyScraper()
    jobs = await scraper.scrape_company(
        company=request.company_name,
        locations=request.locations,
        user_profile=user_profile
    )
    
    if not jobs:
        return {
            "message": "No jobs found",
            "jobs_found": 0,
            "jobs": []
        }
    
    # Save to DB
    result = db.add_jobs(jobs)
    added_count = result["added"]
    skipped_count = result["skipped"]
    
    logger.info(f"Saved {added_count} jobs, skipped {skipped_count} duplicates.")

    # Retrieve specific jobs that were added/processed?
    # Since add_jobs doesn't return the IDs easily without refetching,
    # and we want to return the jobs to the frontend...
    # We can just return the scraped job objects (as dicts).
    
    # Note: The 'jobs' list contains Job objects which might not have IDs yet if they were just created.
    # But for search results display, that might be fine.
    # If we want IDs, we'd need to fetch them from DB based on URL.
    
    return {
        "message": f"Search completed. Found {len(jobs)} jobs.",
        "jobs_found": len(jobs),
        "jobs": [j.to_dict() for j in jobs]
    }
