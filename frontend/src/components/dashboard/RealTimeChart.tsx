'use client';

import {
  AreaChart,
  Area,
  ResponsiveContainer,
  YAxis
} from 'recharts';

interface RealTimeChartProps {
  data: any[];
  dataKey: string;
  baseColor: string;
  height?: number;
}

export function RealTimeChart({ data, dataKey, baseColor, height = 40 }: RealTimeChartProps) {
  // Recharts expects chronological data from left to right.
  // Our alert store keeps newest at index 0, so we must reverse a copy.
  const chartData = [...data].reverse();

  if (chartData.length === 0) {
    return (
      <div style={{ height, width: '100%', opacity: 0.1, background: baseColor, borderRadius: 4 }} />
    );
  }

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 2, right: 0, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id={`color${dataKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={baseColor} stopOpacity={0.4} />
              <stop offset="95%" stopColor={baseColor} stopOpacity={0} />
            </linearGradient>
          </defs>
          <YAxis domain={['dataMin', 'dataMax']} hide />
          <Area
            type="monotone"
            dataKey={dataKey}
            stroke={baseColor}
            strokeWidth={2}
            fillOpacity={1}
            fill={`url(#color${dataKey})`}
            isAnimationActive={false} // Disable animation for true real-time feel
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
