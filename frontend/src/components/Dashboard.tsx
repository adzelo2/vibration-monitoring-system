import { Activity } from 'lucide-react';
import './Dashboard.css';
import ControlPanel from './ControlPanel.tsx';
import SensorStatus from './SensorStatus.tsx';
import SessionManager from './SessionManager.tsx';
import RealTimeChart from './RealTimeChart.tsx';
import { useEffect, useState, useRef } from 'react';
import { getSystemStatus, createWebSocketConnection } from '../services/api';

export default function Dashboard() {
  const [systemStatus, setSystemStatus] = useState<any>({
    status: 'offline',
    esp32_connected: false,
    active_session: null
  });
  const [wsConnected, setWsConnected] = useState(false);
  const [chartData, setChartData] = useState<{ timestamp: number, value: number }[]>([]);
  const MAX_DATA_POINTS = 300;

  const chartDataRef = useRef(chartData);

  useEffect(() => {
    chartDataRef.current = chartData;
  }, [chartData]);

  useEffect(() => {
    // Initial status fetch
    const fetchStatus = async () => {
      try {
        const status = await getSystemStatus();
        setSystemStatus(status);
      } catch (e) {
        console.error("Failed to fetch status", e);
      }
    };

    fetchStatus();
    const statusInterval = setInterval(fetchStatus, 5000);

    // WebSocket setup
    const ws = createWebSocketConnection((data) => {
      setChartData((prev) => {
        const newData = [...prev, data];
        if (newData.length > MAX_DATA_POINTS) {
          return newData.slice(newData.length - MAX_DATA_POINTS);
        }
        return newData;
      });
    });

    ws.onopen = () => setWsConnected(true);
    ws.onclose = () => setWsConnected(false);

    return () => {
      clearInterval(statusInterval);
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  return (
    <div className="app-container">
      <header className="topbar">
        <h1>
          <Activity size={24} color="var(--accent-primary)" />
          Microvibration Monitoring
        </h1>
        <div className="status-badges">
          <div className="status-badge">
            <span className={`status-indicator ${wsConnected ? 'status-online' : 'status-offline'}`}></span>
            Backend: {wsConnected ? 'Connected' : 'Disconnected'}
          </div>
          <div className="status-badge">
            <span className={`status-indicator ${systemStatus.esp32_connected ? 'status-online' : 'status-offline'}`}></span>
            ESP32: {systemStatus.esp32_connected ? 'Connected' : 'Disconnected'}
          </div>
        </div>
      </header>

      <main className="main-content">
        <div className="dashboard-grid">
          <aside className="sidebar">
            <ControlPanel esp32Connected={systemStatus.esp32_connected} />
            <SessionManager
              activeSession={systemStatus.active_session}
              onSessionChange={(status) => setSystemStatus({ ...systemStatus, ...status })}
            />
          </aside>
          <section className="content-area">
            <SensorStatus />
            <RealTimeChart data={chartData} />
          </section>
        </div>
      </main>
    </div>
  );
}
