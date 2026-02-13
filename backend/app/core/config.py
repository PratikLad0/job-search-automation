"""
Central configuration for Job Search Automation.
Loads settings from .env file with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
# Load .env file
BASE_DIR = Path(__file__).parent.parent.parent # Points to backend/
load_dotenv(BASE_DIR / ".env")


def _csv_to_list(value: str) -> list[str]:
    """Convert comma-separated env string to list."""
    return [item.strip() for item in value.split(",") if item.strip()]


# ─── AI Provider Settings ──────────────────────────────────────
AI_PRIMARY_PROVIDER = os.getenv("AI_PRIMARY_PROVIDER", "ollama")
AI_BACKUP_PROVIDER = os.getenv("AI_BACKUP_PROVIDER", "gemini")

# Ollama
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# ─── Job Search Preferences ───────────────────────────────────
TARGET_ROLES = _csv_to_list(os.getenv(
    "TARGET_ROLES",
    "Backend Engineer,Software Development Engineer,SDE-2,Full Stack Developer,"
    "Software Engineer,Platform Engineer,AI Engineer,DevOps Engineer,"
    "Python Developer,Node.js Developer"
))

TARGET_LOCATIONS = _csv_to_list(os.getenv(
    "TARGET_LOCATIONS",
    "India,Germany,Netherlands,UK,Singapore,UAE,Remote"
))

MIN_MATCH_SCORE = int(os.getenv("MIN_MATCH_SCORE", "7"))
EXPERIENCE_YEARS = int(os.getenv("EXPERIENCE_YEARS", "5"))


# ─── Salary Filters ───────────────────────────────────────────
SALARY_FILTERS = {
    "INR": int(os.getenv("SALARY_MIN_INR", "2000000")),       # ₹20 LPA
    "EUR": int(os.getenv("SALARY_MIN_EUR", "65000")),          # €65K
    "GBP": int(os.getenv("SALARY_MIN_GBP", "60000")),          # £60K
    "SGD": int(os.getenv("SALARY_MIN_SGD", "100000")),          # SGD 100K
    "AED": int(os.getenv("SALARY_MIN_AED_MONTHLY", "25000")),  # AED 25K/mo
    "USD": int(os.getenv("SALARY_MIN_USD", "70000")),            # $70K
    "SEK": int(os.getenv("SALARY_MIN_SEK", "600000")),          # SEK 600K
}

# Map locations to expected currency
LOCATION_CURRENCY_MAP = {
    "india": "INR",
    "germany": "EUR",
    "netherlands": "EUR",
    "sweden": "SEK",
    "uk": "GBP",
    "singapore": "SGD",
    "uae": "AED",
    "remote": "USD",
    "usa": "USD",
}


# ─── Scraping Safety Settings ─────────────────────────────────
SCRAPE_DELAY_MIN = int(os.getenv("SCRAPE_DELAY_MIN", "3"))
SCRAPE_DELAY_MAX = int(os.getenv("SCRAPE_DELAY_MAX", "8"))
SCRAPE_MAX_PAGES = int(os.getenv("SCRAPE_MAX_PAGES", "5"))
SCRAPE_MAX_DAILY_RUNS = int(os.getenv("SCRAPE_MAX_DAILY_RUNS", "3"))

# User-agent pool for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0",
]



# ─── Email Settings ───────────────────────────────────────────
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")


# ─── Telegram ─────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


# ─── Paths ─────────────────────────────────────────────────────
OUTPUT_DIR = BASE_DIR / os.getenv("OUTPUT_DIR", "output")
DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
RESUMES_DIR = OUTPUT_DIR / "resumes"
COVER_LETTERS_DIR = OUTPUT_DIR / "cover_letters"
REPORTS_DIR = OUTPUT_DIR / "reports"
TEMPLATES_DIR = BASE_DIR / "app" / "services" / "generators" / "templates"
DB_PATH = DATA_DIR / "jobs.db"
CV_CACHE_PATH = DATA_DIR / "cv_data.json"

# Ensure directories exist
for _dir in [OUTPUT_DIR, DATA_DIR, RESUMES_DIR, COVER_LETTERS_DIR, REPORTS_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)


# ─── CV Path ──────────────────────────────────────────────────
CV_PDF_PATH = BASE_DIR / "PRATIK-LAD-CV.pdf"
CV_REF_PATH = Path(os.getenv("CV_REF_PATH", str(CV_PDF_PATH)))

