"""
Export tracked jobs to CSV/Excel format.
"""

import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

import pandas as pd

from backend.app.core import config
from backend.app.db.database import JobDatabase

logger = logging.getLogger(__name__)


def export_to_csv(
    db: Optional[JobDatabase] = None,
    output_path: Optional[Path] = None,
    min_score: Optional[float] = None,
    status: Optional[str] = None,
) -> Path:
    """
    Export jobs from database to CSV.
    Returns the path to the exported file.
    """
    if db is None:
        db = JobDatabase()

    jobs = db.get_jobs(status=status, min_score=min_score, limit=1000)

    if not jobs:
        logger.warning("No jobs to export")
        return None

    # Convert to DataFrame
    data = []
    for job in jobs:
        data.append({
            "ID": job.id,
            "Title": job.title,
            "Company": job.company,
            "Location": job.location,
            "Score": job.match_score,
            "Status": job.status,
            "Source": job.source,
            "Salary": job.salary_text,
            "URL": job.url,
            "Matched Skills": job.matched_skills,
            "Score Reasoning": job.score_reasoning,
            "Scraped At": job.scraped_at,
            "Applied At": job.applied_at or "",
            "Resume": job.resume_path,
            "Cover Letter": job.cover_letter_path,
            "Notes": job.notes,
        })

    df = pd.DataFrame(data)

    # Sort by score descending
    df = df.sort_values("Score", ascending=False, na_position="last")

    # Generate output path
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = config.REPORTS_DIR / f"jobs_export_{timestamp}.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(str(output_path), index=False, encoding="utf-8-sig")

    logger.info(f"Exported {len(df)} jobs to: {output_path}")
    return output_path


def export_to_excel(
    db: Optional[JobDatabase] = None,
    output_path: Optional[Path] = None,
    min_score: Optional[float] = None,
) -> Path:
    """Export jobs to Excel with formatting."""
    if db is None:
        db = JobDatabase()

    jobs = db.get_jobs(min_score=min_score, limit=1000)

    if not jobs:
        logger.warning("No jobs to export")
        return None

    data = [{
        "Title": j.title,
        "Company": j.company,
        "Location": j.location,
        "Score": j.match_score,
        "Status": j.status,
        "Salary": j.salary_text,
        "URL": j.url,
        "Source": j.source,
        "Applied": j.applied_at or "",
    } for j in jobs]

    df = pd.DataFrame(data).sort_values("Score", ascending=False, na_position="last")

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = config.REPORTS_DIR / f"jobs_export_{timestamp}.xlsx"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(str(output_path), index=False, engine="openpyxl")

    logger.info(f"Exported {len(df)} jobs to Excel: {output_path}")
    return output_path
