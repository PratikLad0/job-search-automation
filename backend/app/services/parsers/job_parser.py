"""
Job description parser.
Fetches full job descriptions from job URLs using Playwright.
"""

import logging
import random

from bs4 import BeautifulSoup

from backend.app.db.models import Job
from backend.app.core import config

logger = logging.getLogger(__name__)


def fetch_job_description(job: Job) -> str:
    """
    Fetch the full job description from a job URL.
    Uses Playwright to render JavaScript-heavy pages.
    """
    if job.description and len(job.description) > 200:
        return job.description

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=random.choice(config.USER_AGENTS),
                viewport={"width": 1366, "height": 768},
            )
            page = context.new_page()

            logger.debug(f"Fetching description from: {job.url}")
            page.goto(job.url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(3000)

            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "lxml")

        # Try common job description selectors
        description = ""
        selectors = [
            ".description__text",             # LinkedIn
            ".jobsearch-jobDescriptionText",  # Indeed
            ".job-description",                # Generic
            ".jd-container",                   # Naukri
            "#job-details",                    # Various
            "[class*='description']",          # Fallback
            "article",                         # Semantic
        ]

        for selector in selectors:
            el = soup.select_one(selector)
            if el:
                description = el.get_text(separator="\n", strip=True)
                if len(description) > 100:
                    break

        # Fallback: get main content
        if len(description) < 100:
            body = soup.select_one("main, .content, body")
            if body:
                description = body.get_text(separator="\n", strip=True)

        # Truncate very long descriptions
        return description[:5000] if description else ""

    except Exception as e:
        logger.error(f"Failed to fetch description for {job.url}: {e}")
        return job.description or ""


def enrich_jobs_with_descriptions(jobs: list[Job], max_fetch: int = 10) -> list[Job]:
    """
    Fetch full descriptions for jobs that don't have them.
    Rate-limited to avoid bans.
    """
    fetched = 0
    for job in jobs:
        if fetched >= max_fetch:
            logger.info(f"Reached max description fetches ({max_fetch})")
            break

        if not job.description or len(job.description) < 200:
            description = fetch_job_description(job)
            if description:
                job.description = description
                fetched += 1

            # Delay between fetches
            import time
            time.sleep(random.uniform(2, 5))

    logger.info(f"Enriched {fetched} jobs with descriptions")
    return jobs
