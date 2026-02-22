from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, List

from backend.app.db.database import JobDatabase
from backend.app.db.models import Email, UserProfile
from backend.app.services.ai.provider import get_ai
from backend.app.core.logger import logger

router = APIRouter(prefix="/emails", tags=["emails"])
db = JobDatabase()

@router.get("/", response_model=List[Email])
async def get_emails(skip: int = Query(0, ge=0), limit: int = Query(50, le=100)):
    """Get a list of emails."""
    return db.get_emails(skip=skip, limit=limit)

@router.get("/{email_id}", response_model=Email)
async def get_email(email_id: int):
    """Get a specific email by ID."""
    email = db.get_email(email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email

@router.post("/{email_id}/reply")
async def generate_reply(email_id: int):
    """Generate an AI reply for a specific email."""
    email = db.get_email(email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    profile = db.get_profile(1) # Default user profile
    if not profile:
        profile = UserProfile(full_name="Job Seeker") # Fallback
        
    ai = get_ai()
    
    # Construct Prompt
    context_str = f"My Name: {profile.full_name}\n"
    if profile.about_me:
        context_str += f"My Background: {profile.about_me}\n"
    if profile.skills:
        context_str += f"My Skills: {profile.skills}\n"
        
    prompt = (
        f"You are writing a professional email reply on behalf of {profile.full_name}.\n\n"
        f"CONTEXT:\n{context_str}\n\n"
        f"INCOMING EMAIL:\n"
        f"From: {email.sender}\n"
        f"Subject: {email.subject}\n"
        f"Content: {email.body}\n\n"
        f"TASK: Write a polite, professional, and concise reply to this email. "
        f"If they are asking for availability, suggest flexibility. "
        f"If they are asking for documents, mention they are attached (I will attach them manually). "
        f"Keep the tone professional and enthusiastic."
    )
    
    try:
        reply = ai.generate(prompt)
        return {"reply": reply}
    except Exception as e:
        logger.error(f"Failed to generate reply: {e}")
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")
