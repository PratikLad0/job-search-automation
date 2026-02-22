from fastapi import APIRouter, Depends
from backend.app.api.models import Stats
from backend.app.api.dependencies import get_db
from backend.app.db.database import JobDatabase

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/", response_model=Stats)
async def get_stats(db: JobDatabase = Depends(get_db)):
    stats = db.get_stats()
    return stats
