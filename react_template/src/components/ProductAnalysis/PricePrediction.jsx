import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAppContext } from '../../context/AppContext';
import { formatCurrency } from '../../utils/helpers';

const PricePrediction = () => {
  const { id } = useParams();
  const { history } = useAppContext();
  const [item, setItem] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('recommended');
  const [showPriceFactors, setShowPriceFactors] = useState(false);

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
          <h3 className="text-lg font-medium text-gray-900 mb-2">找不到分析結果</h3>
          <p className="text-gray-500 mb-6">
            無法找到此 ID 的價格分析。該分析可能已被刪除，或連結無效。
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
  
  // Define pricing strategies
  const pricingStrategies = [
    {
      id: 'recommended',
      name: '建議價格',
      price: results.recommendedPrice,
      description: '此價格基於市場數據和機器學習模型綜合分析得出，為最優化的平衡價格。',
      saleTime: '預估一般銷售時長',
      confidenceScore: results.confidenceScore
    },
    {
      id: 'fast',
      name: '快速銷售',
      price: results.fastSalePrice,
      description: '較低價格以加速銷售過程，適合需要快速出售的情況。',
      saleTime: `預估 ${results.fastSaleTime} 天內售出`,
      confidenceScore: results.confidenceScore - 5
    },
    {
      id: 'profit',
      name: '最大利潤',
      price: results.maxProfitPrice,
      description: '較高定價以追求最大利潤，但可能需要更長的銷售時間。',
      saleTime: `預估 ${results.maxProfitSaleTime} 天內售出`,
      confidenceScore: results.confidenceScore - 10
    }
  ];
  
  // Get active pricing strategy
  const activeStrategy = pricingStrategies.find(strategy => strategy.id === activeTab);

  return (
    <div className="space-y-6">
      {/* Page Header with Item Info */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-start">
        <div>
          <div className="flex items-center">
            <Link to="/product-analysis" className="text-indigo-600 hover:text-indigo-500 mr-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clipRule="evenodd" />
              </svg>
            </Link>
            <h1 className="text-2xl font-bold text-gray-800">{item.name}</h1>
          </div>
          <div className="mt-1 flex flex-wrap items-center text-sm text-gray-500">
            <span>{item.category}</span>
            <span className="mx-2">•</span>
            <span>{item.condition}</span>
          </div>
        </div>
        <div className="mt-4 md:mt-0">
          <Link
            to={`/market-analysis/${id}`}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            查看市場分析
          </Link>
        </div>
      </div>
      
      {/* Main Content - Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Product Image and Info */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow rounded-lg overflow-hidden">
            {/* Product Image */}
            <div className="p-6 flex justify-center">
              {item.imageUrl ? (
                <img 
                  src={item.imageUrl} 
                  alt={item.name} 
                  className="h-48 w-48 object-contain rounded-md"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = "https://via.placeholder.com/200?text=No+Image";
                  }}
                />
              ) : (
                <div className="h-48 w-48 bg-gray-100 rounded-md flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
              )}
            </div>
            
            {/* Price Range */}
            <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
              <h3 className="text-sm font-medium text-gray-500">價格區間</h3>
              <div className="mt-2 flex justify-between items-center">
                <div>
                  <span className="text-xs text-gray-500">最低</span>
                  <p className="text-sm font-medium">{formatCurrency(results.priceRangeLow)}</p>
                </div>
                <div className="h-1 bg-gray-200 flex-1 mx-4 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-indigo-500 rounded-full" 
                    style={{ 
                      width: `${((activeStrategy.price - results.priceRangeLow) / (results.priceRangeHigh - results.priceRangeLow)) * 100}%` 
                    }}
                  ></div>
                </div>
                <div className="text-right">
                  <span className="text-xs text-gray-500">最高</span>
                  <p className="text-sm font-medium">{formatCurrency(results.priceRangeHigh)}</p>
                </div>
              </div>
            </div>
            
            {/* Market Comparison */}
            <div className="px-6 py-4 border-t border-gray-200">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-medium text-gray-900">市場平均價格</h3>
                <span className="text-sm font-medium">{formatCurrency(results.marketAveragePrice)}</span>
              </div>
              
              <div className="mt-3">
                {activeStrategy.price > results.marketAveragePrice ? (
                  <div className="flex items-center text-red-600">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                    <span className="text-xs font-medium">
                      高於市場 {Math.round((activeStrategy.price - results.marketAveragePrice) / results.marketAveragePrice * 100)}%
                    </span>
                  </div>
                ) : (
                  <div className="flex items-center text-green-600">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                    </svg>
                    <span className="text-xs font-medium">
                      低於市場 {Math.round((results.marketAveragePrice - activeStrategy.price) / results.marketAveragePrice * 100)}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {/* Price Factors */}
          <div className="mt-6 bg-white shadow rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-lg font-medium text-gray-900">價格影響因素</h3>
              <button 
                className="text-indigo-600 hover:text-indigo-500 text-sm font-medium focus:outline-none"
                onClick={() => setShowPriceFactors(!showPriceFactors)}
              >
                {showPriceFactors ? '收起' : '展開'}
              </button>
            </div>
            
            <div className={`px-6 py-4 ${showPriceFactors ? '' : 'max-h-40 overflow-hidden'}`}>
              {results.priceFactors.map((factor, index) => (
                <div key={index} className="mb-3 last:mb-0">
                  <div className="flex justify-between items-center mb-1">
                    <h4 className="text-sm font-medium text-gray-900">{factor.name}</h4>
                    <span className={`text-xs font-medium ${factor.impact > 0 ? 'text-green-600' : factor.impact < 0 ? 'text-red-600' : 'text-gray-500'}`}>
                      {factor.impact > 0 ? `+${factor.impact}%` : factor.impact < 0 ? `${factor.impact}%` : '0%'}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">{factor.description}</p>
                </div>
              ))}
              
              {!showPriceFactors && results.priceFactors.length > 2 && (
                <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-white to-transparent"></div>
              )}
            </div>
          </div>
        </div>
        
        {/* Right Column - Pricing Strategies */}
        <div className="lg:col-span-2">
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">價格預測結果</h2>
              <p className="text-sm text-gray-500 mt-1">
                基於深度強化學習演算法和歷史市場數據分析，我們為您提供了以下定價方案
              </p>
            </div>
            
            {/* Pricing Strategy Tabs */}
            <div className="border-b border-gray-200">
              <div className="px-6">
                <nav className="-mb-px flex space-x-6">
                  {pricingStrategies.map((strategy) => (
                    <button
                      key={strategy.id}
                      className={`
                        whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm
                        ${activeTab === strategy.id
                          ? 'border-indigo-500 text-indigo-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }
                      `}
                      onClick={() => setActiveTab(strategy.id)}
                    >
                      {strategy.name}
                    </button>
                  ))}
                </nav>
              </div>
            </div>
            
            {/* Active Strategy Content */}
            <div className="px-6 py-5">
              <div className="flex flex-col md:flex-row md:justify-between md:items-start">
                <div>
                  <div className="flex items-center">
                    <span className="text-3xl font-bold text-gray-900">{formatCurrency(activeStrategy.price)}</span>
                    <div className="ml-3 inline-flex bg-indigo-100 rounded-full px-3 py-0.5">
                      <span className="text-xs font-medium text-indigo-800">
                        {activeStrategy.confidenceScore}% 可信度
                      </span>
                    </div>
                  </div>
                  <p className="mt-1 text-sm text-gray-500">{activeStrategy.saleTime}</p>
                </div>
                
                <div className="mt-4 md:mt-0">
                  <button
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                    </svg>
                    分享結果
                  </button>
                </div>
              </div>
              
              {/* Strategy Description */}
              <div className="mt-4 p-4 bg-gray-50 rounded-md">
                <p className="text-sm text-gray-700">
                  {activeStrategy.description}
                </p>
              </div>
              
              {/* Price Distribution Chart */}
              <div className="mt-6">
                <h3 className="text-sm font-medium text-gray-900 mb-3">市場價格分佈</h3>
                <div className="h-32">
                  {results.priceDistribution.map((range, index) => {
                    // Calculate if current price falls within this range
                    const isPriceInRange = 
                      activeStrategy.price >= range.priceRange[0] && 
                      activeStrategy.price < range.priceRange[1];
                    
                    // Calculate relative height based on count
                    const maxCount = Math.max(...results.priceDistribution.map(r => r.count));
                    const height = (range.count / maxCount) * 100;
                    
                    return (
                      <div 
                        key={index} 
                        className="inline-block"
                        style={{ width: `${100 / results.priceDistribution.length}%` }}
                      >
                        <div className="flex flex-col items-center">
                          <div 
                            className={`w-5/6 rounded-t-sm ${isPriceInRange ? 'bg-indigo-500' : 'bg-gray-200'}`}
                            style={{ height: `${height}%` }}
                          ></div>
                          <span className="text-xs text-gray-500 mt-1">
                            {formatCurrency(range.priceRange[0]).replace('NT$', '')}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
            
            {/* Recommendation Details */}
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
              <h3 className="text-sm font-medium text-gray-900 mb-2">如何達到更好的銷售成效</h3>
              <ul className="text-sm text-gray-700 space-y-2">
                <li className="flex items-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  提供完整詳細的商品描述，包括品牌、型號、規格和功能
                </li>
                <li className="flex items-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  上傳多張高質量照片，展示商品各個角度和細節
                </li>
                <li className="flex items-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  清楚說明商品狀態，誠實披露任何瑕疵或使用痕跡
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricePrediction;