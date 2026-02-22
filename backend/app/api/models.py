from pydantic import BaseModel
from typing import Optional, List

class JobBase(BaseModel):
    title: str
    company: str
    location: str
    url: str
    source: str
    description: str = ""
    salary_text: str = ""
    job_type: str = ""
    posted_date: str = ""
    scraped_at: str = ""
    match_score: Optional[float] = None
    score_reasoning: str = ""
    matched_skills: str = ""
    status: str
    resume_path: str = ""
    cover_letter_path: str = ""
    applied_at: Optional[str] = None
    notes: str = ""

class Job(JobBase):
    id: int

    class Config:
        from_attributes = True

class Stats(BaseModel):
    total: int
    avg_score: float
    by_status: dict[str, int]
    by_source: dict[str, int]
