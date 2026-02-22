"""
Greenhouse public job board scraper.
Uses Greenhouse's public API — no authentication needed.
Focus: Jobs from top tech companies that use Greenhouse ATS.
Many top startups and tech companies use Greenhouse: Airbnb, Stripe, Coinbase, etc.
"""

import logging

import httpx

from backend.app.services.scrapers.base_scraper import BaseScraper
from backend.app.db.models import Job

logger = logging.getLogger(__name__)


class GreenhouseScraper(BaseScraper):
    """
    Scrapes jobs from companies using Greenhouse ATS.
    Queries multiple top tech companies' public job boards.
    No API key needed — Greenhouse GET endpoints are public.
    """

    SOURCE_NAME = "greenhouse"
    API_BASE = "https://boards-api.greenhouse.io/v1/boards"

    # Top tech companies using Greenhouse (board tokens)
    TECH_COMPANIES = [
        "stripe",
        "coinbase",
        "airbnb",
        "discord",
        "figma",
        "notion",
        "hashicorp",
        "gitlab",
        "twitch",
        "snapchat",
        "cloudflare",
        "databricks",
        "postman",
        "canva",
        "airtable",
        "rippling",
        "razorpay",
        "cred",
        "zomato",
    ]

    def scrape(self, query: str, location: str = "") -> list[Job]:
        """Fetch jobs from Greenhouse-powered company boards."""
        jobs = []

        if not self._can_continue():
            return jobs

        headers = {
            "User-Agent": self._get_random_user_agent(),
            "Accept": "application/json",
        }

        query_lower = query.lower()
        query_words = query_lower.split()
        loc_lower = location.lower().strip() if location else ""

        for company_slug in self.TECH_COMPANIES:
            if not self._can_continue():
                break

            try:
                url = f"{self.API_BASE}/{company_slug}/jobs"
                params = {"content": "true"}  # Include job description

                logger.debug(f"[Greenhouse] Fetching {company_slug}...")
                response = httpx.get(url, headers=headers, params=params, timeout=10)

                if response.status_code == 404:
                    logger.debug(f"[Greenhouse] Board not found: {company_slug}")
                    continue
                response.raise_for_status()

                data = response.json()
                listings = data.get("jobs", [])
                self._increment_page()

                for item in listings:
                    try:
                        title = item.get("title", "")
                        job_url = item.get("absolute_url", "")
                        updated_at = item.get("updated_at", "")
                        content = item.get("content", "")  # HTML description

                        # Location from metadata
                        job_location = ""
                        location_obj = item.get("location", {})
                        if location_obj:
                            job_location = location_obj.get("name", "")

                        # Clean HTML from content for searching
                        import re
                        clean_content = re.sub(r'<[^>]+>', ' ', content) if content else ""
                        clean_content = re.sub(r'\s+', ' ', clean_content).strip()

                        # Match against query
                        searchable = f"{title} {clean_content[:500]}".lower()
                        if not any(word in searchable for word in query_words):
                            continue

                        # Location filtering
                        if loc_lower:
                            loc_searchable = f"{job_location}".lower()
                            if loc_lower not in loc_searchable and loc_lower != "remote":
                                if "remote" not in loc_searchable:
                                    continue

                        # Detect remote
                        is_remote = "remote" in job_location.lower() if job_location else False

                        # Department info
                        departments = item.get("departments", [])
                        dept_names = [d.get("name", "") for d in departments]

                        jobs.append(Job(
                            title=title[:100],
                            company=company_slug.replace("-", " ").title(),
                            location=job_location[:60] or "Check posting",
                            url=job_url,
                            source=self.SOURCE_NAME,
                            description=clean_content[:2000],
                            job_type="remote" if is_remote else "",
                            posted_date=updated_at,
                        ))
                    except Exception as e:
                        logger.debug(f"[Greenhouse] Error parsing job: {e}")
                        continue

                # Small delay between companies
                self._random_delay()

            except Exception as e:
                logger.debug(f"[Greenhouse] Error for {company_slug}: {e}")
                continue

        logger.info(f"[Greenhouse] Found {len(jobs)} jobs matching '{query}'")
        return jobs
