# API Documentation

The Job Search Automation Backend is built with **FastAPI**.
You can view the interactive Swagger documentation at `http://localhost:8000/docs` when the server is running.

## Core Endpoints

### 🔐 Authentication (`/auth`)
- `GET /auth/login`: Initiate Google OAuth2 flow.
- `GET /auth/callback`: Handle Google OAuth2 callback.
- `GET /auth/status`: Check if Google authentication is active.

### 👤 Profile (`/profile`)
- `GET /profile/`: Get the current user profile.
- `PUT /profile/`: Update user profile details.
- `DELETE /profile/`: Delete user profile (GDPR).
- `POST /profile/upload-resume`: Upload a resume (PDF/DOCX) to auto-populate profile via AI.

### 🟢 Jobs (`/jobs`)
- `GET /jobs`: List all jobs with filters (status, min_score, location, query, etc.).
- `GET /jobs/{id}`: Get detailed info for a single job.
- `POST /jobs/{id}/applied`: Mark a job as applied.

### 🏢 Company Search (`/company`)
- `POST /company/search`: Trigger a targeted AI search for a specific company's career page.
  - Body: `{ "company_name": "Anthropic", "locations": ["Remote", "SF"] }`

### 📧 Emails (`/emails`)
- `GET /emails/`: List job-related emails.
- `GET /emails/{id}`: Get specific email details.
- `POST /emails/{id}/reply`: Generate an AI reply for an email.

### 🤖 Generation (`/generate`)
- `POST /generate/{id}`: Trigger background generation of Resume and Cover Letter for a job.

### 🕷️ Scrapers (`/scrapers`)
- `POST /scrapers/run`: Trigger a background scraping task.
  - Body: `{ "source": "linkedin", "query": "python", "location": "remote" }`

### 💬 Assistant (`/assistant`)
- `WS /assistant/ws`: WebSocket endpoint for real-time AI chat.
  - Payload processes `chat` messages and `ping`.

### 📊 Stats (`/stats`)
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

### Profile
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "skills": ["Python", "React"],
  "experience": [...]
}
```
