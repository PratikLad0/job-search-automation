"""
Arbeitnow job scraper.
Uses free public JSON API — no API key required.
Focus: European tech jobs, remote jobs, visa sponsorship.
Docs: https://www.arbeitnow.com/api/job-board-api
"""

import logging
from urllib.parse import urlencode

import httpx

from backend.app.services.scrapers.base_scraper import BaseScraper
from backend.app.db.models import Job

logger = logging.getLogger(__name__)


class ArbeitnowScraper(BaseScraper):
    """Scrapes Arbeitnow via free public JSON API. No browser needed."""

    SOURCE_NAME = "arbeitnow"
    API_URL = "https://www.arbeitnow.com/api/job-board-api"

    def scrape(self, query: str, location: str = "") -> list[Job]:
        """Fetch tech jobs from Arbeitnow API."""
        jobs = []

        if not self._can_continue():
            return jobs

        try:
            headers = {
                "User-Agent": self._get_random_user_agent(),
                "Accept": "application/json",
            }

            # Arbeitnow API supports pagination
            page = 1
            max_pages = 3

            while page <= max_pages and self._can_continue():
                url = f"{self.API_URL}?page={page}"
                logger.info(f"[Arbeitnow] Fetching page {page}: {url}")

                response = httpx.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                data = response.json()
                self._increment_page()

                listings = data.get("data", [])
                if not listings:
                    break

                # Filter by query keywords
                query_lower = query.lower()
                query_words = query_lower.split()

                for item in listings:
                    try:
                        title = item.get("title", "")
                        company = item.get("company_name", "")
                        job_location = item.get("location", "")
                        remote = item.get("remote", False)
                        tags = item.get("tags", [])
                        description = item.get("description", "")
                        url_slug = item.get("slug", "")
                        created_at = item.get("created_at", "")

                        # Match against query
                        searchable = f"{title} {company} {' '.join(tags)} {description}".lower()
                        if not any(word in searchable for word in query_words):
                            continue

                        # Location matching
                        if location:
                            loc_lower = location.lower()
                            loc_searchable = f"{job_location} {'remote' if remote else ''}".lower()
                            if loc_lower not in loc_searchable and loc_lower != "remote":
                                continue

                        # Build job URL
                        full_url = f"https://www.arbeitnow.com/view/{url_slug}" if url_slug else ""

                        # Location string
                        loc_str = job_location or ""
                        if remote:
                            loc_str = f"{loc_str} (Remote)" if loc_str else "Remote"

                        jobs.append(Job(
                            title=title,
                            company=company,
                            location=loc_str,
                            url=full_url,
                            source=self.SOURCE_NAME,
                            description=description[:2000],
                            job_type="remote" if remote else "",
                            posted_date=str(created_at),
                        ))
                    except Exception as e:
                        logger.debug(f"[Arbeitnow] Error parsing item: {e}")
                        continue

                # Check if there are more pages
                links = data.get("links", {})
                if not links.get("next"):
                    break
                page += 1
                self._random_delay()

            logger.info(f"[Arbeitnow] Found {len(jobs)} jobs matching '{query}'")

        except Exception as e:
            logger.error(f"[Arbeitnow] API request failed: {e}")

        return jobs
