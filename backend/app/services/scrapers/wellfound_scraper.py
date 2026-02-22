"""
Wellfound (formerly AngelList) job scraper.
Uses Playwright for public listings.
Focus: Startup tech jobs — engineering, AI, full-stack, remote.
"""

import logging

from backend.app.services.scrapers.base_scraper import BaseScraper
from backend.app.db.models import Job

logger = logging.getLogger(__name__)


class WellfoundScraper(BaseScraper):
    """Scrapes Wellfound (AngelList) public job listings using Playwright."""

    SOURCE_NAME = "wellfound"
    BASE_URL = "https://wellfound.com"

    # Role slug map for tech positions
    ROLE_SLUGS = {
        "backend": "backend-engineer",
        "frontend": "frontend-engineer",
        "full-stack": "full-stack-engineer",
        "fullstack": "full-stack-engineer",
        "devops": "devops-engineer",
        "sde": "software-engineer",
        "software": "software-engineer",
        "data": "data-engineer",
        "machine learning": "machine-learning-engineer",
        "ai": "machine-learning-engineer",
        "platform": "software-engineer",
    }

    def _get_role_slug(self, query: str) -> str:
        """Map query to Wellfound role slug."""
        query_lower = query.lower()
        for key, slug in self.ROLE_SLUGS.items():
            if key in query_lower:
                return slug
        return "software-engineer"

    def scrape(self, query: str, location: str = "") -> list[Job]:
        """Scrape tech jobs from Wellfound."""
        jobs = []

        if not self._can_continue():
            return jobs

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.error("[Wellfound] Playwright not installed")
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
                role_slug = self._get_role_slug(query)
                search_url = f"{self.BASE_URL}/role/{role_slug}"
                if location:
                    loc_slug = location.lower().replace(" ", "-")
                    search_url += f"?locationSlug={loc_slug}"

                logger.info(f"[Wellfound] Searching: {search_url}")
                page.goto(search_url, wait_until="domcontentloaded")
                self._random_delay()
                self._increment_page()

                # Scroll to load more jobs
                for _ in range(2):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    self._random_delay()

                # Try multiple selectors
                selectors = [
                    '[data-test="StartupResult"]',
                    '.styles_result__rPRNG',
                    '.styles_component__UCLp3',
                    'div[class*="StartupResult"]',
                    '.job-listing-card',
                ]

                job_cards = []
                for selector in selectors:
                    try:
                        page.wait_for_selector(selector, timeout=5000)
                        job_cards = page.query_selector_all(selector)
                        if job_cards:
                            logger.info(f"[Wellfound] Found {len(job_cards)} cards with '{selector}'")
                            break
                    except:
                        continue

                if not job_cards:
                    # Fallback: Try to find any job links
                    try:
                        links = page.query_selector_all('a[href*="/jobs/"]')
                        for link in links[:20]:
                            href = link.get_attribute("href") or ""
                            text = link.inner_text().strip()
                            if text and href:
                                full_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                                jobs.append(Job(
                                    title=text[:100],
                                    company="",
                                    location=location or "Check posting",
                                    url=full_url,
                                    source=self.SOURCE_NAME,
                                    description="",
                                ))
                    except:
                        pass
                    browser.close()
                    logger.info(f"[Wellfound] Found {len(jobs)} jobs via link fallback")
                    return jobs

                for card in job_cards[:20]:
                    try:
                        # Company name
                        company_el = card.query_selector('h2, [class*="companyName"], a[href*="/company/"]')
                        company = company_el.inner_text().strip() if company_el else ""

                        # Job title(s) — a startup card may have multiple roles
                        title_els = card.query_selector_all('[class*="jobTitle"], [class*="role"], a[href*="/jobs/"]')
                        if not title_els:
                            title_els = [card.query_selector("h3, h4")]

                        for title_el in title_els:
                            if not title_el:
                                continue
                            title = title_el.inner_text().strip()
                            if not title:
                                continue

                            # URL
                            link_el = title_el if title_el.get_attribute("href") else title_el.query_selector("a")
                            job_url = ""
                            if link_el:
                                href = link_el.get_attribute("href") or ""
                                job_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

                            # Location
                            loc_el = card.query_selector('[class*="location"], [class*="Location"]')
                            job_location = loc_el.inner_text().strip() if loc_el else location or "Check posting"

                            # Salary
                            salary_el = card.query_selector('[class*="salary"], [class*="compensation"]')
                            salary = salary_el.inner_text().strip() if salary_el else ""

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
                        logger.debug(f"[Wellfound] Error parsing card: {e}")
                        continue

                browser.close()
                logger.info(f"[Wellfound] Found {len(jobs)} jobs for '{query}'")

        except Exception as e:
            logger.error(f"[Wellfound] Scraping failed: {e}")

        return jobs
