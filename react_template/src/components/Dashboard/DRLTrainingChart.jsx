import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// props: data=[{step: 1, reward: 10, loss: 0.5}, ...]
const DRLTrainingChart = ({ data }) => {
  return (
    <div className="bg-white shadow rounded-lg p-6 mb-6">
      <h2 className="text-lg font-bold text-gray-800 mb-4">DRL訓練過程</h2>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="step" label={{ value: '訓練步數', position: 'insideBottomRight', offset: -5 }} />
          <YAxis yAxisId="left" label={{ value: 'Reward', angle: -90, position: 'insideLeft' }} />
          <YAxis yAxisId="right" orientation="right" label={{ value: 'Loss', angle: 90, position: 'insideRight' }} />
          <Tooltip />
          <Legend />
          <Line yAxisId="left" type="monotone" dataKey="reward" stroke="#4F46E5" name="Reward" dot={false} />
          <Line yAxisId="right" type="monotone" dataKey="loss" stroke="#F59E42" name="Loss" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default DRLTrainingChart;