# Microvibration Measurement System

This is a full-stack monorepo for a microvibration measurement system utilizing an ESP32 for hardware interfacing, a Python FastAPI backend for serial communication and session management, and a React frontend for real-time monitoring and control.

## Architecture

The system consists of three main components:
1. **Frontend (React + Vite + TypeScript)**: A premium dark-mode dashboard for real-time data visualization and hardware control.
2. **Backend (Python FastAPI)**: Handles REST API requests, WebSocket data streaming, session recording (CSV/JSON), and serial communication with the ESP32.
3. **Firmware (MicroPython)**: ESP32 script currently acting as a GPIO test stub, with plans to integrate an ADS1256 ADC for real vibration sensing.

See `docs/architecture.md` for a detailed architecture diagram.

## Prerequisites
- Node.js (v18+)
- Python (3.10+)
- Thonny IDE (for flashing ESP32)

## Setup & Running Locally

### 1. Backend

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

Set the COM port for your ESP32. You can create a `.env` file in the `backend/` directory:
```env
ESP32_PORT=COM7
```

Start the backend:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Firmware

1. Connect your ESP32.
2. Open Thonny IDE.
3. Open `firmware/main.py` and save it to the ESP32 as `main.py`.
4. The script will start automatically on boot, listening to serial commands.

## Future Plans
- Integrate ADS1256 for high-precision ADC reading.
- Stream real sensor data from ESP32 to the backend.
- Implement real-time FFT analysis in the backend.
