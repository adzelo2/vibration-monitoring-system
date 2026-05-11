import PlotlyChart from 'react-plotly.js';
const Plot = (PlotlyChart as any).default || PlotlyChart;
import { Activity } from 'lucide-react';
import './RealTimeChart.css';

interface RealTimeChartProps {
  data: { timestamp: number; value: number }[];
}

export default function RealTimeChart({ data }: RealTimeChartProps) {
  // Convert array of objects to arrays for Plotly
  const x = data.map(d => new Date(d.timestamp * 1000));
  const y = data.map(d => d.value);


  return (
    <div className="glass-panel chart-container">
      <div className="panel-header">
        <Activity size={20} className="icon-blue" />
        <h2>Real-Time Vibration Data</h2>
      </div>

      <div className="plot-wrapper">
        <Plot
          data={[
            {
              x: x,
              y: y,
              type: 'scatter',
              mode: 'lines',
              line: { color: '#3b82f6', width: 2 },
              fill: 'tozeroy',
              fillcolor: 'rgba(59, 130, 246, 0.1)',
            },
          ]}
          layout={{
            autosize: true,
            margin: { t: 10, r: 10, l: 40, b: 30 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#94a3b8', family: 'Inter' },
            xaxis: {
              showgrid: true,
              gridcolor: 'rgba(255,255,255,0.05)',
              zeroline: false,
              type: 'date',
            },
            yaxis: {
              showgrid: true,
              gridcolor: 'rgba(255,255,255,0.05)',
              zeroline: true,
              zerolinecolor: 'rgba(255,255,255,0.1)',
              range: [-2, 2], // Fix range to simulate sensor limits
            },
            hovermode: 'closest'
          }}
          useResizeHandler={true}
          style={{ width: '100%', height: '100%' }}
          config={{ displayModeBar: false, responsive: true }}
        />

        {data.length === 0 && (
          <div className="chart-placeholder">
            Waiting for data stream...
          </div>
        )}
      </div>
    </div>
  );
}
