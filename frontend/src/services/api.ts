import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000/ws';

export const api = axios.create({
  baseURL: API_URL,
});

export const getSystemStatus = async () => {
  const response = await api.get('/status');
  return response.data;
};

export const turnGpioOn = async () => {
  const response = await api.post('/gpio/on');
  return response.data;
};

export const turnGpioOff = async () => {
  const response = await api.post('/gpio/off');
  return response.data;
};

export const startSession = async () => {
  const response = await api.post('/session/start');
  return response.data;
};

export const stopSession = async () => {
  const response = await api.post('/session/stop');
  return response.data;
};

export const listSessions = async () => {
  const response = await api.get('/sessions');
  return response.data;
};

export const createWebSocketConnection = (onMessage: (data: any) => void) => {
  const ws = new WebSocket(WS_URL);
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (e) {
      console.error("Failed to parse websocket message", e);
    }
  };

  return ws;
};
