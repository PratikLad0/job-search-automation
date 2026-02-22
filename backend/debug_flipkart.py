
import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.services.scrapers.ai_company_scraper import AICompanyScraper
from backend.app.db.models import UserProfile
import logging

logging.basicConfig(level=logging.INFO)

async def test_flipkart():
    print("🚀 Testing AICompanyScraper discovery for Flipkart...")
    scraper = AICompanyScraper()
    profile = UserProfile(skills='["Python", "React", "Node.js"]')
    
    # We'll use a slightly modified scraper for debugging locally
    from playwright.async_api import async_playwright
    from backend.app.core import config
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        # Discover
        url = await scraper._search_company_career_page(page, "Flipkart", "India")
        print(f"Discovered URL: {url}")
        
        if url:
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(5000)
            content = await page.content()
            
            with open("discovered_flipkart.html", "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"Saved content to discovered_flipkart.html (Length: {len(content)})")
            
            # Extract
            jobs = await scraper._extract_jobs_with_ai(content, url, profile)
            print(f"Jobs Found: {len(jobs)}")
            for j in jobs:
                print(f"- {j.get('title')}")
        
        await browser.close()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(test_flipkart())
