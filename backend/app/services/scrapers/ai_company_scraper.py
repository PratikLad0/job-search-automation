
import asyncio
import logging
import random
import urllib.parse
from datetime import datetime
from typing import List, Optional

from playwright.async_api import async_playwright, Page

from backend.app.core import config
from backend.app.db.models import Job, UserProfile
from backend.app.services.ai.provider import get_ai
from backend.app.services.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class AICompanyScraper(BaseScraper):
    """
    Scraper that uses Playwright to find career pages and AI (Gemini) to extract jobs.
    """
    SOURCE_NAME = "ai_company_scraper"

    # Domains to exclude (Aggregators, Social Media, Reviews)
    EXCLUDED_DOMAINS = [
        'linkedin.com', 'glassdoor.com', 'indeed.com', 'facebook.com',
        'naukri.com', 'foundit.in', 'shine.com', 'timesjobs.com',
        'ambitionbox.com', 'instahyre.com', 'freshersworld.com',
        'monsterindia.com', 'simplyhired.com', 'ziprecruiter.com',
        'twitter.com', 'instagram.com', 'youtube.com', 'wikipedia.org',
        'quora.com', 'reddit.com', 'tiktok.com', 'pinterest.com'
    ]

    def __init__(self):
        super().__init__()
        self.ai = get_ai()

    async def _discover_links_on_page(self, page: Page, keywords: List[str]) -> Optional[str]:
        """Crawl the current page for links matching specific keywords."""
        try:
            return await page.evaluate(f'''(keywords) => {{
                const anchors = Array.from(document.querySelectorAll('a'));
                for (const a of anchors) {{
                    const text = a.innerText.toLowerCase();
                    const href = a.href;
                    if (!href) continue;
                    
                    if (keywords.some(k => text.includes(k))) {{
                        return href;
                    }}
                }}
                return null;
            }}''', keywords)
        except Exception as e:
            logger.error(f"Error discovering links on page: {e}")
            return None

    async def _search_url_on_engine(self, page: Page, query: str, engine: str = "ddg") -> Optional[str]:
        """Human-like search helper for different engines."""
        try:
            if engine == "ddg":
                home_url = "https://duckduckgo.com/"
                input_selector = 'input[name="q"]'
                result_selector = 'a[data-testid="result-title-a"]'
            else: # bing
                home_url = "https://www.bing.com/"
                input_selector = 'input[name="q"]'
                result_selector = '#b_results .b_algo h2 a'

            logger.info(f"Searching {engine.upper()}: {query}")
            
            # 1. Visit Homepage
            await page.goto(home_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(random.uniform(1.5, 3.0))
            
            # 2. Type query naturally
            await page.click(input_selector)
            await page.type(input_selector, query, delay=random.uniform(50, 150))
            await asyncio.sleep(random.uniform(0.5, 1.0))
            await page.press(input_selector, "Enter")
            
            # 3. Wait for results
            try:
                # Use a combined search for results or common result containers
                await page.wait_for_selector(result_selector, timeout=15000)
                await asyncio.sleep(random.uniform(2.0, 4.0)) # Relax after search
            except:
                logger.warning(f"{engine.upper()} search results not found or blocked (Capturing Source).")
                content = await page.content()
                with open(f"debug_{engine}_blocked.html", "w", encoding="utf-8") as f:
                    f.write(content)
                return None
                
            links = await page.evaluate(f'''(sel) => {{
                const anchors = Array.from(document.querySelectorAll(sel));
                return anchors.map(a => a.href);
            }}''', result_selector)
            
            for url in links:
                if not url or not url.startswith("http"): continue
                clean_url = url.lower().replace("www.", "").replace("https://", "").replace("http://", "")
                if any(ex in clean_url for ex in self.EXCLUDED_DOMAINS):
                    continue
                return url
        except Exception as e:
            logger.debug(f"{engine.upper()} search failed: {e}")
        return None

    async def _discover_via_homepage(self, page: Page, company: str) -> Optional[str]:
        """Discovery Stage 2: Find company website first, then look for careers link."""
        # Try finding homepage
        official_site = await self._search_url_on_engine(page, company, "ddg")
        if not official_site:
            official_site = await self._search_url_on_engine(page, company, "bing")

        if official_site:
            try:
                logger.info(f"Visiting official site to find careers: {official_site}")
                await page.goto(official_site, wait_until="domcontentloaded", timeout=45000)
                await page.wait_for_timeout(3000)
                
                # Look for Career links
                career_link = await self._discover_links_on_page(page, ["career", "jobs", "join us", "work with us", "hiring"])
                if career_link:
                    logger.info(f"Found career link on homepage: {career_link}")
                    return career_link
                
                # Stage 3: Smart Guessing
                parsed = urllib.parse.urlparse(official_site)
                base_url = f"{parsed.scheme}://{parsed.netloc}"
                guesses = [f"{base_url}/careers", f"{base_url}/jobs", f"{base_url}/join-us"]
                
                for guess in guesses:
                    try:
                        logger.debug(f"Smart Guessing: {guess}")
                        response = await page.goto(guess, wait_until="domcontentloaded", timeout=15000)
                        if response and response.status < 400:
                            # Verify page content has "career" or "job"
                            text = await page.inner_text("body")
                            if "career" in text.lower() or "job" in text.lower():
                                logger.info(f"Confirmed career page via guessing: {guess}")
                                return guess
                    except: continue
            except Exception as e:
                logger.error(f"Error crawling homepage {official_site}: {e}")
        return None

    async def _search_company_career_page(self, page: Page, company: str, location: str) -> Optional[str]:
        """Enhanced discovery logic: Direct Search -> Homepage Crawl -> Smart Guess."""
        
        # 1. Try Direct Search (DDG then Bing)
        query = f'"{company}" careers {location}'.strip()
        career_url = await self._search_url_on_engine(page, query, "ddg")
        if not career_url:
            career_url = await self._search_url_on_engine(page, query, "bing")
            
        if career_url:
            return career_url
            
        # 2. Try Discovery via Homepage
        career_url = await self._discover_via_homepage(page, company)
        if career_url:
            return career_url
            
        logger.warning(f"Could not discover career page for {company}")
        return None

    async def _extract_jobs_with_ai(self, page_content: str, url: str, user_profile: Optional[UserProfile]) -> List[dict]:
        """Use AI to parse the HTML/Text content and extract jobs."""
        
        skills_text = ""
        if user_profile:
             try:
                 import json
                 skills = json.loads(user_profile.skills) if isinstance(user_profile.skills, str) else user_profile.skills
                 skills_text = f"User Skills: {', '.join(skills)}"
             except:
                 pass

        prompt = f"""
        You are an expert job scraper. I will provide the text content of a company's career page.
        Your task is to extract job listings that match the following criteria:
        1. Context: The user is looking for software engineering / tech roles.
        2. {skills_text}
        
        Extract a list of jobs. For each job, provide:
        - title
        - location
        - url (if relative, append to {url})
        - description (summary)
        
        Page Content (Truncated if too long):
        {page_content[:20000]}
        
        Return ONLY valid JSON array. If no relevant jobs are found, return [].
        Example: [{{ "title": "...", "location": "...", "url": "...", "description": "..." }}]
        """
        
        try:
            result = self.ai.generate_json(prompt)
            if isinstance(result, list):
                return result
            if isinstance(result, dict) and "jobs" in result:
                return result["jobs"]
            return []
        except Exception as e:
            logger.error(f"AI Extraction failed: {e}")
            return []

    async def scrape_company(self, company: str, locations: List[str], user_profile: Optional[UserProfile]) -> List[Job]:
        """Main method to crawl and scrape."""
        found_jobs = []
        
        async with async_playwright() as p:
            # Launch browser with enhanced stealth
            browser = await p.chromium.launch(
                headless=config.HEADLESS_AUTOMATION,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-infobars"
                ]
            )
            
            context = await browser.new_context(
                user_agent=self._get_random_user_agent(),
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
                timezone_id="Asia/Kolkata",
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                }
            )
            page = await context.new_page()

            # Stealth: Mask navigator.webdriver and other properties
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            """)

            try:
                search_locations = locations if locations else [""]
                
                for location in search_locations:
                    career_url = await self._search_company_career_page(page, company, location)
                    if not career_url:
                        # Final Attempt: Search for just the company name and look for careers
                        career_url = await self._discover_via_homepage(page, company)
                        
                    if not career_url:
                        continue
                    
                    logger.info(f"Scraping confirmed career page: {career_url}")
                    # Use a longer timeout and wait for network idle to ensure job boards load
                    await page.goto(career_url, wait_until="networkidle", timeout=60000)
                    await page.wait_for_timeout(5000) 

                    
                    content = await page.content()
                    for frame in page.frames:
                        try:
                            if frame.url != page.url:
                                content += f"\n<!-- Frame: {frame.url} -->\n" + await frame.content()
                        except: pass
                    
                    extracted_data = await self._extract_jobs_with_ai(content, career_url, user_profile)
                    
                    for item in extracted_data:
                        job_title = item.get("title", "Unknown Role")
                        job_url = item.get("url", career_url)
                        # Robust URL Join
                        job_url = urllib.parse.urljoin(career_url, job_url)

                        job = Job(
                            title=job_title,
                            company=company,
                            location=item.get("location", location),
                            url=job_url,
                            source="Company Website",
                            description=item.get("description", ""),
                            posted_date=datetime.now().strftime("%Y-%m-%d"),
                            status="scraped",
                            matched_skills=user_profile.skills if user_profile else "[]"
                        )
                        found_jobs.append(job)
                        
                    self._random_delay()
                    
            except Exception as e:
                logger.error(f"Error scraping {company}: {e}")
            finally:
                await browser.close()
                
        return found_jobs

    def scrape(self, query: str, location: str = "") -> list[Job]:
        raise NotImplementedError("Use scrape_company async method instead")
