"""
Adzuna job scraper.
Uses Adzuna REST API (free tier — requires app_id + app_key from env).
Focus: Multi-country job search — UK, Germany, India, Singapore, and more.
Register at https://developer.adzuna.com/ for free API credentials.
"""

import logging
import os

import httpx

from backend.app.services.scrapers.base_scraper import BaseScraper
from backend.app.db.models import Job

logger = logging.getLogger(__name__)


class AdzunaScraper(BaseScraper):
    """Scrapes Adzuna via free-tier REST API. Multi-region support."""

    SOURCE_NAME = "adzuna"
    API_BASE = "https://api.adzuna.com/v1/api/jobs"

    # Adzuna country codes
    COUNTRY_MAP = {
        "uk": "gb",
        "united kingdom": "gb",
        "germany": "de",
        "netherlands": "nl",
        "india": "in",
        "singapore": "sg",
        "usa": "us",
        "us": "us",
        "canada": "ca",
        "australia": "au",
        "france": "fr",
        "brazil": "br",
        "south africa": "za",
    }

    def _get_country_code(self, location: str) -> str:
        """Map location to Adzuna country code."""
        if not location:
            return "gb"  # Default to UK
        loc_lower = location.lower().strip()
        for key, code in self.COUNTRY_MAP.items():
            if key in loc_lower:
                return code
        return "gb"

    def scrape(self, query: str, location: str = "") -> list[Job]:
        """Fetch jobs from Adzuna API (multi-country)."""
        jobs = []

        app_id = os.getenv("ADZUNA_APP_ID", "")
        app_key = os.getenv("ADZUNA_APP_KEY", "")

        if not app_id or not app_key:
            logger.warning("[Adzuna] ADZUNA_APP_ID / ADZUNA_APP_KEY not set — skipping (get free at developer.adzuna.com)")
            return jobs

        if not self._can_continue():
            return jobs

        # Determine which countries to search
        countries = []
        if location:
            code = self._get_country_code(location)
            countries = [code]
        else:
            # Search key target countries
            countries = ["gb", "de", "in", "sg"]

        try:
            headers = {
                "User-Agent": self._get_random_user_agent(),
                "Accept": "application/json",
            }

            for country in countries:
                if not self._can_continue():
                    break

                page = 1
                max_pages = 2

                while page <= max_pages and self._can_continue():
                    url = f"{self.API_BASE}/{country}/search/{page}"
                    params = {
                        "app_id": app_id,
                        "app_key": app_key,
                        "what": query,
                        "results_per_page": 20,
                        "content-type": "application/json",
                        "category": "it-jobs",
                    }

                    # Add location within country if specified
                    if location and location.lower() not in ["uk", "germany", "india", "singapore", "usa", "remote"]:
                        params["where"] = location

                    logger.info(f"[Adzuna] Searching {country.upper()} page {page}...")

                    response = httpx.get(url, headers=headers, params=params, timeout=15)
                    response.raise_for_status()
                    data = response.json()
                    self._increment_page()

                    results = data.get("results", [])
                    if not results:
                        break

                    for item in results:
                        try:
                            title = item.get("title", "")
                            # Clean HTML from title
                            import re
                            title = re.sub(r'<[^>]+>', '', title).strip()

                            company_obj = item.get("company", {})
                            company = company_obj.get("display_name", "") if isinstance(company_obj, dict) else str(company_obj)

                            location_obj = item.get("location", {})
                            areas = location_obj.get("area", []) if isinstance(location_obj, dict) else []
                            job_location = ", ".join(areas[-2:]) if areas else country.upper()

                            job_url = item.get("redirect_url", "")
                            description = item.get("description", "")

                            # Salary info
                            salary_min = item.get("salary_min")
                            salary_max = item.get("salary_max")
                            salary_text = ""
                            if salary_min and salary_max:
                                salary_text = f"£{int(salary_min):,} - £{int(salary_max):,}" if country == "gb" else f"{int(salary_min):,} - {int(salary_max):,}"
                            elif salary_min:
                                salary_text = f"From {int(salary_min):,}"

                            contract_type = item.get("contract_type", "")
                            created = item.get("created", "")

                            jobs.append(Job(
                                title=title[:100],
                                company=company[:80],
                                location=job_location[:60],
                                url=job_url,
                                source=self.SOURCE_NAME,
                                description=(description or "")[:2000],
                                salary_text=salary_text,
                                job_type=contract_type,
                                posted_date=created,
                            ))
                        except Exception as e:
                            logger.debug(f"[Adzuna] Error parsing: {e}")
                            continue

                    page += 1
                    self._random_delay()

            logger.info(f"[Adzuna] Found {len(jobs)} jobs matching '{query}'")

        except Exception as e:
            logger.error(f"[Adzuna] API request failed: {e}")

        return jobs
