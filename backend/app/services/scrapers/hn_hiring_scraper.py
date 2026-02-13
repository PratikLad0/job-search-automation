"""
HackerNews "Who's Hiring?" scraper.
Uses the free HN Algolia search API — no API key required.
Focus: High-quality tech jobs posted directly by companies.
API: https://hn.algolia.com/api
"""

import logging
import re
from html import unescape

import httpx

from backend.app.services.scrapers.base_scraper import BaseScraper
from backend.app.db.models import Job

logger = logging.getLogger(__name__)


class HNHiringScraper(BaseScraper):
    """
    Scrapes HackerNews monthly "Who's Hiring?" threads.
    These threads contain high-quality tech postings directly from hiring companies.
    Uses the free HN Algolia API — no browser needed.
    """

    SOURCE_NAME = "hn_hiring"
    SEARCH_URL = "https://hn.algolia.com/api/v1/search_by_date"

    def scrape(self, query: str, location: str = "") -> list[Job]:
        """Fetch jobs from HN Who's Hiring threads."""
        jobs = []

        if not self._can_continue():
            return jobs

        try:
            headers = {
                "User-Agent": self._get_random_user_agent(),
                "Accept": "application/json",
            }

            # Step 1: Find the latest "Who's Hiring?" thread
            thread_url = (
                f"{self.SEARCH_URL}"
                f"?query=%22Who+is+hiring%22"
                f"&tags=story,author_whoishiring"
                f"&hitsPerPage=1"
            )
            logger.info(f"[HN] Finding latest Who's Hiring thread...")
            response = httpx.get(thread_url, headers=headers, timeout=15)
            response.raise_for_status()
            thread_data = response.json()

            hits = thread_data.get("hits", [])
            if not hits:
                logger.warning("[HN] No Who's Hiring thread found")
                return jobs

            thread_id = hits[0].get("objectID", "")
            thread_title = hits[0].get("title", "")
            logger.info(f"[HN] Found thread: {thread_title} (ID: {thread_id})")

            # Step 2: Fetch comments (job posts) from the thread
            comments_url = (
                f"https://hn.algolia.com/api/v1/search"
                f"?tags=comment,story_{thread_id}"
                f"&hitsPerPage=200"
            )
            response = httpx.get(comments_url, headers=headers, timeout=15)
            response.raise_for_status()
            comments_data = response.json()
            self._increment_page()

            comments = comments_data.get("hits", [])
            logger.info(f"[HN] Found {len(comments)} job posts in thread")

            # Filter by query and location keywords
            query_lower = query.lower()
            query_words = query_lower.split()
            loc_lower = location.lower().strip() if location else ""

            for comment in comments:
                try:
                    text = comment.get("comment_text", "")
                    if not text or len(text) < 50:
                        continue

                    # Clean HTML
                    clean_text = unescape(re.sub(r'<[^>]+>', ' ', text))
                    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

                    # Match against query
                    text_lower = clean_text.lower()
                    if not any(word in text_lower for word in query_words):
                        continue

                    # Location filter
                    if loc_lower and loc_lower not in text_lower and loc_lower != "remote":
                        if "remote" not in text_lower:
                            continue

                    # Parse company and title from first line
                    # HN format: "Company Name | Role | Location | ..."
                    first_line = clean_text.split('\n')[0].split('.')[0]
                    parts = [p.strip() for p in first_line.split('|')]

                    company = parts[0][:80] if parts else "Unknown"
                    title = parts[1][:100] if len(parts) > 1 else f"Tech Role at {company}"
                    job_location = parts[2][:60] if len(parts) > 2 else location or "Check posting"

                    # Build unique URL for the comment
                    comment_id = comment.get("objectID", "")
                    job_url = f"https://news.ycombinator.com/item?id={comment_id}"

                    # Detect remote
                    is_remote = "remote" in text_lower
                    if is_remote and "remote" not in job_location.lower():
                        job_location = f"{job_location} / Remote"

                    jobs.append(Job(
                        title=title[:100],
                        company=company[:80],
                        location=job_location[:60],
                        url=job_url,
                        source=self.SOURCE_NAME,
                        description=clean_text[:2000],
                        job_type="remote" if is_remote else "",
                        posted_date=comment.get("created_at", ""),
                    ))
                except Exception as e:
                    logger.debug(f"[HN] Error parsing comment: {e}")
                    continue

            logger.info(f"[HN] Found {len(jobs)} matching jobs for '{query}'")

        except Exception as e:
            logger.error(f"[HN] API request failed: {e}")

        return jobs
