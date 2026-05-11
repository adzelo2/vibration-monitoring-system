import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from serial_manager import SerialManager
from session_manager import SessionManager
from mock_sensor import MockSensorStream

app = FastAPI(title="Microvibration Monitoring Backend")

# Allow CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Managers
serial_manager = SerialManager()
session_manager = SessionManager()
mock_sensor = MockSensorStream()

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
    # Start the mock data generation loop in background
    asyncio.create_task(mock_sensor_loop())

@app.on_event("shutdown")
async def shutdown_event():
    serial_manager.disconnect()

async def mock_sensor_loop():
    """Background task to broadcast mock sensor data and save to session if active."""
    while True:
        data_json = mock_sensor.get_next_reading()
        await manager.broadcast(data_json)
        
        # If a session is active, record the data
        if session_manager.active_session_id:
            import json
            data = json.loads(data_json)
            session_manager.append_data(data["timestamp"], data["value"])
            
        await asyncio.sleep(0.05)  # 20 Hz mock rate

# --- REST API Endpoints ---

@app.get("/api/status")
def get_status():
    """Get the connection status of the ESP32."""
    print(f"DEBUG /api/status: is_connected={serial_manager.is_connected}")
    return {
        "status": "online",
        "esp32_connected": serial_manager.is_connected,
        "active_session": session_manager.active_session_id
    }

@app.post("/api/gpio/on")
def gpio_on():
    """Send ON command to ESP32 to turn on GPIO 14."""
    success = serial_manager.send_command("ON")
    if success:
        return {"message": "Command 'ON' sent successfully."}
    return {"error": "Failed to send command. Is ESP32 connected?"}, 500

@app.post("/api/gpio/off")
def gpio_off():
    """Send OFF command to ESP32 to turn off GPIO 14."""
    success = serial_manager.send_command("OFF")
    if success:
        return {"message": "Command 'OFF' sent successfully."}
    return {"error": "Failed to send command. Is ESP32 connected?"}, 500

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
            # Keep connection open, client might send pings
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
