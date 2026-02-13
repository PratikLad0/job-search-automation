"""
Document generator — renders resume and cover letter to PDF.
Uses Jinja2 templates + WeasyPrint for HTML → PDF conversion.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from backend.app.core import config
from backend.app.db.models import Job, CVData
from backend.app.services.parsers.cv_parser import parse_cv
from backend.app.services.ai.resume_tailor import tailor_resume
from backend.app.services.ai.cover_letter import generate_cover_letter

logger = logging.getLogger(__name__)

# Initialize Jinja2 template engine
jinja_env = Environment(
    loader=FileSystemLoader(str(config.TEMPLATES_DIR)),
    autoescape=True,
)


def generate_resume_pdf(job: Job, cv_data: Optional[CVData] = None) -> Optional[Path]:
    """
    Generate a tailored resume PDF for a specific job.
    Returns the path to the generated PDF.
    """
    if cv_data is None:
        cv_data = parse_cv()

    try:
        # Get tailored content from AI
        tailored = tailor_resume(job, cv_data)

        # Render HTML template
        template = jinja_env.get_template("resume_template.html")
        html_content = template.render(
            name=cv_data.name,
            email=cv_data.email,
            phone=cv_data.phone,
            location=cv_data.location,
            title_line=tailored.get("title_line", "Software Engineer"),
            summary=tailored.get("summary", cv_data.summary),
            skills_highlighted=tailored.get("skills_highlighted", cv_data.skills),
            experience=tailored.get("experience", cv_data.experience),
            education=tailored.get("education", cv_data.education),
            projects=tailored.get("projects_highlighted", cv_data.projects),
            certifications=cv_data.certifications,
            achievements=cv_data.achievements,
            hobbies=cv_data.hobbies,
            interests=cv_data.interests,
            languages=cv_data.languages,
            volunteering=cv_data.volunteering,
            publications=cv_data.publications,
            awards=cv_data.awards,
            references=cv_data.references,
        )

        # Generate PDF filename
        safe_company = _sanitize_filename(job.company)
        safe_title = _sanitize_filename(job.title)
        filename = f"resume_{safe_company}_{safe_title}.pdf"
        output_path = config.RESUMES_DIR / filename

        # Convert HTML to PDF
        try:
            from weasyprint import HTML
            HTML(string=html_content).write_pdf(str(output_path))
            logger.info(f"Resume PDF generated: {output_path}")
        except Exception as e:
            # Fallback: save as HTML if WeasyPrint fails (e.g. missing dependencies or GObject error)
            html_path = output_path.with_suffix(".html")
            html_path.write_text(html_content, encoding="utf-8")
            logger.warning(f"WeasyPrint failed ({e}). Saved HTML: {html_path}")
            return html_path

        return output_path

    except Exception as e:
        logger.error(f"Resume generation failed: {e}")
        return None


def generate_cover_letter_pdf(
    job: Job, cv_data: Optional[CVData] = None
) -> Optional[Path]:
    """
    Generate a cover letter PDF for a specific job.
    Returns the path to the generated PDF.
    """
    if cv_data is None:
        cv_data = parse_cv()

    try:
        # Generate cover letter text
        letter_text = generate_cover_letter(job, cv_data)

        # Convert paragraphs to HTML
        paragraphs = letter_text.strip().split("\n\n")
        # Remove greeting and closing if AI included them
        content_html = ""
        for para in paragraphs:
            para = para.strip()
            if para and not para.lower().startswith("dear") and not para.lower().startswith("best regard"):
                content_html += f"<p>{para}</p>\n"

        # Render template
        template = jinja_env.get_template("cover_letter.html")
        html_content = template.render(
            date=datetime.now().strftime("%B %d, %Y"),
            name=cv_data.name,
            email=cv_data.email,
            phone=cv_data.phone,
            content=content_html,
        )

        # Generate PDF
        safe_company = _sanitize_filename(job.company)
        safe_title = _sanitize_filename(job.title)
        filename = f"cover_letter_{safe_company}_{safe_title}.pdf"
        output_path = config.COVER_LETTERS_DIR / filename

        try:
            from weasyprint import HTML
            HTML(string=html_content).write_pdf(str(output_path))
            logger.info(f"Cover letter PDF generated: {output_path}")
        except Exception as e:
            # Fallback to HTML
            html_path = output_path.with_suffix(".html")
            html_path.write_text(html_content, encoding="utf-8")
            logger.warning(f"WeasyPrint failed ({e}). Saved HTML: {html_path}")
            return html_path

        return output_path

    except Exception as e:
        logger.error(f"Cover letter generation failed: {e}")
        return None


def generate_all(job: Job, cv_data: Optional[CVData] = None) -> dict:
    """Generate both resume and cover letter for a job."""
    if cv_data is None:
        cv_data = parse_cv()

    resume_path = generate_resume_pdf(job, cv_data)
    cover_letter_path = generate_cover_letter_pdf(job, cv_data)

    return {
        "resume_path": str(resume_path) if resume_path else "",
        "cover_letter_path": str(cover_letter_path) if cover_letter_path else "",
    }


def _sanitize_filename(name: str) -> str:
    """Sanitize a string for use in filenames."""
    return "".join(c if c.isalnum() or c in "._- " else "" for c in name).strip()[:50].replace(" ", "_")
