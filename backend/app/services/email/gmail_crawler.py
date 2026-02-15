import os
import base64
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from backend.app.core import config
from backend.app.core.logger import logger
from backend.app.services.notifications.telegram_bot import TelegramNotifier

class GmailCrawler:
    """Service to crawl Gmail for job-related emails."""

    def __init__(self):
        self.notifier = TelegramNotifier()
        self.service = self._get_gmail_service()
        self.cache_file = config.DATA_DIR / "email_cache.json"
        self.processed_ids = self._load_cache()

    def _load_cache(self) -> set:
        """Load processed email IDs from cache file."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    return set(json.load(f))
            except Exception as e:
                logger.error(f"Failed to load email cache: {e}")
        return set()

    def _save_cache(self):
        """Save processed email IDs to cache file."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(list(self.processed_ids), f)
        except Exception as e:
            logger.error(f"Failed to save email cache: {e}")

    def _get_gmail_service(self):
        """Build Gmail API service using stored token."""
        # ... (rest of the method unchanged, but we should import Credentials if not already)
        if not os.path.exists(config.GOOGLE_TOKEN_FILE):
            logger.warning("Gmail token not found. Please authenticate via /auth/login")
            return None

        try:
            creds = Credentials.from_authorized_user_file(str(config.GOOGLE_TOKEN_FILE), config.GOOGLE_SCOPES)
            return build('gmail', 'v1', credentials=creds)
        except Exception as e:
            logger.error(f"Failed to build Gmail service: {e}")
            return None

    async def check_new_emails(self, query="is:unread"):
        """Search for new job-related emails and notify via Telegram."""
        if not self.service:
            # Try to re-initialize service if token appeared later
            self.service = self._get_gmail_service()
            if not self.service:
                return

        try:
            # Search for job-related unread emails
            # Keywords: interview, recruiter, hiring, job application, offer
            job_query = f"{query} (interview OR recruiter OR hiring OR \"job application\" OR \"offer letter\")"
            results = self.service.users().messages().list(userId='me', q=job_query).execute()
            messages = results.get('messages', [])

            if not messages:
                logger.info("No new job-related emails found.")
                return
            
            new_notifications = False
            for msg_info in messages:
                msg_id = msg_info['id']
                
                # specific check to avoid duplicate notifications
                if msg_id in self.processed_ids:
                    continue

                msg = self.service.users().messages().get(userId='me', id=msg_id).execute()
                headers = msg['payload']['headers']
                
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
                sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown Sender")
                snippet = msg.get('snippet', '')

                # Sanitize for HTML
                import html
                safe_sender = html.escape(sender)
                safe_subject = html.escape(subject)
                safe_snippet = html.escape(snippet)

                # Send Telegram notification
                notification_text = (
                    f"📧 <b>Important Email Found!</b>\n"
                    f"👤 <b>From:</b> {safe_sender}\n"
                    f"📝 <b>Subject:</b> {safe_subject}\n\n"
                    f"<i>{safe_snippet}...</i>"
                )
                
                success = await self.notifier.send_message(notification_text)
                if success:
                    logger.info(f"Notification sent for email: {subject}")
                    self.processed_ids.add(msg_id)
                    new_notifications = True
            
            if new_notifications:
                self._save_cache()

        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
        except Exception as e:
            logger.error(f"Unexpected error in GmailCrawler: {e}")

async def run_gmail_crawler():
    """Entry point for periodic Gmail crawling."""
    crawler = GmailCrawler()
    await crawler.check_new_emails()
