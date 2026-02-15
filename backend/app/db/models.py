"""
Data models for the job tracker.
Uses dataclasses for clean, type-safe data structures.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Job:
    """Represents a scraped job posting."""
    id: Optional[int] = None
    title: str = ""
    company: str = ""
    location: str = ""
    url: str = ""
    source: str = ""  # linkedin, indeed, remoteok, naukri
    description: str = ""
    salary_text: str = ""
    job_type: str = ""  # full-time, contract, remote
    posted_date: str = ""
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # AI scoring
    match_score: Optional[float] = None
    score_reasoning: str = ""
    matched_skills: str = ""

    # Application tracking
    status: str = "scraped"  # scraped → scored → resume_generated → applied → interview → offer → rejected
    resume_path: str = ""
    cover_letter_path: str = ""
    applied_at: Optional[str] = None
    notes: str = ""
    
    # Contact & Application Info
    recruiter_email: str = ""
    recruiter_name: str = ""
    application_form_url: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Job":
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)


@dataclass
class CVData:
    """Parsed CV information for matching."""
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    summary: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    skills: list[str] = field(default_factory=list)
    experience: list[dict] = field(default_factory=list)
    education: list[dict] = field(default_factory=list)
    projects: list[dict] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    achievements: list[str] = field(default_factory=list)
    hobbies: list[str] = field(default_factory=list)
    interests: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    volunteering: list[dict] = field(default_factory=list)
    publications: list[dict] = field(default_factory=list)
    awards: list[dict] = field(default_factory=list)
    references: list[dict] = field(default_factory=list)
    total_years: int = 0
    raw_text: str = ""

    def get_skills_text(self) -> str:
        return ", ".join(self.skills)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CVData":
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)


@dataclass
class UserProfile:
    """User profile data for resume generation and job matching."""
    id: int = 1
    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    
    # JSON strings for storage in SQLite
    skills: str = "[]"
    experience: str = "[]"
    education: str = "[]"
    projects: str = "[]"
    certifications: str = "[]"
    achievements: str = "[]"
    hobbies: str = "[]"
    interests: str = "[]"
    languages: str = "[]"
    volunteering: str = "[]"
    publications: str = "[]"
    awards: str = "[]"
    references: str = "[]"
    
    # Additional fields
    resume_path: str = ""
    about_me: str = ""

    # Fields that are stored as JSON strings
    COMPLEX_FIELDS = [
        "skills", "experience", "education", "projects", "certifications", 
        "achievements", "hobbies", "interests", "languages", 
        "volunteering", "publications", "awards", "references"
    ]
    
    def to_cv_data(self) -> CVData:
        """Convert UserProfile to CVData for matching/generation."""
        import json
        
        # Helper to safely parse JSON strings
        def safe_load(s: str) -> list:
            try:
                return json.loads(s) if s else []
            except (json.JSONDecodeError, TypeError):
                return []

        return CVData(
            name=self.full_name,
            email=self.email,
            phone=self.phone,
            location=self.location,
            summary=self.about_me,
            linkedin_url=self.linkedin_url,
            github_url=self.github_url,
            portfolio_url=self.portfolio_url,
            skills=safe_load(self.skills),
            experience=safe_load(self.experience),
            education=safe_load(self.education),
            projects=safe_load(self.projects),
            certifications=safe_load(self.certifications),
            achievements=safe_load(self.achievements),
            hobbies=safe_load(self.hobbies),
            interests=safe_load(self.interests),
            languages=safe_load(self.languages),
            volunteering=safe_load(self.volunteering),
            publications=safe_load(self.publications),
            awards=safe_load(self.awards),
            references=safe_load(self.references),
            # total_years could be calculated or stored, but for now we'll estimate from experience
            total_years=len(safe_load(self.experience)) * 2, # Rough estimate or add a field
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)


@dataclass
class Email:
    """Represents a job-related email."""
    id: Optional[int] = None
    sender: str = ""
    subject: str = ""
    body: str = ""  # HTML or Text content
    snippet: str = ""
    received_at: str = ""
    is_read: bool = False
    labels: str = "[]"  # JSON list of labels
    has_reply: bool = False
    reply_content: str = ""
    telegram_message_id: Optional[int] = None
    
    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Email":
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)
