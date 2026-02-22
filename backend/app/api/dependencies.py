from backend.app.db.database import JobDatabase

# Singleton instance
db_instance = JobDatabase()

def get_db():
    return db_instance
