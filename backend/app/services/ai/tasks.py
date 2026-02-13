import json
import asyncio
import logging
from typing import Optional, List
from pathlib import Path

from backend.app.core.queue_manager import queue_manager
from backend.app.services.ai.provider import get_ai
from backend.app.db.database import JobDatabase
from backend.app.services.parsers.cv_parser import parse_cv
from backend.app.core.logger import logger

async def process_chat_message(message: str, job_id: Optional[int] = None, context: Optional[str] = None):
    """
    Processes a chat message using the AI provider.
    Runs AI generation in a separate thread to avoid blocking.
    """
    ai = get_ai()
    db = JobDatabase()
    
    system_prompt = (
        "You are a helpful career assistant. You help the user with their job search, "
        "analyzing job descriptions, and providing advice on applications."
    )
    
    context_data = ""
    if job_id:
        job = db.get_job(job_id)
        if job:
            context_data += f"\n\nActive Job Context:\nTitle: {job.title}\nCompany: {job.company}\nDescription: {job.description}\n"
    
    if context:
        context_data += f"\n\nAdditional Context: {context}"
        
    if context_data:
        system_prompt += context_data
        
    try:
        response_text = await asyncio.to_thread(ai.generate, message, system_prompt=system_prompt)
        return {"response": response_text, "original_message": message}
    except Exception as e:
        logger.error(f"AI Generation failed: {e}")
        raise e

async def process_profile_update(file_path: Path):
    """
    Parses a CV and automatically updates the user profile.
    Runs parsing in a separate thread.
    """
    try:
        logger.info(f"📄 Background parsing resume: {file_path}")
        cv_data = await asyncio.to_thread(parse_cv, file_path, force_refresh=True)
        logger.info(f"✅ Resume parsed successfully for: {cv_data.name}")
        
        profile_data = {
            "full_name": cv_data.name,
            "email": cv_data.email,
            "phone": cv_data.phone,
            "location": cv_data.location,
            "about_me": cv_data.summary,
            "skills": json.dumps(cv_data.skills, ensure_ascii=False),
            "experience": json.dumps(cv_data.experience, ensure_ascii=False),
            "education": json.dumps(cv_data.education, ensure_ascii=False),
            "projects": json.dumps(cv_data.projects, ensure_ascii=False),
            "certifications": json.dumps(cv_data.certifications, ensure_ascii=False),
            "achievements": json.dumps(cv_data.achievements, ensure_ascii=False),
            "hobbies": json.dumps(cv_data.hobbies, ensure_ascii=False),
            "interests": json.dumps(cv_data.interests, ensure_ascii=False),
            "languages": json.dumps(cv_data.languages, ensure_ascii=False),
            "volunteering": json.dumps(cv_data.volunteering, ensure_ascii=False),
            "publications": json.dumps(cv_data.publications, ensure_ascii=False),
            "awards": json.dumps(cv_data.awards, ensure_ascii=False),
            "references": json.dumps(cv_data.references, ensure_ascii=False),
            "resume_path": str(file_path)
        }
        
        db = JobDatabase()
        db.create_or_update_profile(profile_data)
        logger.info(f"💾 Profile auto-saved for {cv_data.name}")
        
        return {"status": "success", "message": "Profile updated from CV", "full_name": cv_data.name}
    except Exception as e:
        logger.error(f"❌ Background CV update failed: {e}")
        raise e

async def process_resume_generation(job_id: int, format: str = "pdf"):
    """
    Generates resume only.
    Runs generation in threads.
    """
    try:
        from backend.app.services.generators.resume_generator import generate_resume_pdf
        from backend.app.services.generators.docx_generator import generate_resume_docx
        
        db = JobDatabase()
        job = db.get_job(job_id)
        if not job:
            return {"error": "Job not found"}
            
        profile = db.get_profile(1) 
        cv_data = profile.to_cv_data() if profile else None

        logger.info(f"📄 Generating {format.upper()} resume for job {job_id}...")
        
        resume_path = None

        if format.lower() == "pdf":
            resume_path = await asyncio.to_thread(generate_resume_pdf, job, cv_data)
        elif format.lower() == "docx":
            r_path = await asyncio.to_thread(generate_resume_docx, job, cv_data)
            resume_path = str(r_path) if r_path else None

        if resume_path:
            db.update_job(job_id, resume_path=str(resume_path), status="resume_generated")
            
        return {
            "status": "success", 
            "job_id": job_id,
            "document_type": "resume",
            "resume_url": f"/generators/download?path={resume_path}" if resume_path else None,
        }
    except Exception as e:
        logger.error(f"❌ Resume generation failed: {e}")
        raise e

