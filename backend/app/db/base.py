import sqlite3
from pathlib import Path
from typing import Optional
from backend.app.core import config
from backend.app.core.logger import logger

class BaseDatabase:
    """Base class for database operations handling connections and initialization."""
    
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
            # Job Applications Table
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
            conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_score ON jobs(match_score)")

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

            # Emails Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT DEFAULT '',
                    subject TEXT DEFAULT '',
                    body TEXT DEFAULT '',
                    snippet TEXT DEFAULT '',
                    received_at TEXT DEFAULT '',
                    is_read BOOLEAN DEFAULT 0,
                    labels TEXT DEFAULT '[]',
                    has_reply BOOLEAN DEFAULT 0,
                    reply_content TEXT DEFAULT '',
                    telegram_message_id INTEGER
                )
            """)
            
            # Migration: Ensure telegram_message_id exists
            try:
                conn.execute("ALTER TABLE emails ADD COLUMN telegram_message_id INTEGER")
            except Exception:
                pass 

            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
