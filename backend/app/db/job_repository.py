import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from backend.app.db.base import BaseDatabase
from backend.app.db.models import Job
from backend.app.core import config
from backend.app.core.logger import logger

class JobRepository(BaseDatabase):
    """Repository for job application operations."""

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
            return None

    def add_jobs(self, jobs: List[Job]) -> Dict[str, int]:
        """Bulk insert jobs."""
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
    ) -> List[Job]:
        """Query jobs with optional filters and advanced ordering."""
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

    def get_stats(self) -> Dict[str, Any]:
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
