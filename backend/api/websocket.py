from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import asyncio
from datetime import datetime

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.chat_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if chat_id:
            if chat_id not in self.chat_connections:
                self.chat_connections[chat_id] = []
            self.chat_connections[chat_id].append(websocket)

    def disconnect(self, websocket: WebSocket, chat_id: str = None):
        self.active_connections.remove(websocket)
        if chat_id and chat_id in self.chat_connections:
            self.chat_connections[chat_id].remove(websocket)
            if not self.chat_connections[chat_id]:
                del self.chat_connections[chat_id]

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, chat_id: str = None):
        if chat_id and chat_id in self.chat_connections:
            connections = self.chat_connections[chat_id]
        else:
            connections = self.active_connections
        
        for connection in connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/chat/{chat_id}")
async def websocket_chat(websocket: WebSocket, chat_id: str):
    await manager.connect(websocket, chat_id)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Echo back to sender
            await manager.send_message(json.dumps({
                "type": "user_message",
                "data": message_data,
                "timestamp": datetime.now().isoformat()
            }), websocket)
            
            # Simulate AI response with streaming
            if message_data.get("type") == "chat_message":
                response_text = f"これは'{message_data.get('content', '')}'に対するストリーミング応答です。"
                
                # Send start of response
                await manager.send_message(json.dumps({
                    "type": "ai_response_start",
                    "timestamp": datetime.now().isoformat()
                }), websocket)
                
                # Stream response character by character
                for i, char in enumerate(response_text):
                    await manager.send_message(json.dumps({
                        "type": "ai_response_chunk",
                        "content": char,
                        "index": i,
                        "timestamp": datetime.now().isoformat()
                    }), websocket)
                    await asyncio.sleep(0.05)  # Simulate typing delay
                
                # Send end of response
                await manager.send_message(json.dumps({
                    "type": "ai_response_end",
                    "timestamp": datetime.now().isoformat()
                }), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, chat_id)
        await manager.broadcast(json.dumps({
            "type": "user_disconnected",
            "chat_id": chat_id,
            "timestamp": datetime.now().isoformat()
        }), chat_id)

@router.websocket("/notifications")
async def websocket_notifications(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle notification subscriptions
            # In a real app, this would manage notification preferences
            await manager.send_message(json.dumps({
                "type": "notification_ack",
                "timestamp": datetime.now().isoformat()
            }), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)