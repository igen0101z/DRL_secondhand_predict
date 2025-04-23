// Mock eBay API service for category data and market information
const getEbayCategoriesTree = async (apiKey = null) => {
  // In a real app, this would make a request to eBay's API
  // For demo purposes, we'll simulate a network request delay
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Mock categories data
  const categories = [
    { id: 'electronics', name: '電子產品' },
    { id: 'clothing', name: '服飾' },
    { id: 'home', name: '家居用品' },
    { id: 'toys', name: '玩具與嗜好' },
    { id: 'sports', name: '運動與戶外' },
    { id: 'collectibles', name: '收藏品' },
    { id: 'beauty', name: '美妝保養' },
    { id: 'automotive', name: '汽車用品' },
    { id: 'books', name: '書籍與雜誌' },
    { id: 'music', name: '音樂與樂器' }
  ];
  
  return categories;
};

const getMarketInsights = async (categoryId, searchTerm, timeRange = '90days') => {
  // In a real app, this would query eBay's API for market insights
  await new Promise(resolve => setTimeout(resolve, 1200));
  
  // Generate mock insights data
  const insights = {
    trendDirection: Math.random() > 0.5 ? 'up' : 'down',
    percentageChange: Math.floor(Math.random() * 20) - 10, // -10% to +10%
    averagePrice: 5000 + Math.floor(Math.random() * 10000),
    saleVelocity: ['fast', 'medium', 'slow'][Math.floor(Math.random() * 3)],
    popularKeywords: ['二手', '全新', '保固', '盒裝', '配件齊全'],
    bestDayToSell: ['週末', '週五', '週一', '平日'][Math.floor(Math.random() * 4)],
    seasonalTrend: {
      bestMonth: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'][Math.floor(Math.random() * 12)],
      worstMonth: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'][Math.floor(Math.random() * 12)]
    }
  };
  
  return insights;
};

const getSimilarCompletedListings = async (categoryId, searchTerm, timeRange = '90days', pageSize = 20) => {
  // In a real app, this would query eBay's API for completed listings
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Mock completed listings data
  const listings = [];
  const now = new Date();
  
  for (let i = 0; i < pageSize; i++) {
    const daysAgo = Math.floor(Math.random() * parseInt(timeRange));
    const date = new Date(now);
    date.setDate(date.getDate() - daysAgo);
    
    const basePrice = 3000 + Math.floor(Math.random() * 8000);
    const condition = ['New', 'Like New', 'Very Good', 'Good', 'Acceptable'][Math.floor(Math.random() * 5)];
    
    listings.push({
      id: `listing-${i}-${Math.random().toString(36).substring(2)}`,
      title: `${searchTerm} ${Math.random() > 0.5 ? 'Pro' : Math.random() > 0.5 ? 'Max' : ''} ${condition} ${Math.random() > 0.7 ? 'with accessories' : ''}`,
      price: basePrice,
      currency: 'TWD',
      endTime: date.toISOString(),
      conditionDisplayName: condition,
      isCompleted: true,
      isSold: Math.random() > 0.3, // 70% chance the item was sold
      bidCount: Math.floor(Math.random() * 10),
      listingUrl: `https://example.com/item-${i}`,
      imageUrl: `https://via.placeholder.com/150?text=${encodeURIComponent(searchTerm)}`
    });
  }
  
  return listings;
};

const getActiveListings = async (categoryId, searchTerm, sortOrder = 'endingSoonest', pageSize = 10) => {
  // In a real app, this would query eBay's API for active listings
  await new Promise(resolve => setTimeout(resolve, 900));
  
  // Mock active listings data
  const listings = [];
  const now = new Date();
  
  for (let i = 0; i < pageSize; i++) {
    // Random ending time in the next 7 days
    const daysLater = Math.floor(Math.random() * 7);
    const date = new Date(now);
    date.setDate(date.getDate() + daysLater);
    
    const basePrice = 3000 + Math.floor(Math.random() * 8000);
    const condition = ['New', 'Like New', 'Very Good', 'Good', 'Acceptable'][Math.floor(Math.random() * 5)];
    
    listings.push({
      id: `active-${i}-${Math.random().toString(36).substring(2)}`,
      title: `${searchTerm} ${Math.random() > 0.5 ? 'Pro' : Math.random() > 0.5 ? 'Max' : ''} ${condition} ${Math.random() > 0.7 ? 'with accessories' : ''}`,
      price: basePrice,
      currency: 'TWD',
      endTime: date.toISOString(),
      conditionDisplayName: condition,
      bidCount: Math.floor(Math.random() * 10),
      listingUrl: `https://example.com/active-item-${i}`,
      imageUrl: `https://via.placeholder.com/150?text=${encodeURIComponent(searchTerm)}`
    });
  }
  
  return listings;
};

export {
  getEbayCategoriesTree,
  getMarketInsights,
  getSimilarCompletedListings,
  getActiveListings
};