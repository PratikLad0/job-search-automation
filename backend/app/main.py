import sys
import os
import asyncio

# Fix for Windows asyncio loop (required for Playwright) - MUST BE AT TOP
if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception as e:
        print(f"Failed to set ProactorEventLoopPolicy: {e}")

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the project root to sys.path to allow imports from the 'backend' package
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from backend.app.core.logger import logger
from backend.app.api.routers import (
    jobs, stats, scrapers, chat, generators, 
    profile, assistant, auth, company, emails
)

# Track routers in a dictionary for cleaner registration
ROUTERS = {
    'jobs': jobs,
    'stats': stats,
    'scrapers': scrapers,
    'chat': chat,
    'generators': generators,
    'profile': profile,
    'assistant': assistant,
    'company': company,
    'auth': auth,
    'emails': emails
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Log loop type for debugging
    loop = asyncio.get_running_loop()
    logger.info(f"Using event loop: {type(loop).__name__}")
    
    logger.info("🚀 Job Search Automation Backend Starting (Local Mode)...")
    
    # Start the Sequential Queue Worker
    try:
        from backend.app.core.queue_manager import queue_manager
        queue_manager.start_worker()
        logger.info("✅ Sequential Queue Worker initialized")
    except Exception as e:
        logger.error(f"❌ Failed to start Queue Worker: {e}")

    # Initialize Telegram Bot (Optional for local)
    try:
        from backend.app.services.notifications.telegram_bot import TelegramNotifier
        bot = TelegramNotifier()
        await bot.start()
        if bot._enabled:
            startup_msg = (
                "🚀 <b>Job Search Automation (Local) Started</b>\n\n"
                "🤖 <b>Available Commands:</b>\n"
                "/jobs - Show recent top matches\n"
                "/status - Check system status"
            )
            await bot.send_message(startup_msg)
    except Exception as e:
        logger.warning(f"Telegram bot not initialized: {e}")
        
    # Periodic Gmail Crawler Task
    async def periodic_gmail_check():
        from backend.app.services.email.gmail_crawler import run_gmail_crawler
        from backend.app.core import config
        while True:
            try:
                logger.info("🔍 Running periodic Gmail check (Local)...")
                await run_gmail_crawler()
            except Exception as e:
                logger.error(f"Error in periodic Gmail check: {e}")
            await asyncio.sleep(config.GMAIL_CHECK_INTERVAL)

    # Start the Gmail crawler task in the background
    asyncio.create_task(periodic_gmail_check())

    yield
    logger.info("🛑 Job Search Automation Backend Stopped.")

app = FastAPI(
    title="Job Search Automation API",
    description="Backend for Job Search Automation Tool",
    version="1.1.0",
    lifespan=lifespan
)

# Optimized CORS for Localhost
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"📥 {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"📤 {response.status_code} {request.url.path}")
    return response

# Standard Router Registration
logger.info("📦 Registering routers...")
for name, module in ROUTERS.items():
    if hasattr(module, 'router'):
        app.include_router(module.router)
        logger.info(f"  ✅ Router '{name}' registered")
    else:
        logger.warning(f"  ⚠️ Router '{name}' has no .router")

@app.get("/")
async def root():
    return {"message": "Job Search Automation API is running", "status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/debug/routes")
async def list_routes():
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods) if hasattr(route, "methods") else "WebSocket"
        })
    return routes

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
