// Mock API service for product analysis and predictions
const analyzeProduct = async (productData) => {
  // In a real app, this would send data to a backend service
  // For demo purposes, we'll simulate a network request delay
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  // Generate a unique ID for the analysis
  const id = Math.random().toString(36).substring(2, 15);
  
  // Mock analysis results
  const results = {
    id,
    recommendedPrice: calculateRecommendedPrice(productData),
    fastSalePrice: calculateFastSalePrice(productData),
    maxProfitPrice: calculateMaxProfitPrice(productData),
    marketAveragePrice: calculateMarketAverage(productData),
    confidenceScore: Math.floor(75 + Math.random() * 15), // 75-90% confidence
    analysisDate: new Date().toISOString(),
    priceRangeLow: calculatePriceRangeLow(productData),
    priceRangeHigh: calculatePriceRangeHigh(productData),
    averageSaleTime: Math.floor(5 + Math.random() * 10), // 5-15 days
    fastSaleTime: Math.floor(1 + Math.random() * 4), // 1-5 days
    maxProfitSaleTime: Math.floor(15 + Math.random() * 15), // 15-30 days
    priceFactors: generatePriceFactors(productData),
    priceDistribution: generatePriceDistribution(productData),
    similarItems: generateSimilarItems(productData),
    marketTrend: Math.floor(Math.random() * 21) - 10, // -10% to +10%
    demandMetrics: {
      searchVolume: Math.floor(Math.random() * 41) - 20, // -20% to +20%
      viewCount: Math.floor(Math.random() * 61) - 30, // -30% to +30%
      saleSpeed: ['fast', 'average', 'slow'][Math.floor(Math.random() * 3)]
    },
    seasonalTrends: {
      currentSeasonImpact: Math.floor(Math.random() * 21) - 10, // -10% to +10%
      bestSellingSeason: ['春季', '夏季', '秋季', '冬季', '全年'][Math.floor(Math.random() * 5)]
    },
    marketInsights: [
      '根據市場數據，目前此類商品售價略有下降趨勢，建議在近期出售。',
      '同款商品在兩週內有較高的搜尋量，顯示需求正在增加。',
      '為提高銷售速度，建議提供更多產品照片和詳細的狀況描述。',
      '分析顯示，此商品在週末有較高的成交率，建議在週五晚上發布。'
    ]
  };
  
  return results;
};

// Mock image upload service
const uploadProductImage = async (file) => {
  // In a real app, this would upload to a storage service
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Create a fake image URL
  // In a real app, this would be the URL of the uploaded image
  return URL.createObjectURL(file);
};

// Helper functions for price calculations
const calculateRecommendedPrice = (productData) => {
  // Base price based on category
  let basePrice;
  const condition = productData.condition;
  const purchaseYear = productData.purchaseYear || new Date().getFullYear();
  const currentYear = new Date().getFullYear();
  const age = currentYear - purchaseYear;
  
  switch (productData.categoryId) {
    case 'electronics':
      basePrice = 15000;
      break;
    case 'clothing':
      basePrice = 2000;
      break;
    case 'home':
      basePrice = 5000;
      break;
    case 'toys':
      basePrice = 1500;
      break;
    case 'sports':
      basePrice = 3000;
      break;
    default:
      basePrice = 5000; // Default price
  }
  
  // Adjust based on condition
  const conditionMultiplier = 
    condition === '全新' ? 1.0 :
    condition === '幾乎全新' ? 0.9 :
    condition === '使用過 - 良好' ? 0.7 :
    condition === '使用過 - 尚可' ? 0.5 :
    condition === '使用過 - 有明顯磨損' ? 0.3 : 0.5;
  
  // Adjust based on age - products lose value over time
  const ageMultiplier = Math.max(0.3, 1 - (age * 0.1));
  
  // Adjust based on brand recognition (mock implementation)
  const brandMultiplier = productData.brand ? 
    (productData.brand.toLowerCase().includes('apple') ? 1.2 : 
     productData.brand.toLowerCase().includes('samsung') ? 1.1 : 
     productData.brand.toLowerCase().includes('sony') ? 1.1 : 1.0) : 1.0;
  
  // Calculate final price with randomness to simulate market fluctuation
  const randomFactor = 0.9 + (Math.random() * 0.2); // 0.9 to 1.1
  
  let price = basePrice * conditionMultiplier * ageMultiplier * brandMultiplier * randomFactor;
  
  // If the user provided a purchase price, factor it in slightly
  if (productData.purchasePrice) {
    price = (price * 0.7) + (productData.purchasePrice * 0.3 * ageMultiplier);
  }
  
  return Math.round(price);
};

const calculateFastSalePrice = (productData) => {
  const recommendedPrice = calculateRecommendedPrice(productData);
  // Fast sale price is 10-20% lower than recommended
  const discount = 0.1 + (Math.random() * 0.1);
  return Math.round(recommendedPrice * (1 - discount));
};

