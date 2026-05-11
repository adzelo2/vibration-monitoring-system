import { Play, Square, List } from 'lucide-react';
import { useEffect, useState } from 'react';
import { startSession, stopSession, listSessions } from '../services/api';
import './SessionManager.css';

interface SessionManagerProps {
  activeSession: string | null;
  onSessionChange: (status: any) => void;
}

export default function SessionManager({ activeSession, onSessionChange }: SessionManagerProps) {
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchSessions = async () => {
    try {
      const data = await listSessions();
      setSessions(data.sessions);
    } catch (e) {
      console.error("Failed to fetch sessions", e);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [activeSession]);

  const handleStart = async () => {
    setLoading(true);
    try {
      const res = await startSession();
      onSessionChange({ active_session: res.session_id });
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      await stopSession();
      onSessionChange({ active_session: null });
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  return (
    <div className="glass-panel session-manager">
      <div className="panel-header">
        <List size={20} className="icon-blue" />
        <h2>Session Recording</h2>
      </div>

      <div className="session-controls">
        {activeSession ? (
          <div className="active-session-info">
            <span className="status-indicator status-recording"></span>
            Recording: {activeSession}
          </div>
        ) : (
          <div className="inactive-session-info">Ready to record</div>
        )}

        <div className="button-row">
          <button 
            className="btn btn-success" 
            onClick={handleStart} 
            disabled={activeSession !== null || loading}
          >
            <Play size={16} /> Start
          </button>
          <button 
            className="btn btn-danger" 
            onClick={handleStop} 
            disabled={activeSession === null || loading}
          >
            <Square size={16} /> Stop
          </button>
        </div>
      </div>

      <div className="session-list-container">
        <h3>Recent Sessions</h3>
        {sessions.length === 0 ? (
          <p className="no-sessions">No sessions recorded yet.</p>
        ) : (
          <ul className="session-list">
            {sessions.map((s) => (
              <li key={s.session_id} className="session-item">
                <div className="session-id">{s.session_id}</div>
                <div className="session-time">{new Date(s.start_time).toLocaleString()}</div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
