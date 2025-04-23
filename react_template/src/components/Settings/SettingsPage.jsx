import React, { useState } from 'react';
import { useAppContext } from '../../context/AppContext';
import { getEbayCategoriesTree } from '../../services/ebayService';

const SettingsPage = () => {
  const { settings, updateSettings } = useAppContext();
  const [formData, setFormData] = useState({ ...settings });
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  
  const handleSave = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveMessage('');
    
    try {
      // In a real app, this might validate API keys with the backend
      updateSettings(formData);
      
      setSaveMessage('設置已成功儲存');
      setTimeout(() => setSaveMessage(''), 3000);
    } catch (error) {
      console.error('Error saving settings:', error);
      setSaveMessage('儲存設置時發生錯誤');
    } finally {
      setIsSaving(false);
    }
  };
  
  const handleTestApiKey = async () => {
    setIsSaving(true);
    setSaveMessage('');
    
    try {
      // In a real app, this would validate the API key with eBay
      const categories = await getEbayCategoriesTree(formData.ebayApiKey);
      if (categories.length > 0) {
        setSaveMessage('API金鑰驗證成功！');
      } else {
        setSaveMessage('API金鑰驗證失敗，請檢查您的金鑰');
      }
    } catch (error) {
      console.error('Error testing API key:', error);
      setSaveMessage('API金鑰驗證失敗，請檢查您的金鑰或網絡連接');
    } finally {
      setIsSaving(false);
    }
  };
  
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-800">系統設置</h1>
        <p className="mt-1 text-sm text-gray-500">
          自定義分析和預測設置，管理 API 金鑰
        </p>
      </div>
      
      {/* Settings Form */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <form onSubmit={handleSave}>
          {/* General Settings Section */}
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900 mb-4">一般設置</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Default Category */}
              <div>
                <label htmlFor="defaultCategory" className="block text-sm font-medium text-gray-700 mb-1">
                  預設商品類別
                </label>
                <select
                  id="defaultCategory"
                  name="defaultCategory"
                  value={formData.defaultCategory}
                  onChange={handleChange}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                >
                  <option value="">無預設類別</option>
                  <option value="electronics">電子產品</option>
                  <option value="clothing">服飾</option>
                  <option value="home">家居用品</option>
                  <option value="toys">玩具與嗜好</option>
                  <option value="sports">運動與戶外</option>
                </select>
              </div>
              
              {/* Preferred Price Strategy */}
              <div>
                <label htmlFor="preferredPriceStrategy" className="block text-sm font-medium text-gray-700 mb-1">
                  預設定價策略
                </label>
                <select
                  id="preferredPriceStrategy"
                  name="preferredPriceStrategy"
                  value={formData.preferredPriceStrategy}
                  onChange={handleChange}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                >
                  <option value="recommended">建議價格（平衡）</option>
                  <option value="fast">快速銷售</option>
                  <option value="profit">最大利潤</option>
                </select>
              </div>
              
              {/* Confidence Threshold Slider */}
              <div className="md:col-span-2">
                <label htmlFor="confidenceThreshold" className="block text-sm font-medium text-gray-700 mb-1">
                  信心度閾值: {formData.confidenceThreshold}%
                </label>
                <input
                  type="range"
                  id="confidenceThreshold"
                  name="confidenceThreshold"
                  min="50"
                  max="95"
                  step="5"
                  value={formData.confidenceThreshold}
                  onChange={handleChange}
                  className="block w-full"
                />
                <p className="mt-1 text-xs text-gray-500">
                  低於此閾值的預測結果將顯示警告
                </p>
              </div>
            </div>
            
            {/* Display Options */}
            <div className="mt-6">
              <h3 className="text-sm font-medium text-gray-900 mb-2">顯示選項</h3>
              
              <div className="space-y-3">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="showMarketInsights"
                    name="showMarketInsights"
                    checked={formData.showMarketInsights}
                    onChange={handleChange}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <label htmlFor="showMarketInsights" className="ml-2 block text-sm text-gray-700">
                    顯示市場洞察
                  </label>
                </div>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="notifyPriceDrops"
                    name="notifyPriceDrops"
                    checked={formData.notifyPriceDrops}
                    onChange={handleChange}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <label htmlFor="notifyPriceDrops" className="ml-2 block text-sm text-gray-700">
                    價格下降通知
                  </label>
                </div>
              </div>
            </div>
          </div>
          
          {/* API Settings Section */}
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900 mb-4">API 設置</h2>
            
            <div>
              <label htmlFor="ebayApiKey" className="block text-sm font-medium text-gray-700 mb-1">
                eBay API 金鑰
              </label>
              <div className="mt-1 flex rounded-md shadow-sm">
                <input
                  type="password"
                  id="ebayApiKey"
                  name="ebayApiKey"
                  value={formData.ebayApiKey}
                  onChange={handleChange}
                  className="flex-1 min-w-0 block w-full px-3 py-2 rounded-none rounded-l-md border-gray-300 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="Enter your API key"
                />
                <button
                  type="button"
                  className="inline-flex items-center px-3 py-2 border border-l-0 border-gray-300 bg-gray-50 text-gray-500 text-sm rounded-r-md hover:bg-gray-100 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
                  onClick={handleTestApiKey}
                  disabled={isSaving}
                >
                  測試
                </button>
              </div>
              <p className="mt-1 text-xs text-gray-500">
                用於獲取 eBay 市場數據的 API 金鑰。
                <button 
                  type="button" 
                  className="text-indigo-600 hover:text-indigo-500 ml-1"
                  onClick={() => setShowApiKeyModal(true)}
                >
                  如何獲取？
                </button>
              </p>
            </div>
          </div>
          
          {/* App Preferences */}
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900 mb-4">應用偏好</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="theme" className="block text-sm font-medium text-gray-700 mb-1">
                  介面主題
                </label>
                <select
                  id="theme"
                  name="theme"
                  value={formData.theme}
                  onChange={handleChange}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                >
                  <option value="light">淺色</option>
                  <option value="dark">深色</option>
                  <option value="system">跟隨系統</option>
                </select>
              </div>
              
              <div>
                <label htmlFor="language" className="block text-sm font-medium text-gray-700 mb-1">
                  語言
                </label>
                <select
                  id="language"
                  name="language"
                  value={formData.language}
                  onChange={handleChange}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                >
                  <option value="zh-TW">繁體中文</option>
                  <option value="en-US">English (US)</option>
                </select>
              </div>
            </div>
          </div>
          
          {/* Form Actions */}
          <div className="px-6 py-4 bg-gray-50 flex items-center justify-between">
            {saveMessage && (
              <span className={`text-sm ${saveMessage.includes('成功') ? 'text-green-600' : 'text-red-600'}`}>
                {saveMessage}
              </span>
            )}
            
            <div className="flex space-x-3">
              <button
                type="button"
                className="px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                onClick={() => setFormData({ ...settings })}
              >
                重置
              </button>
              <button
                type="submit"
                className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                disabled={isSaving}
              >
                {isSaving ? '儲存中...' : '儲存設置'}
              </button>
            </div>
          </div>
        </form>
      </div>
      
      {/* API Key Help Modal */}
      {showApiKeyModal && (
        <div className="fixed z-10 inset-0 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" aria-hidden="true">
              <div className="absolute inset-0 bg-gray-500 opacity-75" onClick={() => setShowApiKeyModal(false)}></div>
            </div>
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div>
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-2">
                    如何獲取 eBay API 金鑰
                  </h3>
                  <div className="mt-2">
                    <ol className="list-decimal pl-5 space-y-2 text-sm text-gray-700">
                      <li>前往 <a href="https://developer.ebay.com" target="_blank" rel="noreferrer" className="text-indigo-600 hover:text-indigo-500">eBay Developers Program</a> 並創建帳戶</li>
                      <li>登入後，進入 "My Account" 頁面</li>
                      <li>選擇 "Get a User Token" 以創建一個新的應用程序</li>
                      <li>填寫必要的應用程序資訊</li>
                      <li>選擇所需的 API 範圍 (需要包括 "Finding API")</li>
                      <li>生成並複製您的 API 金鑰</li>
                    </ol>
                    <p className="mt-4 text-sm text-gray-500">
                      注意：在真實的生產環境中，API 金鑰應該存儲在服務器端，而不是客戶端。此示例僅為展示目的。
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={() => setShowApiKeyModal(false)}
                >
                  了解
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SettingsPage;