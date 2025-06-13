import React from 'react';
import DRLTrainingChart from './DRLTrainingChart';
import { Link } from 'react-router-dom';

// 假資料，可日後替換為API或Context數據
const trainingData = [
  { step: 1, reward: 10, loss: 0.5 },
  { step: 2, reward: 15, loss: 0.45 },
  { step: 3, reward: 18, loss: 0.4 },
  { step: 4, reward: 22, loss: 0.38 },
  { step: 5, reward: 25, loss: 0.35 },
  { step: 6, reward: 28, loss: 0.33 },
  { step: 7, reward: 30, loss: 0.3 },
  { step: 8, reward: 32, loss: 0.28 },
  { step: 9, reward: 33, loss: 0.27 },
  { step: 10, reward: 35, loss: 0.25 },
  { step: 11, reward: 37, loss: 0.22 },
  { step: 12, reward: 39, loss: 0.21 },
  { step: 13, reward: 40, loss: 0.2 },
  { step: 14, reward: 41, loss: 0.19 },
  { step: 15, reward: 42, loss: 0.18 }
];

const DRLTrainingPage = () => {
  // 僅使用本地假資料
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">DRL訓練詳細過程</h1>
          <p className="mt-1 text-sm text-gray-500">此頁面展示強化學習訓練過程的詳細指標與趨勢圖表。</p>
        </div>
        <Link to="/" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">返回儀表板</Link>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <DRLTrainingChart data={trainingData} />
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-bold text-gray-800 mb-4">訓練指標摘要</h2>
          <ul className="space-y-2 text-gray-700">
            <li>訓練步數：{trainingData.length}</li>
            <li>最高Reward：{trainingData.length > 0 ? Math.max(...trainingData.map(d => d.reward)) : '-'}</li>
            <li>最低Loss：{trainingData.length > 0 ? Math.min(...trainingData.map(d => d.loss)) : '-'}</li>
            <li>最終Reward：{trainingData.length > 0 ? trainingData[trainingData.length-1].reward : '-'}</li>
            <li>最終Loss：{trainingData.length > 0 ? trainingData[trainingData.length-1].loss : '-'}</li>
          </ul>
        </div>
      </div>
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-bold text-gray-800 mb-4">訓練數據表格</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">步數</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reward</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Loss</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {trainingData.map((row, idx) => (
                <tr key={idx}>
                  <td className="px-6 py-4 whitespace-nowrap">{row.step}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{row.reward}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{row.loss}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DRLTrainingPage;