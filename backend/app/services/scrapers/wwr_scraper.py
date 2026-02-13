"""
WeWorkRemotely job scraper.
Uses the free public JSON API — no API key required for reading.
Focus: High-quality remote tech jobs, one of the largest remote-only boards.
API: https://weworkremotely.com/api/v1/remote-jobs
"""

import logging
import re
from html import unescape

import httpx

from backend.app.services.scrapers.base_scraper import BaseScraper
from backend.app.db.models import Job

logger = logging.getLogger(__name__)


class WWRScraper(BaseScraper):
    """Scrapes WeWorkRemotely via free JSON API. No browser needed."""

    SOURCE_NAME = "weworkremotely"
    BASE_URL = "https://weworkremotely.com"

    # Category-specific RSS feeds (as JSON isn't category-filtered)
    CATEGORY_FEEDS = {
        "programming": f"{BASE_URL}/categories/remote-full-stack-programming-jobs.json",
        "backend": f"{BASE_URL}/categories/remote-back-end-programming-jobs.json",
        "frontend": f"{BASE_URL}/categories/remote-front-end-programming-jobs.json",
        "devops": f"{BASE_URL}/categories/remote-devops-sysadmin-jobs.json",
        "data": f"{BASE_URL}/categories/remote-data-jobs.json",
    }

    def scrape(self, query: str, location: str = "") -> list[Job]:
        """Fetch remote jobs from WeWorkRemotely."""
        jobs = []

        if not self._can_continue():
            return jobs

        try:
            headers = {
                "User-Agent": self._get_random_user_agent(),
                "Accept": "application/json",
            }

            # Try main endpoint first
            urls_to_try = [
                f"{self.BASE_URL}/api/v1/remote-jobs",
            ]

            # Add category feeds relevant to query
            query_lower = query.lower()
            for cat_key, cat_url in self.CATEGORY_FEEDS.items():
                if cat_key in query_lower or query_lower in ["software", "engineer", "developer", "sde"]:
                    urls_to_try.append(cat_url)

            all_listings = []
            seen_urls = set()

            for url in urls_to_try:
                if not self._can_continue():
                    break

                try:
                    logger.info(f"[WWR] Fetching: {url}")
                    response = httpx.get(url, headers=headers, timeout=15)
                    response.raise_for_status()
                    data = response.json()
                    self._increment_page()

                    # Handle different response formats
                    listings = []
                    if isinstance(data, list):
                        listings = data
                    elif isinstance(data, dict):
                        listings = data.get("jobs", data.get("data", []))

                    for item in listings:
                        item_url = item.get("url", "")
                        if item_url not in seen_urls:
                            seen_urls.add(item_url)
                            all_listings.append(item)

                    self._random_delay()
                except Exception as e:
                    logger.debug(f"[WWR] Error fetching {url}: {e}")
                    continue

            # Filter by query keywords
            query_words = query_lower.split()

            for item in all_listings:
                try:
                    title = item.get("title", "")
                    company = item.get("company_name", item.get("company", ""))
                    job_url = item.get("url", "")
                    description = item.get("description", item.get("body", ""))
                    category = item.get("category", "")
                    posted_date = item.get("published_at", item.get("date", ""))

                    # Make absolute URL
                    if job_url and not job_url.startswith("http"):
                        job_url = f"{self.BASE_URL}{job_url}"

                    # Clean HTML from description
                    clean_desc = unescape(re.sub(r'<[^>]+>', ' ', description)) if description else ""
                    clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()

                    # Match against query
                    searchable = f"{title} {company} {category} {clean_desc[:500]}".lower()
                    if not any(word in searchable for word in query_words):
                        continue

                    jobs.append(Job(
                        title=title[:100],
                        company=company[:80],
                        location="Remote",
                        url=job_url,
                        source=self.SOURCE_NAME,
                        description=clean_desc[:2000],
                        job_type="remote",
                        posted_date=str(posted_date),
                    ))
                except Exception as e:
                    logger.debug(f"[WWR] Error parsing item: {e}")
                    continue

            logger.info(f"[WWR] Found {len(jobs)} jobs matching '{query}'")

        except Exception as e:
            logger.error(f"[WWR] Scraping failed: {e}")

        return jobs
