import logging
from backend.app.db.models import Job, UserProfile
from backend.app.services.ai.provider import get_ai

logger = logging.getLogger(__name__)

def generate_application_email(job: Job, profile: UserProfile) -> str:
    """
    Generates a draft email to a recruiter based on the job description and user profile.
    
    Args:
        job (Job): The job object containing details like title, company, description, and recruiter info.
        profile (UserProfile): The user's profile containing skills, experience, and contact info.
        
    Returns:
        str: The generated email draft.
    """
    try:
        ai = get_ai()
        
        # specific context if recruiter name is known
        addressee = job.recruiter_name if job.recruiter_name else "Hiring Manager"
        
        system_prompt = (
            "You are an expert career coach and professional copywriter. "
            "Your task is to write a concise, professional, and persuasive job application email."
        )
        
        prompt = (
            f"Draft a cold email to {addressee} at {job.company} for the position of {job.title}.\n\n"
            f"My Details:\n"
            f"Name: {profile.full_name}\n"
            f"Email: {profile.email}\n"
            f"Phone: {profile.phone}\n"
            f"LinkedIn: {profile.linkedin_url}\n"
            f"Portfolio: {profile.portfolio_url}\n"
            f"Key Skills: {', '.join(profile.to_cv_data().skills) if profile.skills else 'Not specified'}\n\n"
            f"Job Description Excerpt:\n{job.description[:2000]}\n\n"
            f"Instructions:\n"
            f"1. Subject line should be clear and professional (e.g., Application for {job.title} - {profile.full_name}).\n"
            f"2. Keep the email body under 200 words.\n"
            f"3. Highlight 2-3 key matches between my skills and the job requirements.\n"
            f"4. Use a professional tone.\n"
            f"5. Mention that my resume is attached.\n"
            f"6. Do not include placeholders like [Your Name] unless absolutely necessary; use the provided profile info.\n"
            f"7. If the recruiter's name is known ({job.recruiter_name}), address them directly.\n"
        )
        
        return ai.generate(prompt, system_prompt)
        
    except Exception as e:
        logger.error(f"Failed to generate email draft: {e}")
        return "Error: Could not generate email draft. Please check AI service definition."
