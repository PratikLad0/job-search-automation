"""
Findwork.dev job scraper.
Uses free REST API (requires free API key from env).
Focus: Developer and design jobs aggregated from multiple sources.
API: https://findwork.dev/api/jobs/
"""

import logging
import os

import httpx

from backend.app.services.scrapers.base_scraper import BaseScraper
from backend.app.db.models import Job

logger = logging.getLogger(__name__)


class FindworkScraper(BaseScraper):
    """Scrapes Findwork.dev via free REST API. Requires free API key."""

    SOURCE_NAME = "findwork"
    API_URL = "https://findwork.dev/api/jobs/"

    def scrape(self, query: str, location: str = "") -> list[Job]:
        """Fetch developer jobs from Findwork API."""
        jobs = []

        api_key = os.getenv("FINDWORK_API_KEY", "")
        if not api_key:
            logger.warning("[Findwork] FINDWORK_API_KEY not set — skipping (get free key at findwork.dev)")
            return jobs

        if not self._can_continue():
            return jobs

        try:
            headers = {
                "Authorization": f"Token {api_key}",
                "User-Agent": self._get_random_user_agent(),
                "Accept": "application/json",
            }

            params = {
                "search": query,
                "order_by": "-date_posted",
            }

            # Apply location filter
            if location:
                loc_lower = location.lower().strip()
                if loc_lower == "remote":
                    params["remote"] = "true"
                else:
                    params["location"] = location

            url = self.API_URL
            page = 0
            max_pages = 3

            while url and page < max_pages and self._can_continue():
                logger.info(f"[Findwork] Fetching page {page + 1}...")

                response = httpx.get(url, headers=headers, params=params if page == 0 else None, timeout=15)
                response.raise_for_status()
                data = response.json()
                self._increment_page()

                results = data.get("results", [])
                if not results:
                    break

                for item in results:
                    try:
                        title = item.get("role", "")
                        company = item.get("company_name", "")
                        job_location = item.get("location", "")
                        job_url = item.get("url", "")
                        description = item.get("text", item.get("description", ""))
                        remote = item.get("remote", False)
                        keywords = item.get("keywords", [])
                        date_posted = item.get("date_posted", "")
                        employment_type = item.get("employment_type", "")

                        # Location enrichment
                        loc_str = job_location or ""
                        if remote:
                            loc_str = f"{loc_str} (Remote)" if loc_str else "Remote"

                        # Build skills text from keywords
                        skills_text = ", ".join(keywords) if keywords else ""

                        jobs.append(Job(
                            title=title[:100],
                            company=company[:80],
                            location=loc_str[:60],
                            url=job_url,
                            source=self.SOURCE_NAME,
                            description=(description or "")[:2000],
                            job_type=employment_type or ("remote" if remote else ""),
                            posted_date=date_posted,
                        ))
                    except Exception as e:
                        logger.debug(f"[Findwork] Error parsing item: {e}")
                        continue

                # Pagination
                url = data.get("next")
                page += 1
                if url:
                    params = {}  # next URL includes params
                    self._random_delay()

            logger.info(f"[Findwork] Found {len(jobs)} jobs matching '{query}'")

        except Exception as e:
            logger.error(f"[Findwork] API request failed: {e}")

        return jobs
