"""
SQLite database layer for tracking job applications.
Handles CRUD operations, duplicate detection, and status management.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from backend.app.db.models import Job
from backend.app.core import config
from backend.app.core.logger import logger


class JobDatabase:
    """SQLite-backed job application tracker."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Create tables if they don't exist."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT DEFAULT '',
                    url TEXT UNIQUE NOT NULL,
                    source TEXT DEFAULT '',
                    description TEXT DEFAULT '',
                    salary_text TEXT DEFAULT '',
                    job_type TEXT DEFAULT '',
                    posted_date TEXT DEFAULT '',
                    scraped_at TEXT DEFAULT '',

                    match_score REAL,
                    score_reasoning TEXT DEFAULT '',
                    matched_skills TEXT DEFAULT '',

                    status TEXT DEFAULT 'scraped',
                    resume_path TEXT DEFAULT '',
                    cover_letter_path TEXT DEFAULT '',
                    applied_at TEXT,
                    notes TEXT DEFAULT ''
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_score ON jobs(match_score)
            """)

            # User Profile Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT DEFAULT '',
                    email TEXT DEFAULT '',
                    phone TEXT DEFAULT '',
                    location TEXT DEFAULT '',
                    linkedin_url TEXT DEFAULT '',
                    github_url TEXT DEFAULT '',
                    portfolio_url TEXT DEFAULT '',
                    
                    skills TEXT DEFAULT '[]',
                    experience TEXT DEFAULT '[]',
                    education TEXT DEFAULT '[]',
                    projects TEXT DEFAULT '[]',
                    certifications TEXT DEFAULT '[]',
                    achievements TEXT DEFAULT '[]',
                    hobbies TEXT DEFAULT '[]',
                    interests TEXT DEFAULT '[]',
                    languages TEXT DEFAULT '[]',
                    volunteering TEXT DEFAULT '[]',
                    publications TEXT DEFAULT '[]',
                    awards TEXT DEFAULT '[]',
                    "references" TEXT DEFAULT '[]',
                    
                    resume_path TEXT DEFAULT '',
                    about_me TEXT DEFAULT ''
                )
            """)
            conn.commit()

    def get_profile(self, profile_id: int = 1) -> Optional["UserProfile"]:
        from backend.app.db.models import UserProfile
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,)).fetchone()
            if row:
                return UserProfile.from_dict(dict(row))
        return None

    def create_or_update_profile(self, profile_data: dict, profile_id: int = 1):
        """Create or update the user profile atomically using SQLite UPSERT."""
        from backend.app.db.models import UserProfile
        
        # Ensure ID is set
        profile_data["id"] = profile_id
        
        # Filter out keys that might not be in the table (extra safety)
        # We'll get columns from UserProfile dataclass
        valid_keys = {f.name for f in UserProfile.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in profile_data.items() if k in valid_keys}
        
        columns = ", ".join(f'"{k}"' for k in filtered_data.keys())
        placeholders = ", ".join("?" for _ in filtered_data)
        
        # Build the UPDATE part of the UPSERT
        update_clause = ", ".join(f'"{k}" = EXCLUDED."{k}"' for k in filtered_data.keys() if k != "id")
        
        sql = f"""
            INSERT INTO profiles ({columns})
            VALUES ({placeholders})
            ON CONFLICT(id) DO UPDATE SET {update_clause}
        """
        
        try:
            with self._get_connection() as conn:
                conn.execute(sql, list(filtered_data.values()))
                conn.commit()
            logger.info(f"Updated profile for ID: {profile_id}")
        except Exception as e:
            logger.error(f"Failed to update profile: {e}")
            raise
            
        return self.get_profile(profile_id)

    def delete_profile(self, profile_id: int = 1) -> bool:
        """Delete the user profile for GDPR compliance."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
            conn.commit()
        return True

    def add_job(self, job: Job) -> Optional[int]:
        """Insert a job, skip if URL already exists. Returns job ID or None."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO jobs (
                        title, company, location, url, source, description,
                        salary_text, job_type, posted_date, scraped_at,
                        match_score, score_reasoning, matched_skills,
                        status, resume_path, cover_letter_path, applied_at, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job.title, job.company, job.location, job.url, job.source,
                    job.description, job.salary_text, job.job_type, job.posted_date,
                    job.scraped_at, job.match_score, job.score_reasoning,
                    job.matched_skills, job.status, job.resume_path,
                    job.cover_letter_path, job.applied_at, job.notes,
                ))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Duplicate URL — skip
            return None

    def add_jobs(self, jobs: list[Job]) -> dict:
        """Bulk insert jobs in a single transaction for performance and consistency."""
        added, skipped = 0, 0
        with self._get_connection() as conn:
            for job in jobs:
                try:
                    conn.execute("""
                        INSERT INTO jobs (
                            title, company, location, url, source, description,
                            salary_text, job_type, posted_date, scraped_at,
                            match_score, score_reasoning, matched_skills,
                            status, resume_path, cover_letter_path, applied_at, notes
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        job.title, job.company, job.location, job.url, job.source,
                        job.description, job.salary_text, job.job_type, job.posted_date,
                        job.scraped_at, job.match_score, job.score_reasoning,
                        job.matched_skills, job.status, job.resume_path,
                        job.cover_letter_path, job.applied_at, job.notes,
                    ))
                    added += 1
                except sqlite3.IntegrityError:
                    skipped += 1
            conn.commit()
        return {"added": added, "skipped": skipped}

    def get_job(self, job_id: int) -> Optional[Job]:
        """Get a single job by ID."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            if row:
                return Job.from_dict(dict(row))
        return None

    def get_jobs(
        self,
        status: Optional[str] = None,
        min_score: Optional[float] = None,
        source: Optional[str] = None,
        query: Optional[str] = None,
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[Job]:
        """Query jobs with optional filters."""
        sql = "SELECT * FROM jobs WHERE 1=1"
        params = []

        if status:
            sql += " AND status = ?"
            params.append(status)
        if min_score is not None:
            sql += " AND match_score >= ?"
            params.append(min_score)
        if source:
            sql += " AND source = ?"
            params.append(source)
        if query:
            # Search in title or company
            sql += " AND (title LIKE ? OR company LIKE ?)"
            wildcard_query = f"%{query}%"
            params.extend([wildcard_query, wildcard_query])
        if location:
            sql += " AND location LIKE ?"
            params.append(f"%{location}%")
        if job_type:
            sql += " AND job_type LIKE ?"
            params.append(f"%{job_type}%")

        sql += " ORDER BY match_score DESC NULLS LAST, scraped_at DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [Job.from_dict(dict(row)) for row in rows]

    def update_job(self, job_id: int, **kwargs) -> bool:
        """Update specific fields of a job."""
        if not kwargs:
            return False

        set_clause = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [job_id]

        with self._get_connection() as conn:
            conn.execute(f"UPDATE jobs SET {set_clause} WHERE id = ?", values)
            conn.commit()
        return True

    def update_status(self, job_id: int, new_status: str) -> bool:
        """Update job status. Auto-sets applied_at if status is 'applied'."""
        kwargs = {"status": new_status}
        if new_status == "applied":
            kwargs["applied_at"] = datetime.now().isoformat()
        return self.update_job(job_id, **kwargs)

    def get_unscored_jobs(self) -> list[Job]:
        """Get all jobs that haven't been scored yet."""
        return self.get_jobs(status="scraped")

    def get_high_score_jobs(self, min_score: Optional[float] = None) -> list[Job]:
        """Get jobs with score above threshold."""
        score = min_score or config.MIN_MATCH_SCORE
        return self.get_jobs(min_score=score)

    def get_stats(self) -> dict:
        """Get summary statistics."""
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
            by_status = {}
            for row in conn.execute("SELECT status, COUNT(*) as cnt FROM jobs GROUP BY status"):
                by_status[row["status"]] = row["cnt"]
            avg_score = conn.execute(
                "SELECT AVG(match_score) FROM jobs WHERE match_score IS NOT NULL"
            ).fetchone()[0]
            by_source = {}
            for row in conn.execute("SELECT source, COUNT(*) as cnt FROM jobs GROUP BY source"):
                by_source[row["source"]] = row["cnt"]

        return {
            "total": total,
            "by_status": by_status,
            "by_source": by_source,
            "avg_score": round(avg_score, 1) if avg_score else 0,
        }

    def delete_job(self, job_id: int) -> bool:
        """Delete a job by ID."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
            conn.commit()
        return True

    def reset_applied_status(self) -> dict:
        """
        Reset 'applied' status for all jobs. 
        Reverts to 'resume_generated' if resume path exists, else 'scored'.
        """
        changed = 0
        with self._get_connection() as conn:
            # First, get all applied jobs
            rows = conn.execute("SELECT id, resume_path FROM jobs WHERE status = 'applied'").fetchall()
            
            for row in rows:
                job_id = row["id"]
                resume_path = row["resume_path"]
                new_status = "resume_generated" if resume_path else "scored"
                
                conn.execute(
                    "UPDATE jobs SET status = ?, applied_at = NULL WHERE id = ?", 
                    (new_status, job_id)
                )
                changed += 1
                
            conn.commit()
            
        return {"count": changed}

