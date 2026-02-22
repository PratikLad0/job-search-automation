"""
Abstract base class for all job board scrapers.
Implements anti-ban safety mechanisms.
"""

import random
import time
import logging
from abc import ABC, abstractmethod

from backend.app.db.models import Job
from backend.app.core import config

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Base class for all job scrapers.
    Provides anti-ban safety: delays, user-agent rotation, rate limiting.
    """

    SOURCE_NAME: str = "unknown"

    def __init__(self):
        self._page_count = 0
        self._max_pages = config.SCRAPE_MAX_PAGES

    def _random_delay(self):
        """Wait a random time between requests to avoid detection."""
        delay = random.uniform(config.SCRAPE_DELAY_MIN, config.SCRAPE_DELAY_MAX)
        logger.debug(f"Waiting {delay:.1f}s before next request...")
        time.sleep(delay)

    def _get_random_user_agent(self) -> str:
        """Get a random user-agent from the pool."""
        return random.choice(config.USER_AGENTS)

    def _can_continue(self) -> bool:
        """Check if we've hit the page limit."""
        if self._page_count >= self._max_pages:
            logger.info(
                f"[{self.SOURCE_NAME}] Reached max pages ({self._max_pages}). Stopping."
            )
            return False
        return True

    def _increment_page(self):
        """Track pages scraped."""
        self._page_count += 1
        logger.debug(f"[{self.SOURCE_NAME}] Page {self._page_count}/{self._max_pages}")

    @abstractmethod
    def scrape(self, query: str, location: str = "") -> list[Job]:
        """
        Scrape jobs for a given query and location.
        Must be implemented by each scraper.
        Returns a list of Job objects.
        """
        pass

    def scrape_all(
        self,
        queries: list[str] | None = None,
        locations: list[str] | None = None,
    ) -> list[Job]:
        """
        Scrape multiple queries x locations.
        Uses target roles/locations from config if not specified.
        """
        queries = queries or config.TARGET_ROLES
        locations = locations or config.TARGET_LOCATIONS

        all_jobs = []
        seen_urls = set()

        for query in queries:
            for location in locations:
                if not self._can_continue():
                    break

                logger.info(f"[{self.SOURCE_NAME}] Scraping: '{query}' in '{location}'")
                try:
                    jobs = self.scrape(query, location)
                    for job in jobs:
                        if job.url and job.url not in seen_urls:
                            seen_urls.add(job.url)
                            all_jobs.append(job)
                except Exception as e:
                    logger.error(f"[{self.SOURCE_NAME}] Error scraping '{query}' in '{location}': {e}")

                self._random_delay()

        logger.info(f"[{self.SOURCE_NAME}] Total unique jobs found: {len(all_jobs)}")
        return all_jobs
