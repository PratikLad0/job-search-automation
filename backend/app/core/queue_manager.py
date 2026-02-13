import asyncio
import logging
import uuid
import traceback
from typing import Callable, Any, Dict, Optional
from datetime import datetime
from backend.app.core.websocket_manager import manager as ws_manager

logger = logging.getLogger("jobsearch.queue")

class AITask:
    """Represents a single task in the sequential queue."""
    def __init__(self, task_type: str, func: Callable, *args, **kwargs):
        self.id = str(uuid.uuid4())
        self.task_type = task_type
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.status = "queued"
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.finished_at: Optional[datetime] = None
        self.result: Any = None
        self.error: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.task_type,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "error": self.error
        }

class SequentialQueueManager:
    """
    Ensures exactly one AI task runs at a time.
    Broadcasts status updates to all connected WebSocket clients.
    """
    def __init__(self):
        self.queue = asyncio.Queue()
        self.current_task: Optional[AITask] = None
        self.history: Dict[str, AITask] = {}
        self._worker_task = None

    def start_worker(self):
        """Start the background worker if not already running."""
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._worker_loop())
            logger.info("Sequential Queue Worker started")

    async def add_task(self, task_type: str, func: Callable, *args, **kwargs) -> str:
        """Add a new task to the queue and return its ID."""
        task = AITask(task_type, func, *args, **kwargs)
        self.history[task.id] = task
        await self.queue.put(task)
        
        # Broadcast that a new task was queued
        await ws_manager.broadcast("task_queued", {
            "task": task.to_dict(),
            "queue_size": self.queue.qsize()
        })
        
        logger.info(f"Task {task.id} ({task_type}) added to queue. Position: {self.queue.qsize()}")
        return task.id

    async def _worker_loop(self):
        """The main loop that processes tasks one by one."""
        while True:
            try:
                # Get a task from the queue
                task = await self.queue.get()
                self.current_task = task
                task.status = "processing"
                task.started_at = datetime.now()
                
                # Broadcast that processing started
                await ws_manager.broadcast("task_started", {
                    "task": task.to_dict()
                })
                
                logger.info(f"Starting task {task.id} ({task.task_type})")
                
                try:
                    # Execute the function
                    if asyncio.iscoroutinefunction(task.func):
                        result = await task.func(*task.args, **task.kwargs)
                    else:
                        result = task.func(*task.args, **task.kwargs)
                    
                    task.status = "completed"
                    task.result = result
                except Exception as e:
                    logger.error(f"Error executing task {task.id}: {e}")
                    logger.error(traceback.format_exc())
                    task.status = "failed"
                    task.error = str(e)
                
                task.finished_at = datetime.now()
                
                # Broadcast completion/failure
                await ws_manager.broadcast("task_finished", {
                    "task": task.to_dict(),
                    "result": task.result if task.status == "completed" else None
                })
                
                self.current_task = None
                self.queue.task_done()
                
            except Exception as e:
                logger.error(f"Critical error in queue worker loop: {e}")
                await asyncio.sleep(1) # Prevent tight loop on error

# Global singleton instance
queue_manager = SequentialQueueManager()
