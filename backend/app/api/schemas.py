from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

class JobBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = ""
    url: str
    source: Optional[str] = ""
    description: Optional[str] = ""
    salary_text: Optional[str] = ""
    job_type: Optional[str] = ""
    posted_date: Optional[str] = ""

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    match_score: Optional[float] = None

class JobResponse(JobBase):
    id: int
    scraped_at: str
    status: str
    match_score: Optional[float] = None
    score_reasoning: Optional[str] = ""
    matched_skills: Optional[str] = ""
    applied_at: Optional[str] = None
    resume_path: Optional[str] = ""
    
    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    total: int
    by_status: Dict[str, int]
    by_source: Dict[str, int]
    avg_score: float

class ProfileBase(BaseModel):
    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    about_me: str = ""
    skills: List[str] = []
    experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []

class ProfileResponse(ProfileBase):
    id: int
