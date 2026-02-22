import logging
from typing import List
from fastapi import WebSocket

logger = logging.getLogger("jobsearch.ws")

class WebSocketManager:
    """
    Manages global WebSocket connections and provides broadcasting capabilities.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: dict):
        """
        Send an event to all connected clients.
        
        Args:
            event_type: String identifier for the event (e.g., 'chat_message', 'task_update')
            data: Dictionary containing the event payload
        """
        if not self.active_connections:
            return

        message = {
            "type": event_type,
            "data": data
        }
        
        logger.debug(f"Broadcasting {event_type} to {len(self.active_connections)} clients")
        
        # Create a list of dead connections to remove
        dead_connections = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send message to a connection: {e}")
                dead_connections.append(connection)
        
        # Clean up dead connections
        for dead in dead_connections:
            self.disconnect(dead)

# Global singleton instance
manager = WebSocketManager()
