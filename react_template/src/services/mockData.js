// Mock data service for dashboard and prediction data
const getMockDashboardData = () => {
  return {
    totalItems: 42,
    averageAccuracy: 92,
    averagePriceDifference: 365,
    averageSaleTime: 7,
    recentItems: [
      {
        id: 'rec-1',
        name: 'iPhone 13 Pro 128GB',
        category: '電子產品',
        condition: '幾乎全新',
        suggestedPrice: 25600,
        marketPrice: 26500,
        analysisDate: '2023-06-10T14:35:22Z',
        imageUrl: 'https://via.placeholder.com/64?text=iPhone'
      },
      {
        id: 'rec-2',
        name: 'Nike Air Max 270',
        category: '服飾',
        condition: '使用過 - 良好',
        suggestedPrice: 2400,
        marketPrice: 2200,
        analysisDate: '2023-06-09T09:12:45Z',
        imageUrl: 'https://via.placeholder.com/64?text=Nike'
      },
      {
        id: 'rec-3',
        name: 'Sony WH-1000XM4 耳機',
        category: '電子產品',
        condition: '全新',
        suggestedPrice: 7800,
        marketPrice: 8000,
        analysisDate: '2023-06-08T17:23:11Z',
        imageUrl: 'https://via.placeholder.com/64?text=Sony'
      },
      {
        id: 'rec-4',
        name: 'IKEA BILLY 書櫃',
        category: '家居用品',
        condition: '使用過 - 尚可',
        suggestedPrice: 1200,
        marketPrice: 1350,
        analysisDate: '2023-06-07T10:45:30Z',
        imageUrl: 'https://via.placeholder.com/64?text=IKEA'
      },
      {
        id: 'rec-5',
        name: 'Nintendo Switch 主機',
        category: '電子產品',
        condition: '使用過 - 良好',
        suggestedPrice: 6500,
        marketPrice: 6200,
        analysisDate: '2023-06-05T13:19:27Z',
        imageUrl: 'https://via.placeholder.com/64?text=Nintendo'
      }
    ]
  };
};

// Generate a random product ID
const generateProductId = () => {
  return Math.random().toString(36).substring(2, 10);
};

export {
  getMockDashboardData,
  generateProductId
};