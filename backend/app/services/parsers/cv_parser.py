import json
import logging
from pathlib import Path
from typing import Optional

import pdfplumber
import docx

from backend.app.core import config
from backend.app.db.models import CVData
from backend.app.services.ai.provider import get_ai

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract raw text from a PDF file."""
    text = ""
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def extract_text_from_docx(docx_path: Path) -> str:
    """Extract raw text from a DOCX file."""
    doc = docx.Document(str(docx_path))
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return "\n".join(text)


def parse_cv(file_path: Optional[Path] = None, force_refresh: bool = False) -> CVData:
    """
    Parse CV (PDF or DOCX) and extract structured data using AI.
    Results are cached in cv_data.json for subsequent runs.
    """
    file_path = file_path or config.CV_PDF_PATH

    # Check cache first (only if using default path)
    is_default = file_path == config.CV_PDF_PATH
    if is_default and not force_refresh and config.CV_CACHE_PATH.exists():
        try:
            with open(config.CV_CACHE_PATH, "r", encoding="utf-8") as f:
                cached = json.load(f)
                logger.info("Loaded CV data from cache")
                return CVData.from_dict(cached)
        except Exception as e:
            logger.warning(f"Cache read failed, re-parsing: {e}")

    if not file_path.exists():
        raise FileNotFoundError(f"CV file not found: {file_path}")

    # Extract raw text based on extension
    if file_path.suffix.lower() == ".pdf":
        raw_text = extract_text_from_pdf(file_path)
    elif file_path.suffix.lower() in [".docx", ".doc"]:
        raw_text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

    logger.info(f"Extracted {len(raw_text)} characters from CV")

    # Use AI to parse structured data
    ai = get_ai()
    prompt = f"""Parse this resume/CV text and extract structured information.

RESUME TEXT:
{raw_text}

Return a valid JSON object with these exact fields:
{{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "phone number",
    "location": "City, Country",
    "summary": "Professional summary",
    "linkedin_url": "URL",
    "github_url": "URL",
    "portfolio_url": "URL",
    "skills": ["skill1", "skill2"],
    "experience": [
        {{
            "title": "Job Title",
            "company": "Company Name",
            "duration": "Start - End",
            "description": "Responsibilities"
        }}
    ],
    "education": [
        {{
            "degree": "Degree",
            "institution": "University",
            "year": "Year"
        }}
    ],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Description",
            "link": "URL",
            "tech_stack": ["Tech1", "Tech2"]
        }}
    ],
    "certifications": ["Cert Name"],
    "achievements": ["Achievement 1"],
    "hobbies": ["Hobby 1"],
    "interests": ["Interest 1"],
    "languages": ["Language 1"],
    "volunteering": [
        {{
            "organization": "Org Name",
            "role": "Role",
            "start_date": "Date",
            "end_date": "Date",
            "description": "Description"
        }}
    ],
    "publications": [
        {{
            "title": "Title",
            "publisher": "Publisher",
            "date": "Date",
            "link": "URL"
        }}
    ],
    "awards": [
        {{
            "title": "Award Name",
            "issuer": "Issuer",
            "date": "Date",
            "description": "Description"
        }}
    ],
    "references": [
        {{
            "name": "Name",
            "contact_info": "Contact",
            "relationship": "Relationship"
        }}
    ],
    "total_years": 5
}}
"""

    try:
        result = ai.generate_json(prompt)
        cv_data = CVData(
            name=result.get("name", ""),
            email=result.get("email", ""),
            phone=result.get("phone", ""),
            location=result.get("location", ""),
            summary=result.get("summary", ""),
            linkedin_url=result.get("linkedin_url", ""),
            github_url=result.get("github_url", ""),
            portfolio_url=result.get("portfolio_url", ""),
            skills=result.get("skills", []),
            experience=result.get("experience", []),
            education=result.get("education", []),
            projects=result.get("projects", []),
            certifications=result.get("certifications", []),
            achievements=result.get("achievements", []),
            hobbies=result.get("hobbies", []),
            interests=result.get("interests", []),
            languages=result.get("languages", []),
            volunteering=result.get("volunteering", []),
            publications=result.get("publications", []),
            awards=result.get("awards", []),
            references=result.get("references", []),
            total_years=int(result.get("total_years", 0)),
            raw_text=raw_text,
        )

        # Cache only if it's the default file
        if is_default:
            config.CV_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(config.CV_CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump(cv_data.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"CV parsed and cached: {cv_data.name}")

        return cv_data

    except Exception as e:
        logger.error(f"AI CV parsing failed: {e}")
        # Try a more basic extraction if JSON fails, or just return raw text
        return CVData(
            name=f"Parsed Result (Error: {str(e)[:50]})",
            raw_text=raw_text
        )
