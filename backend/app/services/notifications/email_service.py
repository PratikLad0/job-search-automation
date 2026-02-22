import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
import config

logger = logging.getLogger(__name__)

class EmailNotifier:
    def __init__(self):
        self.smtp_server = getattr(config, 'SMTP_SERVER', "smtp.gmail.com")
        self.smtp_port = int(getattr(config, 'SMTP_PORT', 587))
        self.username = getattr(config, 'SMTP_USERNAME', None)
        self.password = getattr(config, 'SMTP_PASSWORD', None)
        self.enabled = bool(self.username and self.password)

    def send_email(self, to_email: str, subject: str, body: str):
        if not self.enabled:
            logger.warning("Email notifications disabled (missing credentials)")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.username, to_email, text)
            server.quit()
            logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def send_job_alert(self, to_email: str, job):
        subject = f"New Job Match: {job.title} at {job.company}"
        body = f"""
        <h2>New High Scoring Job Found!</h2>
        <p><b>Role:</b> {job.title}</p>
        <p><b>Company:</b> {job.company}</p>
        <p><b>Location:</b> {job.location}</p>
        <p><b>Score:</b> {job.match_score}/10</p>
        <p><a href="{job.url}">Apply Here</a></p>
        """
        return self.send_email(to_email, subject, body)
