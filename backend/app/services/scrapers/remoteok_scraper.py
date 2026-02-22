"""
RemoteOK job scraper.
Uses the public JSON API — easiest and safest scraper.
"""

import logging

import httpx

from backend.app.services.scrapers.base_scraper import BaseScraper
from backend.app.db.models import Job

logger = logging.getLogger(__name__)


class RemoteOKScraper(BaseScraper):
    """Scrapes RemoteOK via their public JSON API. No browser needed."""

    SOURCE_NAME = "remoteok"
    API_URL = "https://remoteok.com/api"

    def scrape(self, query: str, location: str = "") -> list[Job]:
        """Fetch remote jobs from RemoteOK API."""
        jobs = []

        if not self._can_continue():
            return jobs

        try:
            headers = {
                "User-Agent": self._get_random_user_agent(),
                "Accept": "application/json",
            }

            response = httpx.get(self.API_URL, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            self._increment_page()

            # First item is metadata, skip it
            listings = data[1:] if len(data) > 1 else []

            # Filter by query keywords
            query_lower = query.lower()
            query_words = query_lower.split()

            for item in listings:
                try:
                    title = item.get("position", "")
                    company = item.get("company", "")
                    tags = item.get("tags", [])
                    description = item.get("description", "")
                    salary_min = item.get("salary_min", "")
                    salary_max = item.get("salary_max", "")
                    url = item.get("url", "")
                    date = item.get("date", "")

                    # Match against query
                    searchable = f"{title} {company} {' '.join(tags)} {description}".lower()
                    if not any(word in searchable for word in query_words):
                        continue

                    # Build salary text
                    salary_text = ""
                    if salary_min and salary_max:
                        salary_text = f"${salary_min:,} - ${salary_max:,}"
                    elif salary_min:
                        salary_text = f"${salary_min:,}+"

                    # Build full URL
                    full_url = f"https://remoteok.com{url}" if url.startswith("/") else url

                    jobs.append(Job(
                        title=title,
                        company=company,
                        location="Remote",
                        url=full_url,
                        source=self.SOURCE_NAME,
                        description=description[:2000],  # Truncate long descriptions
                        salary_text=salary_text,
                        job_type="remote",
                        posted_date=date,
                    ))
                except Exception as e:
                    logger.debug(f"[RemoteOK] Error parsing item: {e}")
                    continue

            logger.info(f"[RemoteOK] Found {len(jobs)} jobs matching '{query}'")

        except Exception as e:
            logger.error(f"[RemoteOK] API request failed: {e}")

        return jobs
