import { Cpu, Play, Square, Settings2 } from 'lucide-react';
import { startSampling, stopSampling, setSamplingRate } from '../services/api';
import { useState } from 'react';
import './ControlPanel.css';

interface ControlPanelProps {
  esp32Connected: boolean;
}

export default function ControlPanel({ esp32Connected }: ControlPanelProps) {
  const [isSampling, setIsSampling] = useState(false);
  const [samplingRate, setRate] = useState('15K');

  const handleStart = async () => {
    try {
      await startSampling();
      setIsSampling(true);
    } catch (e) {
      console.error("Failed to start sampling", e);
    }
  };

  const handleStop = async () => {
    try {
      await stopSampling();
      setIsSampling(false);
    } catch (e) {
      console.error("Failed to stop sampling", e);
    }
  };

  const handleRateChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const rate = e.target.value;
    setRate(rate);
    try {
      await setSamplingRate(rate);
    } catch (err) {
      console.error("Failed to set rate", err);
    }
  };

  return (
    <div className="glass-panel control-panel">
      <div className="panel-header">
        <Cpu size={20} className="icon-blue" />
        <h2>Hardware Control</h2>
      </div>
      
      <p className="panel-desc">Control ESP32 ADS1256 sampling and configure settings.</p>
      
      <div className="control-group">
        <label className="control-label">
          <Settings2 size={14} /> Sampling Rate
        </label>
        <select 
          className="rate-select"
          value={samplingRate} 
          onChange={handleRateChange}
          disabled={!esp32Connected || isSampling}
        >
          <option value="15K">15k SPS</option>
          <option value="30K">30k SPS</option>
        </select>
      </div>

      <div className="button-group" style={{ marginTop: '1rem' }}>
        <button 
          className="btn btn-success" 
          onClick={handleStart}
          disabled={!esp32Connected || isSampling}
        >
          <Play size={16} /> Start
        </button>
        <button 
          className="btn btn-danger" 
          onClick={handleStop}
          disabled={!esp32Connected || !isSampling}
        >
          <Square size={16} /> Stop
        </button>
      </div>

      {!esp32Connected && (
        <div className="warning-text">ESP32 is not connected.</div>
      )}
    </div>
  );
}
