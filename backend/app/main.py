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

# Track successfully imported routers in a dictionary to avoid scope issues
ROUTERS = {}

# Try to import routers
try:
    # First try relative to the current app structure
    try:
        from app.api.routers import jobs, stats, scrapers, chat, generators, profile, assistant, auth, company
    except ImportError:
        # Fallback to absolute backend import
        from backend.app.api.routers import jobs, stats, scrapers, chat, generators, profile, assistant, auth, company
    
    # Success! Add to our map
    ROUTERS['jobs'] = jobs
    ROUTERS['stats'] = stats
    ROUTERS['scrapers'] = scrapers
    ROUTERS['chat'] = chat
    ROUTERS['generators'] = generators
    ROUTERS['profile'] = profile
    ROUTERS['assistant'] = assistant
    ROUTERS['company'] = company
    ROUTERS['auth'] = auth
    
    # Try to import emails router (newly added)
    try:
        from app.api.routers import emails
        ROUTERS['emails'] = emails
    except ImportError:
         try:
            from backend.app.api.routers import emails
            ROUTERS['emails'] = emails
         except ImportError:
            logger.warning("Could not import emails router")
    
    logger.info("✅ All routers successfully imported")
except ImportError as e:
    logger.error(f"❌ Critical Import Error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Log loop type for debugging
    loop = asyncio.get_running_loop()
    logger.info(f"Using event loop: {type(loop).__name__}")
    
    logger.info("🚀 Job Search Automation Backend Starting...")
    
    # Start the Sequential Queue Worker
    try:
        from backend.app.core.queue_manager import queue_manager
        queue_manager.start_worker()
        logger.info("✅ Sequential Queue Worker initialized")
    except Exception as e:
        logger.error(f"❌ Failed to start Queue Worker: {e}")

    # Initialize Telegram Bot
    try:
        from backend.app.services.notifications.telegram_bot import TelegramNotifier
        bot = TelegramNotifier()
        await bot.start()
        if bot._enabled:
            startup_msg = (
                "🚀 <b>Job Search Automation Backend Scraper Started</b>\n\n"
                "🤖 <b>Available Commands:</b>\n"
                "/jobs - Show recent top matches\n"
                "/status - Check system status\n"
                "/help - Show all commands"
            )
            await bot.send_message(startup_msg)
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}")
        
    # Periodic Gmail Crawler Task
    async def periodic_gmail_check():
        from backend.app.services.email.gmail_crawler import run_gmail_crawler
        from backend.app.core import config
        while True:
            try:
                logger.info("🔍 Running periodic Gmail check...")
                await run_gmail_crawler()
            except Exception as e:
                logger.error(f"Error in periodic Gmail check: {e}")
            await asyncio.sleep(config.GMAIL_CHECK_INTERVAL)

    # Start the Gmail crawler task in the background
    asyncio.create_task(periodic_gmail_check())

    yield
    logger.info("🛑 Job Search Automation Backend Stopping...")
    try:
        from backend.app.services.notifications.telegram_bot import TelegramNotifier
        bot = TelegramNotifier()
        await bot.stop()
    except Exception as e:
        logger.error(f"Failed to stop Telegram bot: {e}")

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    logger.info("📦 Registering routers...")
    registered_count = 0
    for name, module in ROUTERS.items():
        if module and hasattr(module, 'router'):
            app.include_router(module.router)
            # Add WebSocket route explicitly if it's the assistant
            if name == "assistant":
                 logger.info(f"  ✅ Router '{name}' registered with WebSocket /assistant/ws")
            else:
                 logger.info(f"  ✅ Router '{name}' registered")
            registered_count += 1
        else:
            logger.warning(f"  ⚠️ Router '{name}' NOT found or has no .router")
            
    logger.info(f"✅ Route registration complete. {registered_count} routers active: {list(ROUTERS.keys())}")
except Exception as e:
    logger.error(f"❌ Unexpected error during router registration: {e}")

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
