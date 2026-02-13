"""
LinkedIn public job search page scraper.
Scrapes only public search results — NO login, NO auto-apply.
"""

import logging
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from backend.app.services.scrapers.base_scraper import BaseScraper
from backend.app.db.models import Job

logger = logging.getLogger(__name__)


class LinkedInScraper(BaseScraper):
    """Scrapes LinkedIn public job search pages (no authentication)."""

    SOURCE_NAME = "linkedin"
    BASE_URL = "https://www.linkedin.com/jobs/search/"

    def scrape(self, query: str, location: str = "") -> list[Job]:
        """Scrape LinkedIn public job search results."""
        jobs = []

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

                # Build search URL
                params = f"?keywords={quote_plus(query)}"
                if location:
                    params += f"&location={quote_plus(location)}"
                url = f"{self.BASE_URL}{params}"

                logger.info(f"[LinkedIn] Loading: {url}")
                page.goto(url, wait_until="domcontentloaded")

                # Wait for job listings to load
                page.wait_for_timeout(4000)

                # Scroll down to load more jobs
                for _ in range(3):
                    page.mouse.wheel(0, random.randint(300, 600))
                    page.wait_for_timeout(random.randint(800, 1500))

                html = page.content()
                self._increment_page()

                browser.close()

            # Parse the HTML
            soup = BeautifulSoup(html, "lxml")
            job_cards = soup.select(".base-search-card, .job-search-card")

            for card in job_cards[:15]:  # Limit to 15 per page
                try:
                    title_el = card.select_one("h3, .base-search-card__title")
                    company_el = card.select_one("h4, .base-search-card__subtitle")
                    location_el = card.select_one(".job-search-card__location")
                    link_el = card.select_one("a")

                    title = title_el.get_text(strip=True) if title_el else ""
                    company = company_el.get_text(strip=True) if company_el else ""
                    job_location = location_el.get_text(strip=True) if location_el else location
                    link = link_el.get("href", "") if link_el else ""

                    if not title or not link:
                        continue

                    # Clean up the URL
                    if link and "?" in link:
                        link = link.split("?")[0]

                    jobs.append(Job(
                        title=title,
                        company=company,
                        location=job_location,
                        url=link,
                        source=self.SOURCE_NAME,
                        description="",  # Populated later by parser
                    ))
                except Exception as e:
                    logger.debug(f"[LinkedIn] Error parsing card: {e}")
                    continue

            logger.info(f"[LinkedIn] Found {len(jobs)} jobs for '{query}' in '{location}'")

        except ImportError:
            logger.error("Playwright not installed. Run: pip install playwright && playwright install")
        except Exception as e:
            logger.error(f"[LinkedIn] Scraping failed: {e}")

        return jobs


# Need the import for random scrolling
import random