const calculateMaxProfitPrice = (productData) => {
  const recommendedPrice = calculateRecommendedPrice(productData);
  // Max profit price is 10-25% higher than recommended
  const premium = 0.1 + (Math.random() * 0.15);
  return Math.round(recommendedPrice * (1 + premium));
};

const calculateMarketAverage = (productData) => {
  const recommendedPrice = calculateRecommendedPrice(productData);
  // Market average varies slightly from recommended price
  const variation = 0.9 + (Math.random() * 0.2); // 0.9 to 1.1
  return Math.round(recommendedPrice * variation);
};

const calculatePriceRangeLow = (productData) => {
  const recommendedPrice = calculateRecommendedPrice(productData);
  // Low end of market is 20-30% below recommended
  return Math.round(recommendedPrice * (0.7 - Math.random() * 0.1));
};

const calculatePriceRangeHigh = (productData) => {
  const recommendedPrice = calculateRecommendedPrice(productData);
  // High end of market is 20-40% above recommended
  return Math.round(recommendedPrice * (1.2 + Math.random() * 0.2));
};

const generatePriceFactors = (productData) => {
  // Mock price factors based on product data
  const factors = [
    {
      name: '商品狀態',
      impact: productData.condition === '全新' ? 15 : 
              productData.condition === '幾乎全新' ? 10 : 
              productData.condition === '使用過 - 良好' ? 0 : 
              productData.condition === '使用過 - 尚可' ? -5 : -15,
      description: `商品狀態為「${productData.condition}」，影響價格估算。`
    },
    {
      name: '商品年齡',
      impact: -(new Date().getFullYear() - productData.purchaseYear) * 2,
      description: `商品購於 ${productData.purchaseYear} 年，距今 ${new Date().getFullYear() - productData.purchaseYear} 年。`
    }
  ];
  
  // Add brand factor if available
  if (productData.brand) {
    let brandImpact = 0;
    let brandDescription = '';
    
    if (productData.brand.toLowerCase().includes('apple')) {
      brandImpact = 20;
      brandDescription = '高溢價品牌，較高的品牌價值和轉售價值。';
    } else if (productData.brand.toLowerCase().includes('samsung') || productData.brand.toLowerCase().includes('sony')) {
      brandImpact = 10;
      brandDescription = '知名品牌，有較好的轉售價值。';
    }
    
    if (brandImpact !== 0) {
      factors.push({
        name: '品牌因素',
        impact: brandImpact,
        description: `${productData.brand}: ${brandDescription}`
      });
    }
  }
  
  // Add market demand factor
  factors.push({
    name: '市場需求',
    impact: Math.floor(Math.random() * 21) - 10, // -10% to +10%
    description: '基於當前市場交易量和搜尋趨勢的分析。'
  });
  
  // Add seasonal factor
  const currentMonth = new Date().getMonth();
  let seasonalImpact = 0;
  let seasonalDescription = '';
  
  if (productData.categoryId === 'sports' && currentMonth >= 3 && currentMonth <= 8) {
    seasonalImpact = 5;
    seasonalDescription = '運動用品在春夏季節有較高需求。';
  } else if (productData.categoryId === 'electronics' && (currentMonth === 10 || currentMonth === 11)) {
    seasonalImpact = 5;
    seasonalDescription = '電子產品在年末節慶期間需求增加。';
  }
  
  if (seasonalImpact !== 0) {
    factors.push({
      name: '季節性因素',
      impact: seasonalImpact,
      description: seasonalDescription
    });
  }
  
  return factors;
};

const generatePriceDistribution = (productData) => {
  const avgPrice = calculateRecommendedPrice(productData);
  const lowPrice = calculatePriceRangeLow(productData);
  const highPrice = calculatePriceRangeHigh(productData);
  
  const range = highPrice - lowPrice;
  const segment = range / 8;
  
  // Create price distribution with a bell curve shape
  const distribution = [
    { priceRange: [lowPrice, lowPrice + segment], count: Math.floor(Math.random() * 5) + 1 },
    { priceRange: [lowPrice + segment, lowPrice + 2 * segment], count: Math.floor(Math.random() * 10) + 5 },
    { priceRange: [lowPrice + 2 * segment, lowPrice + 3 * segment], count: Math.floor(Math.random() * 15) + 10 },
    { priceRange: [lowPrice + 3 * segment, lowPrice + 4 * segment], count: Math.floor(Math.random() * 15) + 15 },
    { priceRange: [lowPrice + 4 * segment, lowPrice + 5 * segment], count: Math.floor(Math.random() * 15) + 15 },
    { priceRange: [lowPrice + 5 * segment, lowPrice + 6 * segment], count: Math.floor(Math.random() * 15) + 10 },
    { priceRange: [lowPrice + 6 * segment, lowPrice + 7 * segment], count: Math.floor(Math.random() * 10) + 5 },
    { priceRange: [lowPrice + 7 * segment, highPrice], count: Math.floor(Math.random() * 5) + 1 }
  ];
  
  return distribution;
};

