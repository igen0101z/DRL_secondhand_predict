import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getMockDashboardData } from '../../services/mockData';
import { formatCurrency, formatDate } from '../../utils/helpers';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        // In a real application, this would fetch from an API
        const data = getMockDashboardData();
        setDashboardData(data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-red-500">無法載入儀表板數據，請稍後再試。</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-800">儀表板</h1>
        <p className="mt-1 text-sm text-gray-500">
          歡迎使用二手價格預測系統。查看最新統計數據和預測記錄。
        </p>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="總預測項目"
          value={dashboardData.totalItems}
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          }
        />
        
        <StatCard 
          title="平均準確度"
          value={`${dashboardData.averageAccuracy}%`}
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
          }
        />
        
        <StatCard 
          title="平均價格差異"
          value={formatCurrency(dashboardData.averagePriceDifference)}
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
        
        <StatCard 
          title="平均銷售時間"
          value={`${dashboardData.averageSaleTime} 天`}
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
      </div>
      
      {/* Recent Items */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">最近分析項目</h3>
        </div>
        
        <div className="divide-y divide-gray-200">
          {dashboardData.recentItems.length > 0 ? (
            dashboardData.recentItems.map((item) => (
              <RecentItemCard key={item.id} item={item} />
            ))
          ) : (
            <div className="p-6 text-center">
              <p className="text-gray-500">尚未有分析項目。</p>
              <Link 
                to="/product-analysis" 
                className="mt-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
              >
                開始新的分析
              </Link>
            </div>
          )}
        </div>
        
        {dashboardData.recentItems.length > 0 && (
          <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
            <Link to="/history" className="text-sm font-medium text-indigo-600 hover:text-indigo-500 flex items-center">
              查看所有歷史記錄
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-1" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            </Link>
          </div>
        )}
      </div>
      
      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">快速操作</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Link 
            to="/product-analysis" 
            className="bg-indigo-50 hover:bg-indigo-100 p-4 rounded-lg flex items-center space-x-3 transition-colors"
          >
            <div className="bg-indigo-100 rounded-lg p-3">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-900">新增分析</h4>
              <p className="text-xs text-gray-500">開始新的價格分析預測</p>
            </div>
          </Link>
          
          <Link 
            to="/history" 
            className="bg-purple-50 hover:bg-purple-100 p-4 rounded-lg flex items-center space-x-3 transition-colors"
          >
            <div className="bg-purple-100 rounded-lg p-3">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-900">歷史紀錄</h4>
              <p className="text-xs text-gray-500">查看過去的所有分析</p>
            </div>
          </Link>
          
          <Link 
            to="/settings" 
            className="bg-blue-50 hover:bg-blue-100 p-4 rounded-lg flex items-center space-x-3 transition-colors"
          >
            <div className="bg-blue-100 rounded-lg p-3">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-900">系統設置</h4>
              <p className="text-xs text-gray-500">自定義預測和分析設置</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
};

// Stat Card Component
const StatCard = ({ title, value, icon }) => {
  return (
    <div className="bg-white shadow rounded-lg p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-2xl font-semibold text-gray-900 mt-1">{value}</p>
        </div>
        <div className="bg-indigo-50 rounded-lg p-2">
          <div className="text-indigo-500">
            {icon}
          </div>
        </div>
      </div>
    </div>
  );
};

// Recent Item Card Component
const RecentItemCard = ({ item }) => {
  const priceStatus = item.suggestedPrice > item.marketPrice 
    ? { color: 'text-red-600', icon: '↓' } 
    : { color: 'text-green-600', icon: '↑' };
  
  const priceDiff = Math.abs(item.suggestedPrice - item.marketPrice);
  const diffPercentage = ((priceDiff / item.marketPrice) * 100).toFixed(1);
  
  return (
    <Link to={`/price-prediction/${item.id}`} className="block hover:bg-gray-50 transition-colors">
      <div className="px-6 py-4 flex items-center">
        <div className="flex-shrink-0 h-16 w-16">
          <img 
            className="h-16 w-16 rounded-md object-cover" 
            src={item.imageUrl} 
            alt={item.name} 
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = "https://via.placeholder.com/64?text=No+Image";
            }}
          />
        </div>
        
        <div className="ml-4 flex-1">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium text-gray-900">{item.name}</h4>
            <span className="text-xs text-gray-500">{formatDate(item.analysisDate)}</span>
          </div>
          
          <div className="mt-1">
            <span className="text-xs text-gray-500">{item.category} · {item.condition}</span>
          </div>
          
          <div className="mt-2 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">建議價格:</span>
              <span className="text-sm font-medium">{formatCurrency(item.suggestedPrice)}</span>
            </div>
            
            <div className="flex items-center">
              <span className="text-sm text-gray-500 mr-2">市場價格比較:</span>
              <span className={`text-sm font-medium ${priceStatus.color}`}>
                {priceStatus.icon} {diffPercentage}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default Dashboard;