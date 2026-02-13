"""
Indeed job scraper.
Scrapes public search result pages.
"""

import logging
import random
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from backend.app.services.scrapers.base_scraper import BaseScraper
from backend.app.db.models import Job

logger = logging.getLogger(__name__)


class IndeedScraper(BaseScraper):
    """Scrapes Indeed public job search pages."""

    SOURCE_NAME = "indeed"

    # Indeed domains by region
    DOMAINS = {
        "india": "https://www.indeed.co.in",
        "germany": "https://de.indeed.com",
        "netherlands": "https://www.indeed.nl",
        "uk": "https://www.indeed.co.uk",
        "singapore": "https://www.indeed.com.sg",
        "uae": "https://www.indeed.ae",
        "remote": "https://www.indeed.com",
        "usa": "https://www.indeed.com",
    }

    def _get_domain(self, location: str) -> str:
        """Get the Indeed domain for a location."""
        loc_lower = location.lower().strip()
        for key, domain in self.DOMAINS.items():
            if key in loc_lower:
                return domain
        return "https://www.indeed.com"

    def scrape(self, query: str, location: str = "") -> list[Job]:
        """Scrape Indeed job search results."""
        jobs = []

        if not self._can_continue():
            return jobs

        try:
            from playwright.sync_api import sync_playwright

            domain = self._get_domain(location)

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=self._get_random_user_agent(),
                    viewport={"width": 1366, "height": 768},
                )
                page = context.new_page()

                url = f"{domain}/jobs?q={quote_plus(query)}&l={quote_plus(location)}"
                logger.info(f"[Indeed] Loading: {url}")
                page.goto(url, wait_until="domcontentloaded")

                page.wait_for_timeout(3000)

                # Human-like scrolling
                for _ in range(2):
                    page.mouse.wheel(0, random.randint(200, 500))
                    page.wait_for_timeout(random.randint(500, 1200))

                html = page.content()
                self._increment_page()

                browser.close()

            # Parse
            soup = BeautifulSoup(html, "lxml")
            job_cards = soup.select(".job_seen_beacon, .jobsearch-ResultsList > li, .result")

            for card in job_cards[:15]:
                try:
                    title_el = card.select_one("h2.jobTitle a, .jobTitle span, h2 a")
                    company_el = card.select_one("[data-testid='company-name'], .companyName, .company")
                    location_el = card.select_one("[data-testid='text-location'], .companyLocation, .location")

                    title = title_el.get_text(strip=True) if title_el else ""
                    company = company_el.get_text(strip=True) if company_el else ""
                    job_location = location_el.get_text(strip=True) if location_el else location

                    # Get link
                    link = ""
                    link_el = card.select_one("h2 a, .jobTitle a")
                    if link_el:
                        href = link_el.get("href", "")
                        if href.startswith("/"):
                            link = f"{domain}{href}"
                        else:
                            link = href

                    # Salary info
                    salary_el = card.select_one(".salary-snippet-container, .metadata.salary-snippet-container")
                    salary_text = salary_el.get_text(strip=True) if salary_el else ""

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
                    logger.debug(f"[Indeed] Error parsing card: {e}")
                    continue

            logger.info(f"[Indeed] Found {len(jobs)} jobs for '{query}' in '{location}'")

        except ImportError:
            logger.error("Playwright not installed. Run: pip install playwright && playwright install")
        except Exception as e:
            logger.error(f"[Indeed] Scraping failed: {e}")

        return jobs
