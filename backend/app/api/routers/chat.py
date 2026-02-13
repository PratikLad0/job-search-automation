from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import sys
import os



try:
    from backend.app.services.ai.provider import get_ai
    from backend.app.db.database import JobDatabase
    from backend.app.api.dependencies import get_db
except ImportError:
    pass

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    job_id: Optional[int] = None
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: JobDatabase = Depends(get_db)):
    ai = get_ai()
    
    system_prompt = (
        "You are a helpful career assistant. You help the user with their job search, "
        "analyzing job descriptions, and providing advice on applications."
    )
    
    context_data = ""
    
    if request.job_id:
        job = db.get_job(request.job_id)
        if job:
            context_data += f"\n\nActive Job Context:\nTitle: {job.title}\nCompany: {job.company}\nDescription: {job.description}\n"
    
    if request.context:
        context_data += f"\n\nAdditional Context: {request.context}"
        
    if context_data:
        system_prompt += context_data
        
    try:
        response_text = ai.generate(request.message, system_prompt=system_prompt)
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