async def process_cover_letter_generation(job_id: int, format: str = "pdf"):
    """
    Generates cover letter only.
    Runs generation in threads.
    """
    try:
        from backend.app.services.generators.resume_generator import generate_cover_letter_pdf
        from backend.app.services.generators.docx_generator import generate_cover_letter_docx
        
        db = JobDatabase()
        job = db.get_job(job_id)
        if not job:
            return {"error": "Job not found"}
            
        profile = db.get_profile(1) 
        cv_data = profile.to_cv_data() if profile else None

        logger.info(f"📄 Generating {format.upper()} cover letter for job {job_id}...")
        
        cover_letter_path = None

        if format.lower() == "pdf":
            cover_letter_path = await asyncio.to_thread(generate_cover_letter_pdf, job, cv_data)
        elif format.lower() == "docx":
            c_path = await asyncio.to_thread(generate_cover_letter_docx, job, cv_data)
            cover_letter_path = str(c_path) if c_path else None

        if cover_letter_path:
            db.update_job(job_id, cover_letter_path=str(cover_letter_path))
            
        return {
            "status": "success", 
            "job_id": job_id,
            "document_type": "cover_letter",
            "cover_letter_url": f"/generators/download?path={cover_letter_path}" if cover_letter_path else None,
        }
    except Exception as e:
        logger.error(f"❌ Cover letter generation failed: {e}")
        raise e

async def process_document_generation(job_id: int, format: str = "pdf"):
    """
    Generates resume and cover letter sequentially (DEPRECATED - use separate functions).
    Runs generation in threads.
    """
    try:
        from backend.app.services.generators.resume_generator import generate_all as generate_pdf
        from backend.app.services.generators.docx_generator import generate_resume_docx, generate_cover_letter_docx
        
        db = JobDatabase()
        job = db.get_job(job_id)
        if not job:
            return {"error": "Job not found"}
            
        profile = db.get_profile(1) 
        cv_data = profile.to_cv_data() if profile else None

        logger.info(f"📄 Generating {format.upper()} documents for job {job_id}...")
        
        resume_path = None
        cover_letter_path = None

        if format.lower() == "pdf":
            result = await asyncio.to_thread(generate_pdf, job, cv_data)
            resume_path = result.get("resume_path")
            cover_letter_path = result.get("cover_letter_path")
        elif format.lower() == "docx":
            r_path = await asyncio.to_thread(generate_resume_docx, job, cv_data)
            c_path = await asyncio.to_thread(generate_cover_letter_docx, job, cv_data)
            resume_path = str(r_path) if r_path else None
            cover_letter_path = str(c_path) if c_path else None

        if resume_path:
            db.update_job(job_id, resume_path=resume_path, status="resume_generated")
        if cover_letter_path:
            db.update_job(job_id, cover_letter_path=cover_letter_path)
            
        return {
            "status": "success", 
            "job_id": job_id,
            "resume_url": f"/generators/download?path={resume_path}" if resume_path else None,
            "cover_letter_url": f"/generators/download?path={cover_letter_path}" if cover_letter_path else None
        }
    except Exception as e:
        logger.error(f"❌ Document generation failed: {e}")
        raise e


async def process_scraping(source: Optional[str], query: Optional[str], location: Optional[str]):
    """
    Runs one or more scrapers and adds results to the database.
    Runs scrapers in threads.
    """
    try:
        from backend.app.cli import _get_scrapers
        
        db = JobDatabase()
        scrapers_classes = _get_scrapers(source)
        
        overall_result = {"added": 0, "skipped": 0, "scrapers": []}
        
        for scraper_cls in scrapers_classes:
            scraper = scraper_cls()
            logger.info(f"🚀 Scraping {scraper.SOURCE_NAME}...")
            
            if query and location:
                jobs = await asyncio.to_thread(scraper.scrape, query, location)
            elif query:
                jobs = await asyncio.to_thread(scraper.scrape, query)
            else:
                jobs = await asyncio.to_thread(scraper.scrape_all)
            
            result = db.add_jobs(jobs)
            logger.info(f"✅ Added {result['added']} jobs from {scraper.SOURCE_NAME}")
            
            overall_result["added"] += result["added"]
            overall_result["skipped"] += result["skipped"]
            overall_result["scrapers"].append({
                "name": scraper.SOURCE_NAME,
                "added": result["added"],
                "skipped": result["skipped"]
            })
            
            # Start background scoring for newly added jobs
            # This could be another task queued here
            
        return {
            "status": "success",
            "message": f"Scraping complete. Added {overall_result['added']} jobs.",
            "data": overall_result
        }
    except Exception as e:
        logger.error(f"❌ Scraper task failed: {e}")
        raise e
