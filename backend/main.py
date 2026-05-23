import os
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from serial_manager import SerialManager
from session_manager import SessionManager

app = FastAPI(title="Microvibration Monitoring Backend")

# Allow CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Managers
serial_manager = SerialManager()
session_manager = SessionManager()

# Active websocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    serial_manager.connect()
    # Start the real data forwarding loop in background
    asyncio.create_task(serial_data_loop())

@app.on_event("shutdown")
async def shutdown_event():
    serial_manager.disconnect()

import time

last_broadcast_time = 0
BROADCAST_INTERVAL = 1.0 / 30.0  # 30 Hz

async def serial_data_loop():
    """Background task to broadcast real sensor data and save to session."""
    global last_broadcast_time
    batch = []

    while True:
        items = []
        while not serial_manager.data_queue.empty():
            items.append(serial_manager.data_queue.get_nowait())

        for data in items:
            # Always save all raw data to session
            if session_manager.active_session_id:
                session_manager.append_data(data["timestamp"], data["value"])
            batch.append(data)

        # Send 1 averaged point to frontend at 30 Hz
        current_time = time.time()
        if current_time - last_broadcast_time >= BROADCAST_INTERVAL and batch:
            avg_val = sum(p["value"] for p in batch) / len(batch)
            point = {"timestamp": batch[-1]["timestamp"], "value": avg_val}
            await manager.broadcast(json.dumps(point))
            batch = []
            last_broadcast_time = current_time

        await asyncio.sleep(0.005)

# --- REST API Endpoints ---

@app.get("/api/status")
def get_status():
    """Get the connection status of the ESP32."""
    return {
        "status": "online",
        "esp32_connected": serial_manager.is_connected,
        "active_session": session_manager.active_session_id
    }

class RateRequest(BaseModel):
    rate: str

@app.post("/api/sampling/start")
def sampling_start():
    """Send START command to ESP32."""
    success = serial_manager.send_command("START")
    if success:
        return {"message": "Command 'START' sent successfully."}
    return {"error": "Failed to send command."}, 500

@app.post("/api/sampling/stop")
def sampling_stop():
    """Send STOP command to ESP32."""
    success = serial_manager.send_command("STOP")
    if success:
        return {"message": "Command 'STOP' sent successfully."}
    return {"error": "Failed to send command."}, 500

@app.post("/api/sampling/rate")
def sampling_rate(req: RateRequest):
    """Send RATE command to ESP32."""
    # Ensure rate is 15K or 30K
    valid_rates = ["15K", "30K"]
    if req.rate not in valid_rates:
        return {"error": "Invalid rate"}, 400
        
    success = serial_manager.send_command(f"RATE:{req.rate}")
    if success:
        return {"message": f"Command 'RATE:{req.rate}' sent successfully."}
    return {"error": "Failed to send command."}, 500

@app.post("/api/session/start")
def start_session():
    """Start a new recording session."""
    session_id = session_manager.start_session()
    if not session_id:
        return {"error": "A session is already active."}, 400
    return {"message": "Session started", "session_id": session_id}

@app.post("/api/session/stop")
def stop_session():
    """Stop the current recording session."""
    session_id = session_manager.stop_session()
    if not session_id:
        return {"error": "No active session to stop."}, 400
    return {"message": "Session stopped", "session_id": session_id}

@app.get("/api/sessions")
def list_sessions():
    """List all recorded sessions."""
    sessions = session_manager.list_sessions()
    return {"sessions": sessions}

# --- WebSocket Endpoint ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data streaming."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
