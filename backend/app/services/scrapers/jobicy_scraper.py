"""
Jobicy remote jobs scraper.
Uses free public JSON API — no API key required.
Focus: Remote tech jobs with salary data.
Docs: https://jobicy.com/api/v2/remote-jobs
"""

import logging
import re

import httpx

from backend.app.services.scrapers.base_scraper import BaseScraper
from backend.app.db.models import Job

logger = logging.getLogger(__name__)


class JobicyScraper(BaseScraper):
    """Scrapes Jobicy via free public JSON API. No browser needed."""

    SOURCE_NAME = "jobicy"
    API_URL = "https://jobicy.com/api/v2/remote-jobs"

    # Industry tags for tech filtering
    TECH_INDUSTRIES = [
        "software-dev", "dev", "devops", "backend", "frontend",
        "data-science", "machine-learning", "engineering",
        "cloud", "sysadmin", "qa", "security",
    ]

    def scrape(self, query: str, location: str = "") -> list[Job]:
        """Fetch remote tech jobs from Jobicy API."""
        jobs = []

        if not self._can_continue():
            return jobs

        try:
            headers = {
                "User-Agent": self._get_random_user_agent(),
                "Accept": "application/json",
            }

            params = {
                "count": 50,
                "tag": "software-dev",  # Focus on software dev jobs
            }

            # Add geo filter if location is specified
            geo_map = {
                "india": "india",
                "germany": "germany",
                "uk": "uk",
                "netherlands": "netherlands",
                "singapore": "singapore",
                "uae": "uae",
                "usa": "usa",
                "remote": "anywhere",
            }
            if location:
                loc_key = location.lower().strip()
                for key, geo in geo_map.items():
                    if key in loc_key:
                        params["geo"] = geo
                        break

            url = f"{self.API_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
            logger.info(f"[Jobicy] Fetching: {url}")

            response = httpx.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            self._increment_page()

            listings = data.get("jobs", [])

            # Filter by query keywords
            query_lower = query.lower()
            query_words = query_lower.split()

            for item in listings:
                try:
                    title = item.get("jobTitle", "")
                    company = item.get("companyName", "")
                    job_geo = item.get("jobGeo", "Remote")
                    job_url = item.get("url", "")
                    job_type = item.get("jobType", [])
                    job_level = item.get("jobLevel", "")
                    excerpt = item.get("jobExcerpt", "")
                    pub_date = item.get("pubDate", "")
                    industry = item.get("jobIndustry", [])

                    # Salary data
                    salary_min = item.get("salaryMin", "")
                    salary_max = item.get("salaryMax", "")
                    salary_currency = item.get("salaryCurrency", "")

                    # Match against query
                    searchable = f"{title} {company} {excerpt} {' '.join(industry if isinstance(industry, list) else [industry])}".lower()
                    if not any(word in searchable for word in query_words):
                        continue

                    # Build salary text
                    salary_text = ""
                    if salary_min and salary_max:
                        salary_text = f"{salary_currency} {salary_min:,} - {salary_max:,}"
                    elif salary_min:
                        salary_text = f"{salary_currency} {salary_min:,}+"

                    # Build job type string
                    type_str = ", ".join(job_type) if isinstance(job_type, list) else str(job_type)

                    # Clean HTML from excerpt
                    clean_excerpt = re.sub(r'<[^>]+>', '', excerpt) if excerpt else ""

                    jobs.append(Job(
                        title=title,
                        company=company,
                        location=job_geo or "Remote",
                        url=job_url,
                        source=self.SOURCE_NAME,
                        description=clean_excerpt[:2000],
                        salary_text=salary_text,
                        job_type=type_str,
                        posted_date=pub_date,
                    ))
                except Exception as e:
                    logger.debug(f"[Jobicy] Error parsing item: {e}")
                    continue

            logger.info(f"[Jobicy] Found {len(jobs)} jobs matching '{query}'")

        except Exception as e:
            logger.error(f"[Jobicy] API request failed: {e}")

        return jobs
