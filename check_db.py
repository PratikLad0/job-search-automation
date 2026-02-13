import sqlite3
import json
from pathlib import Path

db_path = Path("backend/data/jobs.db")
if not db_path.exists():
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check jobs count
cursor.execute("SELECT COUNT(*) FROM jobs")
count = cursor.fetchone()[0]
print(f"Total jobs: {count}")

# Check first 5 jobs
cursor.execute("SELECT id, title, company, status FROM jobs LIMIT 5")
jobs = [dict(row) for row in cursor.fetchall()]
print(f"First 5 jobs: {json.dumps(jobs, indent=2)}")

# Check profile
cursor.execute("SELECT * FROM profiles LIMIT 1")
profile = cursor.fetchone()
if profile:
    print(f"Profile found: {profile['full_name']}")
else:
    print("No profile found")

conn.close()
