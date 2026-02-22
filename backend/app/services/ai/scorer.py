"""
AI-powered job-CV match scoring engine.
Scores jobs 1-10 based on skill match, seniority, tech stack alignment.
"""

import logging
from typing import Optional

from backend.app.core import config
from backend.app.services.ai.provider import get_ai
from backend.app.db.models import Job, CVData
from backend.app.services.parsers.cv_parser import parse_cv

logger = logging.getLogger(__name__)


def score_job(job: Job, cv_data: Optional[CVData] = None) -> dict:
    """
    Score a single job against the candidate's CV.

    Returns:
        dict with keys: score (float), reasoning (str), matched_skills (str)
    """
    if cv_data is None:
        cv_data = parse_cv()

    ai = get_ai()

    prompt = f"""You are a job matching expert. Score how well this candidate matches the job.

CANDIDATE PROFILE:
- Name: {cv_data.name}
- Experience: {cv_data.total_years}+ years
- Skills: {cv_data.get_skills_text()}
- Summary: {cv_data.summary}
- Current Location: {cv_data.location}

JOB DETAILS:
- Title: {job.title}
- Company: {job.company}
- Location: {job.location}
- Source: {job.source}
- Salary: {job.salary_text or 'Not specified'}
- Description: {job.description[:3000] if job.description else 'Not available'}

SCORING CRITERIA:
1. Technical skill match (40%): How well do the candidate's skills match the requirements?
2. Seniority fit (20%): Is this role appropriate for {cv_data.total_years}+ years experience?
3. Role type alignment (20%): Does this match Backend/Full-stack/SDE/Platform/AI roles?
4. Location compatibility (10%): Is the location suitable (considering remote/relocation)?
5. Growth potential (10%): Does this role offer career growth?

IMPORTANT:
- Accept broad roles: Backend, SDE, Full-stack, Software Engineer, Platform, DevOps, AI/ML
- Do NOT reject roles just because they're not purely backend
- Score frontend-only or unrelated roles (sales, marketing) low

Return a JSON object:
{{
    "score": 7.5,
    "reasoning": "Brief explanation of the score",
    "matched_skills": "skill1, skill2, skill3",
    "concerns": "Any potential issues or mismatches"
}}
"""

    try:
        result = ai.generate_json(prompt)
        score = float(result.get("score", 0))
        score = max(1.0, min(10.0, score))  # Clamp between 1-10

        return {
            "score": score,
            "reasoning": result.get("reasoning", ""),
            "matched_skills": result.get("matched_skills", ""),
            "concerns": result.get("concerns", ""),
        }
    except Exception as e:
        logger.error(f"Scoring failed for '{job.title}' at '{job.company}': {e}")
        return {
            "score": 0,
            "reasoning": f"Scoring error: {str(e)}",
            "matched_skills": "",
            "concerns": "",
        }


def score_jobs(jobs: list[Job], cv_data: Optional[CVData] = None) -> list[Job]:
    """
    Score multiple jobs and update their match_score fields.
    Returns the list with scores populated.
    """
    if cv_data is None:
        cv_data = parse_cv()

    for i, job in enumerate(jobs):
        logger.info(f"Scoring job {i+1}/{len(jobs)}: {job.title} at {job.company}")

        result = score_job(job, cv_data)
        job.match_score = result["score"]
        job.score_reasoning = result["reasoning"]
        job.matched_skills = result["matched_skills"]
        job.status = "scored"

        logger.info(
            f"  → Score: {result['score']}/10 | "
            f"Skills: {result['matched_skills'][:50]}"
        )

    # Sort by score descending
    jobs.sort(key=lambda j: j.match_score or 0, reverse=True)

    high_score = [j for j in jobs if (j.match_score or 0) >= config.MIN_MATCH_SCORE]
    logger.info(
        f"Scoring complete: {len(high_score)}/{len(jobs)} jobs scored ≥ {config.MIN_MATCH_SCORE}"
    )

    return jobs


def filter_high_scoring(jobs: list[Job], min_score: Optional[float] = None) -> list[Job]:
    """Filter jobs to only those above the minimum score threshold."""
    threshold = min_score or config.MIN_MATCH_SCORE
    return [j for j in jobs if (j.match_score or 0) >= threshold]
