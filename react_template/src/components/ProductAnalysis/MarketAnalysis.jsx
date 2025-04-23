import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAppContext } from '../../context/AppContext';
import { formatCurrency, formatDate } from '../../utils/helpers';

const MarketAnalysis = () => {
  const { id } = useParams();
  const { history } = useAppContext();
  const [item, setItem] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [timeframeFilter, setTimeframeFilter] = useState('30days'); // 7days, 30days, 90days, 1year
  const [categoryFilter, setCategoryFilter] = useState('all'); // all, same, similar
  const [priceRangeFilter, setPriceRangeFilter] = useState('all'); // all, lower, similar, higher

  useEffect(() => {
    // Find the item in history using the id from URL params
    const foundItem = history.find(item => item.id === id);
    
    if (foundItem) {
      setItem(foundItem);
    }
    
    setIsLoading(false);
  }, [id, history]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (!item) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="text-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">找不到市場分析資料</h3>
          <p className="text-gray-500 mb-6">
            無法找到此 ID 的商品分析。該分析可能已被刪除，或連結無效。
          </p>
          <div className="flex justify-center space-x-3">
            <Link
              to="/product-analysis"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
            >
              新增分析
            </Link>
            <Link
              to="/history"
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50"
            >
              查看歷史記錄
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const results = item.analysisResults;
  
  // Filter similar items based on the selected filters
  const filteredSimilarItems = results.similarItems.filter(similarItem => {
    // Time filter
    const itemDate = new Date(similarItem.saleDate);
    const now = new Date();
    const daysDiff = Math.ceil((now - itemDate) / (1000 * 60 * 60 * 24));
    
    if (timeframeFilter === '7days' && daysDiff > 7) return false;
    if (timeframeFilter === '30days' && daysDiff > 30) return false;
    if (timeframeFilter === '90days' && daysDiff > 90) return false;
    if (timeframeFilter === '1year' && daysDiff > 365) return false;
    
    // Category filter
    if (categoryFilter === 'same' && similarItem.category !== item.category) return false;
    if (categoryFilter === 'similar' && !similarItem.category.includes(item.category.split(' ')[0])) return false;
    
    // Price range filter
    const recommendedPrice = results.recommendedPrice;
    if (priceRangeFilter === 'lower' && similarItem.price > recommendedPrice * 0.9) return false;
    if (priceRangeFilter === 'similar' && (similarItem.price < recommendedPrice * 0.9 || similarItem.price > recommendedPrice * 1.1)) return false;
    if (priceRangeFilter === 'higher' && similarItem.price < recommendedPrice * 1.1) return false;
    
    return true;
  });
  
  // Calculate market statistics based on filtered items
  const calculateStats = (items) => {
    if (items.length === 0) return { avg: 0, min: 0, max: 0, count: 0 };
    
    const prices = items.map(item => item.price);
    return {
      avg: prices.reduce((a, b) => a + b, 0) / prices.length,
      min: Math.min(...prices),
      max: Math.max(...prices),
      count: items.length
    };
  };
  
  const filteredStats = calculateStats(filteredSimilarItems);

  return (
    <div className="space-y-6">
      {/* Page Header with Item Info */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-start">
        <div>
          <div className="flex items-center">
            <Link to={`/price-prediction/${id}`} className="text-indigo-600 hover:text-indigo-500 mr-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clipRule="evenodd" />
              </svg>
            </Link>
            <h1 className="text-2xl font-bold text-gray-800">市場分析 - {item.name}</h1>
          </div>
          <div className="mt-1 flex flex-wrap items-center text-sm text-gray-500">
            <span>{item.category}</span>
            <span className="mx-2">•</span>
            <span>{item.condition}</span>
          </div>
        </div>
      </div>
      
      {/* Market Overview */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">市場概況</h2>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Price Stats */}
            <div className="bg-indigo-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-indigo-700">推薦售價</h3>
              <p className="mt-1 text-2xl font-semibold text-gray-900">{formatCurrency(results.recommendedPrice)}</p>
              <div className="mt-1 flex items-center text-sm">
                <span className="text-gray-500">可信度:</span>
                <span className="ml-1 font-medium">{results.confidenceScore}%</span>
              </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-700">市場平均價</h3>
              <p className="mt-1 text-2xl font-semibold text-gray-900">{formatCurrency(filteredStats.avg)}</p>
              <div className="mt-1 flex items-center text-sm">
                <span className="text-gray-500">基於 {filteredStats.count} 筆資料</span>
              </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-700">價格區間</h3>
              <div className="mt-1 text-xl font-semibold text-gray-900 flex items-center">
                <span>{formatCurrency(filteredStats.min)}</span>
                <span className="mx-2 text-gray-400">-</span>
                <span>{formatCurrency(filteredStats.max)}</span>
              </div>
              <div className="mt-1 text-sm text-gray-500">市場最低 - 最高價</div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-700">市場趨勢</h3>
              <div className="mt-1 text-xl font-semibold flex items-center">
                {results.marketTrend > 0 ? (
                  <span className="text-green-600 flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clipRule="evenodd" />
                    </svg>
                    上漲 {results.marketTrend}%
                  </span>
                ) : results.marketTrend < 0 ? (
                  <span className="text-red-600 flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M12 13a1 1 0 100 2h5a1 1 0 001-1v-5a1 1 0 10-2 0v2.586l-4.293-4.293a1 1 0 00-1.414 0L8 9.586l-4.293-4.293a1 1 0 00-1.414 1.414l5 5a1 1 0 001.414 0L11 9.414 14.586 13H12z" clipRule="evenodd" />
                    </svg>
                    下跌 {Math.abs(results.marketTrend)}%
                  </span>
                ) : (
                  <span className="text-gray-600">持平 0%</span>
                )}
              </div>
              <div className="mt-1 text-sm text-gray-500">過去30天</div>
            </div>
          </div>
          
          {/* Price Trend Chart */}
          <div className="mt-8">
            <h3 className="text-sm font-medium text-gray-900 mb-4">價格趨勢</h3>
            <div className="h-64 bg-gray-50 rounded-lg p-4 flex items-center justify-center">
              {/* This would be a chart in a real app */}
              <div className="text-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-gray-400 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                </svg>
                <p className="text-sm text-gray-500">
                  此圖表將顯示過去90天的價格趨勢<br />
                  （在實際應用中會有互動式圖表）
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Similar Items */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-lg font-medium text-gray-900">相似商品</h2>
          <span className="text-sm text-gray-500">
            找到 {filteredSimilarItems.length} 筆相似商品
          </span>
        </div>
        
        {/* Filters */}
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div className="flex flex-wrap gap-4">
            <div>
              <label htmlFor="timeframeFilter" className="block text-sm font-medium text-gray-700 mb-1">
                時間範圍
              </label>
              <select
                id="timeframeFilter"
                value={timeframeFilter}
                onChange={(e) => setTimeframeFilter(e.target.value)}
                className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              >
                <option value="7days">最近 7 天</option>
                <option value="30days">最近 30 天</option>
                <option value="90days">最近 90 天</option>
                <option value="1year">最近 1 年</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="categoryFilter" className="block text-sm font-medium text-gray-700 mb-1">
                類別
              </label>
              <select
                id="categoryFilter"
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              >
                <option value="all">所有類別</option>
                <option value="same">相同類別</option>
                <option value="similar">類似類別</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="priceRangeFilter" className="block text-sm font-medium text-gray-700 mb-1">
                價格範圍
              </label>
              <select
                id="priceRangeFilter"
                value={priceRangeFilter}
                onChange={(e) => setPriceRangeFilter(e.target.value)}
                className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              >
                <option value="all">所有價格</option>
                <option value="lower">較低價格</option>
                <option value="similar">相似價格</option>
                <option value="higher">較高價格</option>
              </select>
            </div>
          </div>
        </div>
        
        {/* Similar Items List */}
        <div className="divide-y divide-gray-200">
          {filteredSimilarItems.length > 0 ? (
            filteredSimilarItems.map((similarItem, index) => (
              <div key={index} className="p-6 flex items-start">
                <div className="flex-shrink-0 h-16 w-16">
                  <img 
                    className="h-16 w-16 rounded-md object-cover" 
                    src={similarItem.imageUrl || "https://via.placeholder.com/64?text=No+Image"} 
                    alt={similarItem.title}
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = "https://via.placeholder.com/64?text=No+Image";
                    }}
                  />
                </div>
                
                <div className="ml-4 flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium text-gray-900">{similarItem.title}</h4>
                    <span className="text-xs text-gray-500">{formatDate(similarItem.saleDate)}</span>
                  </div>
                  
                  <div className="mt-1">
                    <span className="text-xs text-gray-500">{similarItem.category} · {similarItem.condition}</span>
                  </div>
                  
                  <div className="mt-2 flex items-center justify-between">
                    <div>
                      <span className="text-sm font-medium">{formatCurrency(similarItem.price)}</span>
                      {similarItem.finalPrice && similarItem.finalPrice !== similarItem.price && (
                        <span className="ml-2 text-xs text-gray-500">
                          成交價: {formatCurrency(similarItem.finalPrice)}
                        </span>
                      )}
                    </div>
                    
                    <div className="flex items-center">
                      {similarItem.price > results.recommendedPrice ? (
                        <span className="text-sm text-red-600 flex items-center">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                          </svg>
                          高 {Math.round((similarItem.price - results.recommendedPrice) / results.recommendedPrice * 100)}%
                        </span>
                      ) : similarItem.price < results.recommendedPrice ? (
                        <span className="text-sm text-green-600 flex items-center">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                          </svg>
                          低 {Math.round((results.recommendedPrice - similarItem.price) / results.recommendedPrice * 100)}%
                        </span>
                      ) : (
                        <span className="text-sm text-gray-600">持平</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="p-6 text-center">
              <p className="text-gray-500">無符合條件的相似商品。請調整篩選條件再試一次。</p>
            </div>
          )}
        </div>
        
        {filteredSimilarItems.length > 5 && (
          <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 text-center">
            <button
              className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
            >
              查看更多相似商品
            </button>
          </div>
        )}
      </div>
      
      {/* Market Insights */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">市場洞察</h2>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-2">需求趨勢</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">搜尋量</span>
                  <span className="text-sm font-medium">
                    {results.demandMetrics.searchVolume > 0 ? (
                      <span className="text-green-600">↑ {results.demandMetrics.searchVolume}%</span>
                    ) : (
                      <span className="text-red-600">↓ {Math.abs(results.demandMetrics.searchVolume)}%</span>
                    )}
                  </span>
                </div>
                
                <div className="mt-2 flex justify-between items-center">
                  <span className="text-sm text-gray-500">觀看次數</span>
                  <span className="text-sm font-medium">
                    {results.demandMetrics.viewCount > 0 ? (
                      <span className="text-green-600">↑ {results.demandMetrics.viewCount}%</span>
                    ) : (
                      <span className="text-red-600">↓ {Math.abs(results.demandMetrics.viewCount)}%</span>
                    )}
                  </span>
                </div>
                
                <div className="mt-2 flex justify-between items-center">
                  <span className="text-sm text-gray-500">銷售速度</span>
                  <span className="text-sm font-medium">
                    {results.demandMetrics.saleSpeed === 'fast' ? (
                      <span className="text-green-600">快速 (平均 {results.averageSaleTime} 天)</span>
                    ) : results.demandMetrics.saleSpeed === 'average' ? (
                      <span className="text-yellow-600">一般 (平均 {results.averageSaleTime} 天)</span>
                    ) : (
                      <span className="text-red-600">緩慢 (平均 {results.averageSaleTime} 天)</span>
                    )}
                  </span>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-2">季節性趨勢</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-700 mb-3">
                  {results.seasonalTrends.currentSeasonImpact > 0 ? (
                    `目前季節通常對此類商品有正面影響，價格可能上漲 ${results.seasonalTrends.currentSeasonImpact}%。`
                  ) : results.seasonalTrends.currentSeasonImpact < 0 ? (
                    `目前季節通常對此類商品有負面影響，價格可能下跌 ${Math.abs(results.seasonalTrends.currentSeasonImpact)}%。`
                  ) : (
                    `目前季節對此類商品價格影響不大。`
                  )}
                </p>
                <p className="text-sm text-gray-700">
                  {results.seasonalTrends.bestSellingSeason ? (
                    `此商品的最佳銷售季節為 ${results.seasonalTrends.bestSellingSeason}。`
                  ) : (
                    `此商品全年銷售趨勢穩定，無明顯季節性差異。`
                  )}
                </p>
              </div>
            </div>
            
            <div className="md:col-span-2">
              <h3 className="text-sm font-medium text-gray-900 mb-2">價格建議</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <ul className="space-y-2 text-sm text-gray-700">
                  {results.marketInsights.map((insight, index) => (
                    <li key={index} className="flex items-start">
                      <svg className="h-5 w-5 text-indigo-500 mr-2 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {insight}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketAnalysis;