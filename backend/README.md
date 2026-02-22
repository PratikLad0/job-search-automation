# 🐍 Job Search Automation - Backend

Python-based API, scrapers, and AI engine for the Job Search Automation project.

## 🛠️ Components

### 1. API Services (`app/api`)
- **Routers**: Modular endpoints for Jobs, Auth, Profile, Assistant, Emails, and Company Search.
- **WebSocket**: Real-time communication for the AI Assistant.

### 2. Scrapers (`app/services/scrapers`)
- **Playwright Scraper**: Handles dynamic sites (LinkedIn, Glassdoor) using browser automation.
- **AI Company Scraper**: targeted searching of company career pages using LLM extraction.
- **BeautifulSoup**: Fallback for static content.

### 3. AI Engine (`app/services/ai`)
- **LLM Provider**: Configurable to use **Ollama** (local) or **Gemini/OpenAI** (cloud).
- **Extraction**: JSON mode used for structured job data extraction.
- **Generation**: Resume and Cover Letter tailoring.

### 4. Background Workers
- **Queue Manager**: Sequential processing of resource-intensive tasks (Scraping, AI Generation) to prevent server overload.

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

**Recommended (Windows & Linux)**:
Use the `run.py` script. This ensures the correct asyncio event loop policy is applied (critical for Playwright on Windows).

```bash
python run.py
```

Access Swagger UI at `http://localhost:8000/docs`.

### CLI Commands
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
