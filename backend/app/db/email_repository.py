from typing import Optional, List, Dict, Any
from backend.app.db.base import BaseDatabase
from backend.app.db.models import Email
from backend.app.core.logger import logger

class EmailRepository(BaseDatabase):
    """Repository for email related operations."""

    def add_email(self, email: Email) -> Optional[int]:
        """Save an email to the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO emails (
                        sender, subject, body, snippet, received_at,
                        is_read, labels, has_reply, reply_content, telegram_message_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    email.sender, email.subject, email.body, email.snippet,
                    email.received_at, email.is_read, email.labels,
                    email.has_reply, email.reply_content, email.telegram_message_id
                ))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to add email: {e}")
            return None

    def get_emails(self, skip: int = 0, limit: int = 50) -> List[Email]:
        """Get listed emails."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM emails ORDER BY received_at DESC LIMIT ? OFFSET ?", 
                (limit, skip)
            ).fetchall()
            return [Email.from_dict(dict(row)) for row in rows]

    def get_email(self, email_id: int) -> Optional[Email]:
        """Get a single email by ID."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM emails WHERE id = ?", (email_id,)).fetchone()
            if row:
                return Email.from_dict(dict(row))
        return None

    def update_email(self, email_id: int, **kwargs) -> bool:
        """Update specific fields of an email."""
        if not kwargs:
            return False
        set_clause = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [email_id]
        with self._get_connection() as conn:
            conn.execute(f"UPDATE emails SET {set_clause} WHERE id = ?", values)
            conn.commit()
        return True
