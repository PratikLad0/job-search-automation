import json
import asyncio
import logging
import sys
import traceback
from typing import Optional, List
from pathlib import Path

from backend.app.core.queue_manager import queue_manager
from backend.app.services.ai.provider import get_ai
from backend.app.db.database import JobDatabase
from backend.app.services.parsers.cv_parser import parse_cv
from backend.app.core.logger import logger
from backend.app.services.automation.application_automator import AutomationManager
from backend.app.services.ai.scorer import score_job

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
        
        if (not cv_data.name or "Parsed Result (Error:" in cv_data.name) and not cv_data.email and not cv_data.skills:
            logger.warning("⚠️ Parsed CV data is largely empty or contains errors. Not updating profile to avoid wiping existing data.")
            return {"status": "error", "message": "AI failed to extract structured information from resume."}

        profile_data = {
            "full_name": cv_data.name,
            "email": cv_data.email,
            "phone": cv_data.phone,
            "location": cv_data.location,
            "about_me": cv_data.summary,
            "linkedin_url": cv_data.linkedin_url,
            "github_url": cv_data.github_url,
            "portfolio_url": cv_data.portfolio_url,
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
            
            # Prepare filters for scrape_all
            queries = [query] if query else None
            locations = [location] if location else None
            
            # Use scrape_all with the provided filters. 
            # If queries or locations are None, scrape_all will use config defaults.
            jobs = await asyncio.to_thread(scraper.scrape_all, queries=queries, locations=locations)
            
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

async def process_job_application(job_id: int):
    """
    Runs the automated job application process.
    On Windows, this must run in a dedicated thread with a ProactorEventLoop 
    to support Playwright's subprocess requirements.
    """
    def _run_automation_sync(jid: int):
        # Create a new event loop for this thread
        if sys.platform == 'win32':
            loop = asyncio.WindowsProactorEventLoopPolicy().new_event_loop()
        else:
            loop = asyncio.new_event_loop()
            
        asyncio.set_event_loop(loop)
        
        try:
            manager = AutomationManager()
            return loop.run_until_complete(manager.run_application(jid))
        finally:
            loop.close()

    try:
        logger.info(f"🚀 Starting automated application for job {job_id} (Windows-compatible mode)...")
        # Run the synchronous-wrapper in a separate thread
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, _run_automation_sync, job_id)
        
        if result.get("status") == "success":
            logger.info(f"✅ Application successful for job {job_id}")
        else:
            logger.error(f"❌ Application failed for job {job_id}: {result.get('message')}")
            
        return result
    except Exception as e:
        logger.error(f"❌ Automation task failed: {e}")
        logger.error(traceback.format_exc())
        raise e

async def process_job_scoring(job_id: int):
    """
    Scores a single job against the user profile.
    """
    try:
        db = JobDatabase()
        job = db.get_job(job_id)
        if not job:
            return {"status": "error", "message": "Job not found"}
        
        # Get profile data
        profile = db.get_profile(1)
        cv_data = profile.to_cv_data() if profile else None
        
        logger.info(f"📊 Scoring job {job_id}: {job.title} at {job.company}...")
        
        # Run scoring in thread
        result = await asyncio.to_thread(score_job, job, cv_data)
        
        # Update database
        db.update_job(
            job_id, 
            match_score=result["score"],
            score_reasoning=result["reasoning"],
            matched_skills=result["matched_skills"],
            status="scored"
        )
        
        return {
            "status": "success", 
            "message": f"Job scored: {result['score']}/10",
            "score": result["score"]
        }
    except Exception as e:
        logger.error(f"❌ Scoring task failed: {e}")
        raise e

async def process_bulk_scoring():
    """
    Scores all jobs that currently have no score.
    """
    try:
        db = JobDatabase()
        # Find all unscored jobs (status 'scraped' or match_score is null)
        # Using status='scraped' is a good proxy for unscored
        jobs = db.get_jobs(status="scraped")
        
        if not jobs:
            return {"status": "success", "message": "No unscored jobs found."}
        
        logger.info(f"� Starting bulk scoring for {len(jobs)} jobs...")
        
        profile = db.get_profile(1)
        cv_data = profile.to_cv_data() if profile else None
        
        scored_count = 0
        for job in jobs:
            try:
                # Score one by one to avoid overwhelming AI (or use thread pool)
                # But since this is a background task, sequential is fine for safety
                result = await asyncio.to_thread(score_job, job, cv_data)
                
                db.update_job(
                    job.id, 
                    match_score=result["score"],
                    score_reasoning=result["reasoning"],
                    matched_skills=result["matched_skills"],
                    status="scored"
                )
                scored_count += 1
            except Exception as inner_e:
                logger.error(f"Failed to score job {job.id}: {inner_e}")
                
        return {
            "status": "success", 
            "message": f"Bulk scoring complete. Scored {scored_count} jobs.",
            "count": scored_count
        }
    except Exception as e:
        logger.error(f"❌ Bulk scoring task failed: {e}")
        raise e
