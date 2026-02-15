
import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.services.scrapers.ai_company_scraper import AICompanyScraper
from backend.app.db.models import UserProfile

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_scraper():
    print("🚀 Starting Company Search Verification...")
    
    company = "Anthropic"
    locations = ["Remote"]
    
    # Mock User Profile
    profile = UserProfile(
        skills='["Python", "React", "AI", "Machine Learning"]'
    )
    
    scraper = AICompanyScraper()
    
    try:
        print(f"🔎 Searching for {company} jobs in {locations}...")
        jobs = await scraper.scrape_company(company, locations, profile)
        
        print(f"✅ Found {len(jobs)} jobs:")
        for job in jobs:
            print(f"  - {job.title} ({job.location})")
            print(f"    URL: {job.url}")
            print(f"    Desc: {job.description[:100]}...")
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(test_scraper())
