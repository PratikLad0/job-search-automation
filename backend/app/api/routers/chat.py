from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from backend.app.core.queue_manager import queue_manager
from backend.app.services.ai.tasks import process_chat_message

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    job_id: Optional[int] = None
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str

@router.post("/", response_model=dict)
async def chat(request: ChatRequest):
    """Queue chat message for background processing."""
    await queue_manager.add_task(
        "chat",
        process_chat_message,
        message=request.message,
        job_id=request.job_id,
        context=request.context
    )
    
    return {
        "status": "queued",
        "message": "Chat request sent to AI for processing. You will see the response in the chat soon."
    }
