from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
from pydantic import BaseModel
# Dynamic import to avoid circular dependency if possible, or just standard import
import importlib
import sys
import os



from backend.app.core.logger import logger

router = APIRouter(prefix="/scrapers", tags=["scrapers"])

class ScrapeRequest(BaseModel):
    source: Optional[str] = None
    query: Optional[str] = None
    location: Optional[str] = None

def run_scraper_task(source: Optional[str], query: Optional[str], location: Optional[str]):
    # Allow time for imports
    try:
        from backend.app.cli import _get_scrapers  # Import from root main.py helper
        from backend.app.db.database import JobDatabase
        
        db = JobDatabase()
        scrapers = _get_scrapers(source)
        
        for scraper_cls in scrapers:
            scraper = scraper_cls()
            logger.info(f"🚀 Scraping {scraper.SOURCE_NAME}...")
            if query and location:
                jobs = scraper.scrape(query, location)
            elif query:
                jobs = scraper.scrape(query)
            else:
                jobs = scraper.scrape_all()
            
            result = db.add_jobs(jobs)
            logger.info(f"✅ Added {result['added']} jobs from {scraper.SOURCE_NAME} (Skipped {result['skipped']} duplicates)")
            
    except Exception as e:
        logger.error(f"❌ Error in background scraper: {e}", exc_info=True)

@router.post("/run")
async def run_scraper(request: ScrapeRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_scraper_task, request.source, request.query, request.location)
    return {"status": "started", "message": "Scraper task started in background"}