const generateSimilarItems = (productData) => {
  const recommendedPrice = calculateRecommendedPrice(productData);
  const count = 10 + Math.floor(Math.random() * 8); // 10-17 similar items
  const similarItems = [];
  
  const conditions = ['全新', '幾乎全新', '使用過 - 良好', '使用過 - 尚可', '使用過 - 有明顯磨損'];
  const currentDate = new Date();
  
  // Generate similar product names based on the category
  let productNames = [];
  switch (productData.categoryId) {
    case 'electronics':
      productNames = [
        'iPhone 13', 'Samsung Galaxy S21', 'iPad Air', 'MacBook Pro', 'Sony WH-1000XM4',
        'Nintendo Switch', 'Apple Watch Series 7', 'Bose QuietComfort', 'Canon EOS M50', 'DJI Mavic Air 2'
      ];
      break;
    case 'clothing':
      productNames = [
        'Nike Air Max', 'Adidas Ultra Boost', 'Levi\'s 501', 'Uniqlo T恤', 'H&M 襯衫',
        'North Face 外套', 'Columbia 登山鞋', 'Ray-Ban 太陽眼鏡', 'Coach 皮包', 'Zara 洋裝'
      ];
      break;
    case 'home':
      productNames = [
        'IKEA BILLY 書櫃', 'Dyson V11', 'KitchenAid 攪拌機', 'Nespresso 咖啡機', '無印良品收納盒',
        'Sony 55吋電視', '象印電子鍋', '膳魔師保溫瓶', 'Philips 空氣清淨機', '小米掃地機器人'
      ];
      break;
    default:
      productNames = [
        'iPhone 13', 'Samsung Galaxy S21', 'Nike Air Max', 'Dyson V11', 'Sony WH-1000XM4',
        'Nintendo Switch', 'IKEA BILLY 書櫃', 'Adidas Ultra Boost', 'Nespresso 咖啡機', '小米掃地機器人'
      ];
  }
  
  // Add some variations to product names
  const variations = ['Pro', 'Max', 'Ultra', 'Lite', 'Plus', '2022版', '限量版', '二代', '經典款', '特別版'];
  
  for (let i = 0; i < count; i++) {
    const randomDay = Math.floor(Math.random() * 120); // 0-120 days ago
    const saleDate = new Date(currentDate);
    saleDate.setDate(saleDate.getDate() - randomDay);
    
    // Decide if this is a variation of the product or a different one
    let title;
    const useVariation = Math.random() > 0.5;
    
    if (useVariation) {
      // Use the base product with a variation
      const baseName = productNames[Math.floor(Math.random() * productNames.length)];
      const variation = variations[Math.floor(Math.random() * variations.length)];
      title = `${baseName} ${variation}`;
    } else {
      // Just use a random product name
      title = productNames[Math.floor(Math.random() * productNames.length)];
    }
    
    // Generate a random price that's somewhat close to the recommended price
    const priceVariation = 0.7 + Math.random() * 0.6; // 0.7 to 1.3
    const price = Math.round(recommendedPrice * priceVariation);
    
    // Some items may have a different final price (to simulate negotiation)
    const hasFinalPrice = Math.random() > 0.7;
    const finalPrice = hasFinalPrice ? Math.round(price * (0.85 + Math.random() * 0.1)) : null;
    
    const condition = conditions[Math.floor(Math.random() * conditions.length)];
    
    // Assign a category that's either the same or similar
    let category;
    if (Math.random() > 0.3) {
      // Same category
      category = productData.categoryId === 'electronics' ? '電子產品' :
                 productData.categoryId === 'clothing' ? '服飾' :
                 productData.categoryId === 'home' ? '家居用品' :
                 productData.categoryId === 'toys' ? '玩具與嗜好' :
                 productData.categoryId === 'sports' ? '運動與戶外' : '其他';
    } else {
      // Similar category
      const similarCategories = {
        'electronics': ['智能設備', '電腦配件', '攝影器材'],
        'clothing': ['鞋子', '配飾', '包包'],
        'home': ['傢俱', '廚房用品', '居家裝飾'],
        'toys': ['桌遊', '收藏品', '模型'],
        'sports': ['健身器材', '戶外裝備', '球類運動']
      };
      
      const options = similarCategories[productData.categoryId] || ['其他類別'];
      category = options[Math.floor(Math.random() * options.length)];
    }
    
    // Generate placeholder image URL
    // In a real app, this would be actual product images
    const imageUrl = `https://via.placeholder.com/150?text=${encodeURIComponent(title)}`;
    
    similarItems.push({
      id: Math.random().toString(36).substring(2, 15),
      title,
      price,
      finalPrice,
      condition,
      category,
      saleDate: saleDate.toISOString(),
      imageUrl
    });
  }
  
  return similarItems;
};

export {
  analyzeProduct,
  uploadProductImage
};