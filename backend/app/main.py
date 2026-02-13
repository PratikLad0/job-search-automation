import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the project root to sys.path to allow imports from the 'backend' package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.core.logger import logger

try:
    from backend.app.api.routers import jobs, stats, scrapers, chat, generators, profile
    logger.info("✅ All routers successfully imported")
except ImportError as e:
    logger.error(f"❌ Critical Import Error: {e}")
    # Don't fail here, let include_router handle it safely
    import traceback
    logger.debug(traceback.format_exc())

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Job Search Automation Backend Starting...")
    
    # Initialize Telegram Bot
    try:
        from backend.app.services.notifications.telegram_bot import TelegramNotifier
        bot = TelegramNotifier()
        if bot._enabled:
            await bot.send_message("🚀 <b>Job Search Automation Backend Scraper Started</b>")
    except Exception as e:
        logger.error(f"Failed to send startup notification: {e}")
        
    yield
    logger.info("🛑 Job Search Automation Backend Stopping...")

app = FastAPI(
    title="Job Search Automation API",
    description="Backend for Job Search Automation Tool",
    version="1.0.0",
    lifespan=lifespan
)

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:3000",
]

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"📥 {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"📤 {response.status_code} {request.url.path}")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    logger.info("📦 Loading routers...")
    if 'jobs' in locals():
        app.include_router(jobs.router)
    if 'stats' in locals():
        app.include_router(stats.router)
    if 'scrapers' in locals():
        app.include_router(scrapers.router)
    if 'chat' in locals():
        app.include_router(chat.router)
    if 'generators' in locals():
        app.include_router(generators.router)
    if 'profile' in locals():
        app.include_router(profile.router)
    logger.info("✅ Routers check complete")
except Exception as e:
    logger.error(f"❌ Error including routers: {e}")
    # Print which ones are defined
    for name in ["jobs", "stats", "scrapers", "chat", "generators", "profile"]:
        if name in locals() or name in globals():
            print(f"  - {name} is defined")
        else:
            print(f"  - {name} is NOT defined")

@app.get("/")
async def root():
    return {"message": "Job Search Automation API is running", "status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
