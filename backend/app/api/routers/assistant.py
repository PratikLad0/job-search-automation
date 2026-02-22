import json
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from backend.app.core.websocket_manager import manager as ws_manager
from backend.app.core.queue_manager import queue_manager

from backend.app.services.ai.tasks import process_chat_message

logger = logging.getLogger("jobsearch.assistant")

router = APIRouter(prefix="/assistant", tags=["assistant"])

class ChatRequest(BaseModel):
    message: str
    job_id: Optional[int] = None
    context: Optional[str] = None

@router.get("/test")
async def test_assistant():
    return {"status": "assistant router is working"}

@router.websocket("/ws")
async def websocket_assistant(websocket: WebSocket):
    logger.info("Incoming WebSocket connection attempt...")
    try:
        await ws_manager.connect(websocket)
        logger.info("WebSocket connection accepted and managed.")
    except Exception as e:
        logger.error(f"Failed to connect WebSocket: {e}")
        return
    try:
        while True:
            # Receive data from client
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                
                if payload.get("type") == "chat":
                    message = payload.get("message")
                    job_id = payload.get("job_id")
                    context = payload.get("context")
                    
                    if not message:
                        continue
                        
                    # Add chat processing to the sequential queue
                    await queue_manager.add_task(
                        "chat", 
                        process_chat_message, 
                        message=message, 
                        job_id=job_id, 
                        context=context
                    )
                
                elif payload.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received: {data}")
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)
