from typing import Optional, Dict, Any
from backend.app.db.base import BaseDatabase
from backend.app.core.logger import logger

class ProfileRepository(BaseDatabase):
    """Repository for user profile operations."""

    def get_profile(self, profile_id: int = 1) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,)).fetchone()
            if row:
                return dict(row)
        return None

    def create_or_update_profile(self, profile_data: Dict[str, Any], profile_id: int = 1) -> Optional[Dict[str, Any]]:
        """Create or update the user profile atomically."""
        profile_data["id"] = profile_id
        
        # In a real app, we'd validate keys against the table schema
        columns = ", ".join(f'"{k}"' for k in profile_data.keys())
        placeholders = ", ".join("?" for _ in profile_data)
        update_clause = ", ".join(f'"{k}" = EXCLUDED."{k}"' for k in profile_data.keys() if k != "id")
        
        sql = f"""
            INSERT INTO profiles ({columns})
            VALUES ({placeholders})
            ON CONFLICT(id) DO UPDATE SET {update_clause}
        """
        
        with self._get_connection() as conn:
            conn.execute(sql, list(profile_data.values()))
            conn.commit()
            
        return self.get_profile(profile_id)

    def delete_profile(self, profile_id: int = 1) -> bool:
        """Delete user profile."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
            conn.commit()
        return True
