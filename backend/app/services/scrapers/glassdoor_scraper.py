"""
Glassdoor job scraper.
Uses Playwright for public job listing pages.
Focus: Multi-region job search with company ratings.
"""

import logging
import re

from backend.app.services.scrapers.base_scraper import BaseScraper
from backend.app.db.models import Job

logger = logging.getLogger(__name__)


class GlassdoorScraper(BaseScraper):
    """Scrapes Glassdoor public job listings using Playwright."""

    SOURCE_NAME = "glassdoor"

    # Region-specific domains
    DOMAINS = {
        "default": "https://www.glassdoor.com",
        "india": "https://www.glassdoor.co.in",
        "uk": "https://www.glassdoor.co.uk",
        "germany": "https://www.glassdoor.de",
        "singapore": "https://www.glassdoor.sg",
        "netherlands": "https://www.glassdoor.nl",
    }

    def _get_domain(self, location: str) -> str:
        """Get region-specific Glassdoor domain."""
        loc_lower = location.lower().strip() if location else ""
        for key, domain in self.DOMAINS.items():
            if key in loc_lower:
                return domain
        return self.DOMAINS["default"]

    def scrape(self, query: str, location: str = "") -> list[Job]:
        """Scrape jobs from Glassdoor public pages."""
        jobs = []

        if not self._can_continue():
            return jobs

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.error("[Glassdoor] Playwright not installed")
            return jobs

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=self._get_random_user_agent(),
                    viewport={"width": 1280, "height": 800},
                )
                page = context.new_page()
                page.set_default_timeout(15000)

                # Build search URL
                domain = self._get_domain(location)
                query_encoded = query.replace(" ", "-")
                search_url = f"{domain}/Job/jobs.htm?sc.keyword={query.replace(' ', '+')}"
                if location:
                    search_url += f"&locT=C&locKeyword={location.replace(' ', '+')}"

                logger.info(f"[Glassdoor] Searching: {search_url}")
                page.goto(search_url, wait_until="domcontentloaded")
                self._random_delay()
                self._increment_page()

                # Try multiple selectors for job cards
                selectors = [
                    'li[data-test="jobListing"]',
                    '.JobsList_jobListItem__wjTHv',
                    'li.react-job-listing',
                    '[data-test="job-link"]',
                    '.job-listing',
                ]

                job_cards = []
                for selector in selectors:
                    try:
                        page.wait_for_selector(selector, timeout=5000)
                        job_cards = page.query_selector_all(selector)
                        if job_cards:
                            logger.info(f"[Glassdoor] Found {len(job_cards)} cards with '{selector}'")
                            break
                    except:
                        continue

                if not job_cards:
                    logger.warning("[Glassdoor] No job cards found — page structure may have changed")
                    browser.close()
                    return jobs

                for card in job_cards[:20]:  # Limit to first 20
                    try:
                        # Extract title
                        title_el = card.query_selector('[data-test="job-title"], .JobCard_jobTitle__GLyJ1, a.jobLink')
                        title = title_el.inner_text().strip() if title_el else ""

                        # Extract company
                        company_el = card.query_selector('.EmployerProfile_companyName__9dmmw, .job-search-key-l2wjgv, .employerName')
                        company = company_el.inner_text().strip() if company_el else ""
                        # Clean rating from company name
                        company = re.sub(r'\d+\.?\d*$', '', company).strip()

                        # Extract location
                        loc_el = card.query_selector('[data-test="emp-location"], .JobCard_location__rCz3x, .job-search-key-9xj0id')
                        job_location = loc_el.inner_text().strip() if loc_el else location

                        # Extract URL
                        link_el = card.query_selector('a[data-test="job-title"], a.jobLink, a[href*="/job-listing/"]')
                        job_url = ""
                        if link_el:
                            href = link_el.get_attribute("href") or ""
                            if href.startswith("/"):
                                job_url = f"{domain}{href}"
                            elif href.startswith("http"):
                                job_url = href

                        # Extract salary if available
                        salary_el = card.query_selector('[data-test="detailSalary"], .JobCard_salaryEstimate__QpbTW')
                        salary = salary_el.inner_text().strip() if salary_el else ""

                        if title:
                            jobs.append(Job(
                                title=title[:100],
                                company=company[:80],
                                location=job_location[:60],
                                url=job_url,
                                source=self.SOURCE_NAME,
                                description="",
                                salary_text=salary,
                            ))
                    except Exception as e:
                        logger.debug(f"[Glassdoor] Error parsing card: {e}")
                        continue

                browser.close()
                logger.info(f"[Glassdoor] Found {len(jobs)} jobs for '{query}'")

        except Exception as e:
            logger.error(f"[Glassdoor] Scraping failed: {e}")

        return jobs
