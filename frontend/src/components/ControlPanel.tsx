import { Cpu, Power, ZapOff } from 'lucide-react';
import { turnGpioOn, turnGpioOff } from '../services/api';
import './ControlPanel.css';

interface ControlPanelProps {
  esp32Connected: boolean;
}

export default function ControlPanel({ esp32Connected }: ControlPanelProps) {
  const handleOn = async () => {
    try {
      await turnGpioOn();
    } catch (e) {
      console.error("Failed to turn ON", e);
    }
  };

  const handleOff = async () => {
    try {
      await turnGpioOff();
    } catch (e) {
      console.error("Failed to turn OFF", e);
    }
  };

  return (
    <div className="glass-panel control-panel">
      <div className="panel-header">
        <Cpu size={20} className="icon-blue" />
        <h2>Hardware Control</h2>
      </div>
      
      <p className="panel-desc">Test the ESP32 connection by toggling GPIO 14.</p>
      
      <div className="button-group">
        <button 
          className="btn btn-success" 
          onClick={handleOn}
          disabled={!esp32Connected}
        >
          <Power size={16} /> GPIO 14 ON
        </button>
        <button 
          className="btn btn-danger" 
          onClick={handleOff}
          disabled={!esp32Connected}
        >
          <ZapOff size={16} /> GPIO 14 OFF
        </button>
      </div>

      {!esp32Connected && (
        <div className="warning-text">ESP32 is not connected. Commands will be mocked.</div>
      )}
    </div>
  );
}
