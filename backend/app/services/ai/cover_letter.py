"""
AI-powered cover letter generator.
Creates concise, professional cover letters tailored to each job.
"""

import logging
from typing import Optional

from ai.provider import get_ai
from tracker.models import Job, CVData
from parsers.cv_parser import parse_cv

logger = logging.getLogger(__name__)


def generate_cover_letter(job: Job, cv_data: Optional[CVData] = None) -> str:
    """
    Generate a tailored cover letter for a specific job.
    Adapts style based on region (EU: concise, US: traditional, India: formal).
    """
    if cv_data is None:
        cv_data = parse_cv()

    ai = get_ai()

    # Determine style based on location
    style = _determine_style(job.location)

    prompt = f"""Write a professional cover letter for this job application.

CANDIDATE:
- Name: {cv_data.name}
- Experience: {cv_data.total_years}+ years
- Key Skills: {cv_data.get_skills_text()}
- Current Location: {cv_data.location}
- Recent Role: {cv_data.experience[0].get('title', 'Professional') if cv_data.experience else 'Professional'} at {cv_data.experience[0].get('company', '') if cv_data.experience else ''}
- Notable Projects: {", ".join([p.get('name', '') for p in cv_data.projects[:3]])}
- Achievements: {", ".join(cv_data.achievements[:3])}

JOB:
- Title: {job.title}
- Company: {job.company}
- Location: {job.location}
- Description: {job.description[:2000] if job.description else 'Not available'}

STYLE: {style}

INSTRUCTIONS:
1. Keep it concise ({_get_length_guide(style)})
2. Open with genuine interest in the role/company
3. Highlight 2-3 most relevant skills matching the job
4. Mention specific technical achievements with metrics
5. Show enthusiasm without being generic
6. {_get_relocation_note(cv_data.location, job.location)}
7. Close with a confident call to action

Do NOT use overly generic phrases like "I am writing to express my interest..."
Be specific and show you understand the role.

Return ONLY the cover letter text (no JSON, no metadata).
"""

    try:
        letter = ai.generate(prompt)
        logger.info(f"Cover letter generated for: {job.title} at {job.company}")
        return letter.strip()
    except Exception as e:
        logger.error(f"Cover letter generation failed: {e}")
        return _fallback_cover_letter(job, cv_data)


def _determine_style(location: str) -> str:
    """Determine cover letter style based on job location."""
    loc = location.lower()
    if any(x in loc for x in ["germany", "netherlands", "sweden", "eu", "europe"]):
        return "European (concise, direct, professional)"
    elif any(x in loc for x in ["uk", "london", "manchester"]):
        return "British (professional, slightly formal)"
    elif any(x in loc for x in ["usa", "us", "united states", "remote"]):
        return "American (confident, achievement-focused)"
    elif any(x in loc for x in ["india", "mumbai", "bangalore", "hyderabad", "pune"]):
        return "Indian (professional, detail-oriented)"
    elif any(x in loc for x in ["singapore", "uae", "dubai"]):
        return "International (professional, multicultural-aware)"
    return "Professional (standard international)"


def _get_length_guide(style: str) -> str:
    if "European" in style:
        return "200-300 words max — Europeans prefer brevity"
    elif "American" in style:
        return "250-350 words"
    return "250-350 words"


def _get_relocation_note(current_location: str, job_location: str) -> str:
    """Add relocation readiness note if locations differ."""
    if not current_location or not job_location:
        return "Skip relocation mentions"

    curr = current_location.lower()
    target = job_location.lower()

    if "remote" in target:
        return "Mention comfort with remote work and async collaboration"
    elif curr != target and not any(x in target for x in curr.split()):
        return f"Briefly mention readiness to relocate to {job_location}"
    return "No relocation mention needed"


def _fallback_cover_letter(job: Job, cv_data: CVData) -> str:
    """Simple fallback if AI fails."""
    return f"""Dear Hiring Manager,

I am writing to apply for the {job.title} position at {job.company}.

With {cv_data.total_years}+ years of experience in software engineering, specializing in {', '.join(cv_data.skills[:5])}, I am confident in my ability to contribute meaningfully to your team.

I would welcome the opportunity to discuss how my experience aligns with your requirements.

Best regards,
{cv_data.name}
{cv_data.email}
"""
