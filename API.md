# API Documentation

The Job Search Automation Backend is built with **FastAPI**.
You can view the interactive Swagger documentation at `http://localhost:8000/docs` when the server is running.

## Core Endpoints

### 🟢 Jobs
- `GET /jobs`: List all jobs with filters (status, min_score, location, query, etc.).
- `GET /jobs/{id}`: Get detailed info for a single job.
- `POST /jobs/{id}/applied`: Mark a job as applied.

### 🤖 Generation
- `POST /generate/{id}`: Trigger background generation of Resume and Cover Letter for a job.

### 🕷️ Scrapers
- `POST /scrapers/run`: Trigger a background scraping task.
  - Body: `{ "source": "linkedin", "query": "python", "location": "remote" }`

### 💬 Chat
- `POST /chat/`: Send a message to the AI career assistant.
  - Body: `{ "message": "How do I improve my resume?", "context": "optional context" }`

### 📊 Stats
- `GET /stats`: Get dashboard statistics (total jobs, application status counts, sources).

## Data Models

### Job
```json
{
  "id": 1,
  "title": "Senior Engineer",
  "company": "Tech Corp",
  "location": "Remote",
  "match_score": 8.5,
  "status": "scraped",
  "url": "https://..."
}
```

### Stats
```json
{
  "total": 150,
  "avg_score": 7.2,
  "by_status": { "applied": 10, "scraped": 140 },
  "by_source": { "linkedin": 100, "indeed": 50 }
}
```
