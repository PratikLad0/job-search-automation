import logging
import html
import asyncio
from typing import Optional

from telegram import Update, Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, ApplicationBuilder, CallbackQueryHandler

from backend.app.core import config
from backend.app.db.database import JobDatabase
from backend.app.db.models import Job

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """
    Telegram bot service handling both push notifications and interactive commands.
    Implemented as a Singleton to ensure only one Application instance exists.
    """
    _instance = None
    _app: Optional[Application] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelegramNotifier, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self._enabled = bool(config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID)
        self.db = JobDatabase()
        
        if self._enabled:
            try:
                # Build the Application
                self._app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
                self._register_handlers()
                logger.info("Telegram Application built successfully")
            except Exception as e:
                logger.error(f"Failed to build Telegram Application: {e}")
                self._enabled = False
        else:
            logger.warning("Telegram Bot Token or Chat ID missing. Notifications disabled.")
        
        self._initialized = True

    def _register_handlers(self):
        """Register command handlers."""
        if not self._app:
            return
            
        self._app.add_handler(CommandHandler("start", self.cmd_start))
        self._app.add_handler(CommandHandler("help", self.cmd_help))
        self._app.add_handler(CommandHandler("status", self.cmd_status))
        self._app.add_handler(CommandHandler("jobs", self.cmd_jobs))
        
        # Handler for text messages (replies)
        from telegram.ext import MessageHandler, filters
        self._app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_reply))
        
        # Handler for callback queries (buttons)
        self._app.add_handler(CallbackQueryHandler(self.handle_callback))

    async def start(self):
        """Start the bot application (initialize, start, start_polling)."""
        if not self._enabled or not self._app:
            return

        try:
            logger.info("Starting Telegram Bot Polling...")
            await self._app.initialize()
            await self._app.start()
            # Start polling in a non-blocking way
            await self._app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
            logger.info("Telegram Bot Polling Active")
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")

    async def stop(self):
        """Stop the bot application."""
        if not self._enabled or not self._app:
            return

        try:
            logger.info("Stopping Telegram Bot...")
            await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()
            logger.info("Telegram Bot Stopped")
        except Exception as e:
            logger.error(f"Failed to stop Telegram bot: {e}")

    async def send_message(self, text: str, reply_markup=None) -> Optional[int]:
        """Send a text message via Telegram. Returns Message ID if successful."""
        if not self._enabled or not self._app:
            logger.debug("Telegram notifications disabled")
            return None

        try:
            message = await self._app.bot.send_message(
                chat_id=config.TELEGRAM_CHAT_ID,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
            return message.message_id
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            return None

    async def send_job_alert(self, job: Job) -> bool:
        """Send a single job alert."""
        safe_title = html.escape(job.title)
        safe_company = html.escape(job.company)
        safe_location = html.escape(job.location)
        
        message = (
            f"🎯 <b>New Match: {safe_title}</b>\n"
            f"🏢 {safe_company}\n"
            f"📍 {safe_location}\n"
            f"⭐ Score: {job.match_score}/10\n"
        )
        if job.salary_text:
            message += f"💰 {html.escape(job.salary_text)}\n"
        if job.matched_skills:
            message += f"🔧 {html.escape(job.matched_skills)}\n"
        message += f"\n🔗 <a href='{job.url}'>Apply Here</a>"

        # Add buttons for actions
        buttons = []
        if job.recruiter_email:
             buttons.append([InlineKeyboardButton("✍️ Draft Email", callback_data=f"draft_email_{job.id}")])
        if job.application_form_url:
             buttons.append([InlineKeyboardButton("📝 Open Form", url=job.application_form_url)])
        
        reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

        return await self.send_message(message, reply_markup=reply_markup)

    async def send_daily_digest(self, jobs: list[Job]) -> bool:
        """Send a summary of high-scoring jobs."""
        if not jobs:
            return await self.send_message("📋 No new high-scoring jobs found today.")

        header = f"📊 <b>Daily Job Digest</b>\n🎯 {len(jobs)} high-scoring matches\n\n"
        entries = []

        for i, job in enumerate(jobs[:10], 1):  # Max 10 per digest
            safe_title = html.escape(job.title)
            safe_company = html.escape(job.company)
            safe_location = html.escape(job.location)
            
            entry = (
                f"{i}. <b>{safe_title}</b>\n"
                f"   🏢 {safe_company} | 📍 {safe_location}\n"
                f"   ⭐ {job.match_score}/10"
            )
            if job.salary_text:
                entry += f" | 💰 {html.escape(job.salary_text)}"
            entry += f"\n   🔗 <a href='{job.url}'>Apply</a>\n"
            entries.append(entry)

        message = header + "\n".join(entries)
        if len(jobs) > 10:
            message += f"\n... and {len(jobs) - 10} more. Check the tracker for full list."

        return await self.send_message(message)

    # --- Command Handlers ---

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "👋 <b>Welcome to Job Search Automation Bot!</b>\n\n"
            "I can help you track new job postings and notifications.\n"
            "Try /help to see available commands.",
            parse_mode=ParseMode.HTML
        )

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            "🤖 <b>Available Commands:</b>\n\n"
            "/jobs - Show recent high-scoring jobs\n"
            "/status - Check backend system status\n"
            "/help - Show this help message"
        )
        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            stats = self.db.get_stats()
            total = stats.get("total", 0)
            avg_score = stats.get("avg_score", 0)
            
            status_text = (
                "🟢 <b>System Online</b>\n\n"
                f"📊 <b>Job Stats:</b>\n"
                f"• Total Jobs: {total}\n"
                f"• Avg Match Score: {avg_score}\n"
            )
            await update.message.reply_text(status_text, parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await update.message.reply_text("❌ Error fetching status.")

    async def cmd_jobs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            # Fetch top 5 high scoring jobs
            jobs = self.db.get_jobs(limit=5, min_score=7.0)
            
            # Fallback if no high scoring jobs
            if not jobs:
                jobs = self.db.get_jobs(limit=5)
            
            if not jobs:
                await update.message.reply_text("📭 No jobs found.")
                return

            response = "🔎 <b>Recent Top Jobs:</b>\n\n"
            for job in jobs:
                safe_title = html.escape(job.title)
                safe_company = html.escape(job.company)
                response += (
                    f"• <b>{safe_title}</b>\n"
                    f"  🏢 {safe_company}\n"
                    f"  ⭐ {job.match_score}/10\n"
                    f"  🔗 <a href='{job.url}'>View Job</a>\n\n"
                )
            await update.message.reply_html(response)
        except Exception as e:
            logger.error(f"Error in jobs command: {e}")
            await update.message.reply_text("❌ Error fetching jobs.")

    async def handle_reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming text messages (potential replies to emails)."""
        if not update.message or not update.message.reply_to_message:
            return

        original_msg_id = update.message.reply_to_message.message_id
        user_reply = update.message.text
        
        # Check if this message corresponds to an email
        email = self.db.get_email_by_telegram_id(original_msg_id)
        if not email:
            # Not an email thread, ignore
            return
            
        await update.message.reply_text("✍️ <b>Drafting reply...</b>", parse_mode=ParseMode.HTML)
        
        try:
            # Generate AI Reply
            from backend.app.db.models import UserProfile
            from backend.app.services.ai.provider import get_ai
            
            profile = self.db.get_profile(1)
            if not profile:
                profile = UserProfile(full_name="Job Seeker")
            
            ai = get_ai()
            
            context_str = f"My Name: {profile.full_name}\n"
            if profile.about_me:
                context_str += f"My Background: {profile.about_me}\n"
            
            prompt = (
                f"You are drafting a semi-automated reply to an email based on the user's instructions.\n\n"
                f"CONTEXT:\n{context_str}\n\n"
                f"INCOMING EMAIL:\n"
                f"From: {email.sender}\n"
                f"Subject: {email.subject}\n"
                f"Content: {email.body}\n\n"
                f"USER INSTRUCTION: {user_reply}\n\n"
                f"TASK: Write a complete, professional email reply following the user's instruction."
            )
            
            draft_reply = ai.generate(prompt)
            
            # Send draft back to user
            response_text = (
                f"📝 <b>Draft Reply for: {html.escape(email.subject)}</b>\n\n"
                f"<i>{html.escape(draft_reply)}</i>\n\n"
                f"⚠️ <i>Copy this text to send. (Sending directly not yet implemented)</i>"
            )
            await update.message.reply_text(response_text, parse_mode=ParseMode.HTML, reply_to_message_id=update.message.message_id)
            
        except Exception as e:
            logger.error(f"Failed to generate draft reply: {e}")
            await update.message.reply_text("❌ Failed to generate draft.")

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks."""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        if data.startswith("draft_email_"):
            try:
                job_id = int(data.split("_")[2])
                job = self.db.get_job(job_id)
                profile = self.db.get_profile(1) # Default profile
                
                if not job:
                    await query.edit_message_text("❌ Job not found.")
                    return
                    
                if not profile:
                    await query.edit_message_text("❌ User Profile not found.")
                    return

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"⏳ Generating email draft for <b>{html.escape(job.title)}</b>...",
                    parse_mode=ParseMode.HTML
                )
                
                # Generate Draft
                from backend.app.services.generators.email_generator import generate_application_email
                draft = generate_application_email(job, profile)
                
                response_text = (
                    f"📝 <b>Draft Email to {html.escape(job.recruiter_name or 'Hiring Manager')}</b>\n"
                    f"📧 {html.escape(job.recruiter_email)}\n\n"
                    f"<pre>{html.escape(draft)}</pre>\n\n"
                    f"⚠️ <i>Copy and paste into your email client.</i>"
                )
                
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, 
                    text=response_text, 
                    parse_mode=ParseMode.HTML
                )
                
            except Exception as e:
                logger.error(f"Error in handle_callback: {e}")
                await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Error generating draft.")

    
def send_sync_message(text: str) -> bool:
    """Synchronous wrapper for sending a Telegram message."""
    import asyncio
    notifier = TelegramNotifier()
    try:
        # This is tricky because we might need to use the existing loop or create a new one
        # But if the app is already running in a loop, we can't just run_until_complete?
        # Ideally, we should not use sync wrappers with async Application.
        # But keeping it for backward compat if needed.
        return asyncio.run(notifier.send_message(text))
    except Exception as e:
        logger.error(f"Sync Telegram send failed: {e}")
        return False


def send_sync_digest(jobs: list[Job]) -> bool:
    """Synchronous wrapper for sending a daily digest via CLI."""
    import asyncio
    notifier = TelegramNotifier()
    try:
        return asyncio.run(notifier.send_daily_digest(jobs))
    except Exception as e:
        logger.error(f"Sync digest send failed: {e}")
        return False
