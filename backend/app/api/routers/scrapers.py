from fastapi import APIRouter
from typing import Optional
from pydantic import BaseModel

from backend.app.core.logger import logger
from backend.app.core.queue_manager import queue_manager
from backend.app.services.ai.tasks import process_scraping

router = APIRouter(prefix="/scrapers", tags=["scrapers"])

class ScrapeRequest(BaseModel):
    source: Optional[str] = None
    query: Optional[str] = None
    location: Optional[str] = None


@router.post("/run")
async def run_scraper(request: ScrapeRequest):
    """Queue a scraper task."""
    await queue_manager.add_task(
        "scraping",
        process_scraping,
        source=request.source,
        query=request.query,
        location=request.location
    )
    return {"status": "queued", "message": "Scraper task queued"}
