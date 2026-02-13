# 🐍 Job Search Automation - Backend

Python-based API, scrapers, and AI engine for the Job Search Automation project.

## 🛠️ Features
- **Job Scraping**: LinkedIn, Indeed, RemoteOK, Naukri, Glassdoor, and more.
- **AI Scoring**: Ollama, Gemini, OpenAI integration.
- **Resume Generator**: PDF generation with Jinja2 and WeasyPrint.
- **Notifications**: Telegram bot and Email alerts.

## 🚀 Setup

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai/) (optional, for local AI)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/job-search-automation.git
    cd job-search-automation/backend
    ```

2.  **Create virtual environment**:
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

4.  **Configure Environment**:
    copy `.env.example` to `.env` and fill in your details:
    ```bash
    cp .env.example .env
    ```

### Running the Application

**Run the API Server**:
```bash
python -m uvicorn app.main:app --reload
```
Access Swagger UI at `http://localhost:8000/docs`.

**Run CLI Commands**:
The application also provides a CLI interface.
```bash
# List available commands
python -m app.cli --help

# Run all scrapers
python -m app.cli scrape

# Run full pipeline
python -m app.cli run
```

## 🧪 Testing

Run unit tests:
```bash
pytest
```
