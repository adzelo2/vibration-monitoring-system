import { LockKeyhole } from 'lucide-react';
import './SensorStatus.css';

export default function SensorStatus() {
  return (
    <div className="sensor-status-banner">
      <div className="banner-icon">
        <LockKeyhole size={24} />
      </div>
      <div className="banner-content">
        <h3>Sensor System Locked</h3>
        <p>Sensor system not active yet (ESP32 only in GPIO test mode). The chart below displays mock data for UI demonstration purposes until the ADS1256 is integrated.</p>
      </div>
    </div>
  );
}
