"""
AI-powered resume tailoring engine.
Dynamically adjusts resume emphasis based on specific job requirements.
"""

import logging
from typing import Optional

from ai.provider import get_ai
from tracker.models import Job, CVData
from parsers.cv_parser import parse_cv

logger = logging.getLogger(__name__)


def tailor_resume(job: Job, cv_data: Optional[CVData] = None) -> dict:
    """
    Generate tailored resume content for a specific job.

    Returns a dict with tailored sections ready for template rendering:
    - summary, skills, experience_highlights, title_line
    """
    if cv_data is None:
        cv_data = parse_cv()

    ai = get_ai()

    prompt = f"""You are an expert resume writer. Tailor this candidate's resume for the specific job.

CANDIDATE PROFILE:
- Name: {cv_data.name}
- Email: {cv_data.email}
- Phone: {cv_data.phone}
- Location: {cv_data.location}
- Total Experience: {cv_data.total_years}+ years
- Skills: {cv_data.get_skills_text()}
- Summary: {cv_data.summary}

EXPERIENCE:
{_format_experience(cv_data.experience)}

EDUCATION:
{_format_education(cv_data.education)}

PROJECTS:
{_format_projects(cv_data.projects)}

ACHIEVEMENTS:
{", ".join(cv_data.achievements) if cv_data.achievements else "Not available"}

TARGET JOB:
- Title: {job.title}
- Company: {job.company}
- Location: {job.location}
- Description: {job.description[:2500] if job.description else 'Not available'}

INSTRUCTIONS:
1. Write a tailored professional summary (3-4 sentences) emphasizing skills relevant to THIS job
2. Reorder and highlight the most relevant skills for this role
3. For each experience entry, write 3-4 bullet points emphasizing relevant achievements
4. Create an appropriate title line (e.g., "Senior Backend Engineer | Cloud & Microservices")

IMPORTANT:
- Keep all information truthful — only reorganize and emphasize, don't fabricate
- Use action verbs and quantify achievements where possible
- Make it ATS-friendly (use keywords from the job description)
- Keep it concise (aim for 1-2 page resume content)

Return a JSON object:
{{
    "title_line": "Professional title matching the job",
    "summary": "Tailored professional summary",
    "skills_highlighted": ["most", "relevant", "skills", "first"],
    "experience": [
        {{
            "title": "Job Title",
            "company": "Company",
            "duration": "Duration",
            "bullets": ["Achievement 1", "Achievement 2", "Achievement 3"]
        }}
    ],
    "education": [
        {{
            "degree": "Degree",
            "institution": "Institution",
            "year": "Year"
        }}
    ]
}}
"""

    try:
        result = ai.generate_json(prompt)
        logger.info(f"Resume tailored for: {job.title} at {job.company}")
        return result
    except Exception as e:
        logger.error(f"Resume tailoring failed: {e}")
        # Return raw CV data as fallback
        return {
            "title_line": f"{cv_data.name} | Software Engineer",
            "summary": cv_data.summary,
            "skills_highlighted": cv_data.skills,
            "experience": cv_data.experience,
            "education": cv_data.education,
        }


def _format_experience(experience: list[dict]) -> str:
    """Format experience list for the prompt."""
    parts = []
    for exp in experience:
        title = exp.get("title", "")
        company = exp.get("company", "")
        duration = exp.get("duration", "")
        desc = exp.get("description", "")
        parts.append(f"- {title} at {company} ({duration}): {desc}")
    return "\n".join(parts) if parts else "Not available"


def _format_education(education: list[dict]) -> str:
    """Format education list for the prompt."""
    parts = []
    for edu in education:
        degree = edu.get("degree", "")
        institution = edu.get("institution", "")
        year = edu.get("year", "")
        parts.append(f"- {degree} from {institution} ({year})")
    return "\n".join(parts) if parts else "Not available"


def _format_projects(projects: list[dict]) -> str:
    """Format projects list for the prompt."""
    parts = []
    for proj in projects:
        name = proj.get("name", "")
        desc = proj.get("description", "")
        tech = ", ".join(proj.get("tech_stack", []))
        parts.append(f"- {name}: {desc} (Tech: {tech})")
    return "\n".join(parts) if parts else "Not available"
