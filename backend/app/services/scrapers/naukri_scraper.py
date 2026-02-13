"""
Naukri.com job scraper.
Targets India-based roles (₹20 LPA+).
"""

import logging
import random
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from backend.app.services.scrapers.base_scraper import BaseScraper
from backend.app.db.models import Job

logger = logging.getLogger(__name__)


class NaukriScraper(BaseScraper):
    """Scrapes Naukri.com public job search pages."""

    SOURCE_NAME = "naukri"
    BASE_URL = "https://www.naukri.com"

    def scrape(self, query: str, location: str = "") -> list[Job]:
        """Scrape Naukri job search results."""
        jobs = []

        # Only scrape for India location
        loc_lower = location.lower().strip()
        if loc_lower and "india" not in loc_lower and loc_lower not in [
            "mumbai", "bangalore", "bengaluru", "hyderabad", "pune",
            "delhi", "ncr", "chennai", "kolkata", "noida", "gurugram",
        ]:
            return jobs

        if not self._can_continue():
            return jobs

        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=self._get_random_user_agent(),
                    viewport={"width": 1366, "height": 768},
                )
                page = context.new_page()

                # Build Naukri search URL
                query_slug = query.lower().replace(" ", "-")
                url = f"{self.BASE_URL}/{query_slug}-jobs"
                if location and "india" not in loc_lower:
                    url += f"-in-{location.lower().replace(' ', '-')}"

                # Add experience filter
                url += f"?experience=5"

                logger.info(f"[Naukri] Loading: {url}")
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(4000)

                # Scroll
                for _ in range(2):
                    page.mouse.wheel(0, random.randint(300, 600))
                    page.wait_for_timeout(random.randint(600, 1200))

                html = page.content()
                self._increment_page()

                browser.close()

            # Parse
            soup = BeautifulSoup(html, "lxml")
            job_cards = soup.select(".srp-jobtuple-wrapper, .jobTupleHeader, article.jobTuple")

            for card in job_cards[:15]:
                try:
                    title_el = card.select_one(".title, a.title, .row1 .title")
                    company_el = card.select_one(".comp-name, .subTitle a, .companyInfo a")
                    location_el = card.select_one(".locWdth, .loc, .location .loc-icon")
                    salary_el = card.select_one(".sal, .salary, .ni-job-tuple-icon-srp-rupee")
                    link_el = card.select_one("a.title, a[href*='naukri.com']")

                    title = title_el.get_text(strip=True) if title_el else ""
                    company = company_el.get_text(strip=True) if company_el else ""
                    job_location = location_el.get_text(strip=True) if location_el else location
                    salary_text = salary_el.get_text(strip=True) if salary_el else ""
                    link = link_el.get("href", "") if link_el else ""

                    if not title or not link:
                        continue

                    jobs.append(Job(
                        title=title,
                        company=company,
                        location=job_location,
                        url=link,
                        source=self.SOURCE_NAME,
                        salary_text=salary_text,
                        description="",
                    ))
                except Exception as e:
                    logger.debug(f"[Naukri] Error parsing card: {e}")
                    continue

            logger.info(f"[Naukri] Found {len(jobs)} jobs for '{query}'")

        except ImportError:
            logger.error("Playwright not installed. Run: pip install playwright && playwright install")
        except Exception as e:
            logger.error(f"[Naukri] Scraping failed: {e}")

        return jobs
