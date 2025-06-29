"""WebSocket connection manager for real-time updates"""

import json
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections for real-time dashboard updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_times: Dict[WebSocket, datetime] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_times[websocket] = datetime.now()
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            self.connection_times.pop(websocket, None)
            print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        if not self.active_connections:
            return
            
        # Add timestamp to message
        message['server_timestamp'] = datetime.now().isoformat()
        message_json = json.dumps(message, default=str)
        
        # Send to all connections, removing failed ones
        failed_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                failed_connections.append(connection)
        
        # Clean up failed connections
        for connection in failed_connections:
            self.disconnect(connection)
    
    async def broadcast_reading(self, reading_data: Dict[str, Any]):
        """Broadcast a reactor reading to all clients"""
        await self.broadcast({
            "type": "reading",
            "data": reading_data
        })
    
    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        """Broadcast an anomaly alert to all clients"""
        await self.broadcast({
            "type": "alert",
            "data": alert_data
        })
    
    async def broadcast_status(self, status_data: Dict[str, Any]):
        """Broadcast system status to all clients"""
        await self.broadcast({
            "type": "status",
            "data": status_data
        })
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get information about current connections"""
        now = datetime.now()
        connections_info = []
        
        for ws, connect_time in self.connection_times.items():
            duration = (now - connect_time).total_seconds()
            connections_info.append({
                "connected_for_seconds": duration,
                "connect_time": connect_time.isoformat()
            })
        
        return {
            "total_connections": len(self.active_connections),
            "connections": connections_info
        }
