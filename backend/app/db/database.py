from typing import List, Optional, Any, Dict
from backend.app.db.job_repository import JobRepository
from backend.app.db.profile_repository import ProfileRepository
from backend.app.db.email_repository import EmailRepository
from backend.app.db.models import Job, Email, UserProfile
from backend.app.core.logger import logger

class JobDatabase(JobRepository, ProfileRepository, EmailRepository):
    """
    Unified database interface for the Job Search Automation app.
    Inherits from specialized repositories to maintain backward compatibility
    while allowing modular development.
    """

    def get_unscored_jobs(self):
        """Get all jobs that haven't been scored yet."""
        return self.get_jobs(status="scraped")

    def get_high_score_jobs(self, min_score: float = None):
        """Get jobs with score above threshold."""
        from backend.app.core import config
        score = min_score or config.MIN_MATCH_SCORE
        return self.get_jobs(min_score=score)

    def reset_applied_status(self) -> dict:
        """
        Reset 'applied' status for all jobs. 
        Reverts to 'resume_generated' if resume path exists, else 'scored'.
        """
        changed = 0
        with self._get_connection() as conn:
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

    def get_profile(self, profile_id: int = 1) -> Optional[UserProfile]:
        """Override to return UserProfile model instead of dict."""
        data = super().get_profile(profile_id)
        if data:
            return UserProfile.from_dict(data)
        return None

    def get_email_by_telegram_id(self, message_id: int) -> Optional[Email]:
        """Get email by its Telegram message ID."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM emails WHERE telegram_message_id = ?", (message_id,)).fetchone()
            if row:
                return Email.from_dict(dict(row))
        return None

# Singleton instance for the app
db = JobDatabase()
