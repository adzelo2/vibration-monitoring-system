# Architecture Overview

```mermaid
graph TD
    subgraph Frontend [React + Vite Dashboard]
        UI[UI Components]
        WS_Client[WebSocket Client]
        REST_Client[REST Client]
        
        UI --> WS_Client
        UI --> REST_Client
    end

    subgraph Backend [FastAPI Backend]
        API[REST API Endpoints]
        WS_Server[WebSocket Server]
        SM[Session Manager]
        Serial[Serial Manager]
        Mock[Mock Sensor Data]
        FFT[Signal Processing / FFT Placeholder]
        
        REST_Client -->|HTTP POST/GET| API
        WS_Client <-->|WebSocket Stream| WS_Server
        
        API --> SM
        API --> Serial
        Mock --> WS_Server
        Serial --> WS_Server
    end

    subgraph Storage [Local File System]
        CSV[raw_data.csv]
        JSON[metadata.json]
        
        SM -->|Writes| CSV
        SM -->|Writes| JSON
    end

    subgraph Hardware [ESP32 MicroPython]
        MainLoop[Serial Read Loop]
        GPIO[GPIO 14 Control]
        ADC[Future: ADS1256 ADC]
        
        Serial <-->|USB Serial COM7| MainLoop
        MainLoop --> GPIO
    end
```

## Data Flow
1. **Hardware Control**: The user clicks a button on the React frontend. A REST POST request is sent to the FastAPI backend. The backend `SerialManager` sends the command string ("ON" or "OFF") over the serial port to the ESP32. The ESP32 parses the string and toggles GPIO 14.
2. **Real-time Streaming**: The React frontend establishes a WebSocket connection to the FastAPI backend. Currently, the backend streams mock data generated at a fixed interval. In the future, this data will come directly from the `SerialManager` reading from the ESP32.
3. **Session Recording**: When a session is started via the frontend, the backend creates a new folder in `recordings/`. It begins appending incoming data points to a `raw_data.csv` file and saves session metadata to a `metadata.json` file.
