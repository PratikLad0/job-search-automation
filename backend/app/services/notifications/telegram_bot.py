"""
Telegram bot for job notifications.
Sends daily digests of high-scoring jobs with apply links.
"""

import logging
from typing import Optional

from backend.app.core import config
from backend.app.db.models import Job

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send job notifications via Telegram."""

    def __init__(self):
        self._bot = None
        self._enabled = bool(config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID)

    def _get_bot(self):
        """Lazy-init Telegram bot."""
        if self._bot is None and self._enabled:
            try:
                from telegram import Bot
                self._bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
                logger.info("Telegram bot initialized")
            except ImportError:
                logger.warning("python-telegram-bot not installed")
                self._enabled = False
            except Exception as e:
                logger.error(f"Telegram bot init failed: {e}")
                self._enabled = False
        return self._bot

    async def send_message(self, text: str) -> bool:
        """Send a text message via Telegram."""
        if not self._enabled:
            logger.debug("Telegram notifications disabled (no token/chat_id)")
            return False

        try:
            bot = self._get_bot()
            if bot:
                await bot.send_message(
                    chat_id=config.TELEGRAM_CHAT_ID,
                    text=text,
                    parse_mode="HTML",
                )
                return True
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
        return False

    async def send_job_alert(self, job: Job) -> bool:
        """Send a single job alert."""
        message = (
            f"🎯 <b>New Match: {job.title}</b>\n"
            f"🏢 {job.company}\n"
            f"📍 {job.location}\n"
            f"⭐ Score: {job.match_score}/10\n"
        )
        if job.salary_text:
            message += f"💰 {job.salary_text}\n"
        if job.matched_skills:
            message += f"🔧 {job.matched_skills}\n"
        message += f"\n🔗 <a href='{job.url}'>Apply Here</a>"

        return await self.send_message(message)

    async def send_daily_digest(self, jobs: list[Job]) -> bool:
        """Send a summary of high-scoring jobs."""
        if not jobs:
            return await self.send_message("📋 No new high-scoring jobs found today.")

        header = f"📊 <b>Daily Job Digest</b>\n🎯 {len(jobs)} high-scoring matches\n\n"
        entries = []

        for i, job in enumerate(jobs[:10], 1):  # Max 10 per digest
            entry = (
                f"{i}. <b>{job.title}</b>\n"
                f"   🏢 {job.company} | 📍 {job.location}\n"
                f"   ⭐ {job.match_score}/10"
            )
            if job.salary_text:
                entry += f" | 💰 {job.salary_text}"
            entry += f"\n   🔗 <a href='{job.url}'>Apply</a>\n"
            entries.append(entry)

        message = header + "\n".join(entries)
        if len(jobs) > 10:
            message += f"\n... and {len(jobs) - 10} more. Check the tracker for full list."

        return await self.send_message(message)


def send_sync_message(text: str) -> bool:
    """Synchronous wrapper for sending a Telegram message."""
    import asyncio
    notifier = TelegramNotifier()
    try:
        return asyncio.run(notifier.send_message(text))
    except Exception as e:
        logger.error(f"Sync Telegram send failed: {e}")
        return False


def send_sync_digest(jobs: list[Job]) -> bool:
    """Synchronous wrapper for sending a daily digest."""
    import asyncio
    notifier = TelegramNotifier()
    try:
        return asyncio.run(notifier.send_daily_digest(jobs))
    except Exception as e:
        logger.error(f"Sync digest send failed: {e}")
        return False
