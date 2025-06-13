import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../../context/AppContext';
import { analyzeProduct, uploadProductImage } from '../../services/api';
import { getEbayCategoriesTree } from '../../services/ebayService';

const ProductAnalysisForm = () => {
  const navigate = useNavigate();
  const { addToHistory, settings } = useAppContext();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [categories, setCategories] = useState([]);
  const [categoriesLoading, setCategoriesLoading] = useState(true);
  const [imageUploading, setImageUploading] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 20 }, (_, i) => currentYear - i);

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    categoryId: settings.defaultCategory || '',
    brand: '',
    condition: '全新',
    purchaseYear: currentYear,
    purchasePrice: '',
    imageUrl: '',
    notes: ''
  });

  // Fetch categories on component mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const categoriesData = await getEbayCategoriesTree();
        setCategories(categoriesData);
      } catch (error) {
        console.error('Error fetching categories:', error);
        setError('無法載入類別資料，請重試');
      } finally {
        setCategoriesLoading(false);
      }
    };

    fetchCategories();
  }, []);

  // Handle form input changes
  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? (value ? Number(value) : '') : value
    }));
  };

  // Handle image upload
  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    if (!validTypes.includes(file.type)) {
      setError('請上傳有效的圖片格式（JPG, PNG, WebP, GIF）');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('圖片大小不能超過 5MB');
      return;
    }

    try {
      setImageUploading(true);
      setError('');

      // Create a local preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result); // For local preview
        setFormData(prev => ({ // Store base64 string for persistence
          ...prev,
          imageUrl: reader.result
        }));
      };
      reader.readAsDataURL(file);

      // Simulate upload process if needed, but we use base64 for imageUrl
      await uploadProductImage(file);

      // In a real app, this would upload to a server
      // For this mock, we are using the base64 string from FileReader as the imageUrl
      // const imageUrl = await uploadProductImage(file); 
      // The actual setting of imageUrl will happen in reader.onloadend
      // setFormData(prev => ({
      //   ...prev,
      //   imageUrl
      // }));
    } catch (error) {
      console.error('Image upload error:', error);
      setError('圖片上傳失敗，請稍後再試');
    } finally {
      setImageUploading(false);
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Simple validation
    if (!formData.title) {
      setError('請輸入商品名稱');
      return;
    }

    if (!formData.categoryId) {
      setError('請選擇商品類別');
      return;
    }

    try {
      setIsLoading(true);
      setError('');

      // Submit product data for analysis
      const result = await analyzeProduct(formData);
      
      // Add the result to history
      addToHistory({
        id: result.id,
        name: formData.title,
        category: categories.find(cat => cat.id === formData.categoryId)?.name || formData.categoryId,
        condition: formData.condition,
        suggestedPrice: result.recommendedPrice,
        marketPrice: result.marketAveragePrice,
        analysisDate: result.analysisDate,
        imageUrl: formData.imageUrl, // This will now be a base64 string or empty
        analysisResults: result
      });

      // Navigate to the price prediction page
      navigate(`/price-prediction/${result.id}`);
    } catch (error) {
      console.error('Analysis error:', error);
      setError(error.message || '分析請求失敗，請稍後再試');
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-800">價格分析</h1>
        <p className="mt-1 text-sm text-gray-500">
          輸入您的商品資訊，獲得基於深度強化學習的智能價格預測
        </p>
      </div>

      {/* Form Container */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">商品資訊</h2>
          <p className="text-sm text-gray-600 mt-1">
            請填寫越詳細的資訊，預測結果越準確
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
              <div className="flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-red-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          )}

          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                商品名稱 *
              </label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="例：iPhone 13 Pro 128GB"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                required
              />
            </div>

            <div>
              <label htmlFor="brand" className="block text-sm font-medium text-gray-700">
                品牌
              </label>
              <input
                type="text"
                id="brand"
                name="brand"
                value={formData.brand}
                onChange={handleChange}
                placeholder="例：Apple"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
              />
            </div>
          </div>

          {/* Category and Condition */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="categoryId" className="block text-sm font-medium text-gray-700">
                商品類別 *
              </label>
              <select
                id="categoryId"
                name="categoryId"
                value={formData.categoryId}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                required
                disabled={categoriesLoading}
              >
                <option value="">請選擇類別</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>{category.name}</option>
                ))}
              </select>
              {categoriesLoading && (
                <p className="mt-1 text-xs text-gray-500">載入類別中...</p>
              )}
            </div>

            <div>
              <label htmlFor="condition" className="block text-sm font-medium text-gray-700">
                商品狀態 *
              </label>
              <select
                id="condition"
                name="condition"
                value={formData.condition}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                required
              >
                <option value="全新">全新</option>
                <option value="幾乎全新">幾乎全新</option>
                <option value="使用過 - 良好">使用過 - 良好</option>
                <option value="使用過 - 尚可">使用過 - 尚可</option>
                <option value="使用過 - 有明顯磨損">使用過 - 有明顯磨損</option>
              </select>
            </div>
          </div>

          {/* Purchase Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="purchaseYear" className="block text-sm font-medium text-gray-700">
                購買年份
              </label>
              <select
                id="purchaseYear"
                name="purchaseYear"
                value={formData.purchaseYear}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
              >
                {years.map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="purchasePrice" className="block text-sm font-medium text-gray-700">
                購買價格 (TWD)
              </label>
              <input
                type="number"
                id="purchasePrice"
                name="purchasePrice"
                value={formData.purchasePrice}
                onChange={handleChange}
                min="0"
                placeholder="例：25000"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
              />
            </div>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700">
              商品描述
            </label>
            <textarea
              id="description"
              name="description"
              rows={4}
              value={formData.description}
              onChange={handleChange}
              placeholder="請輸入商品的詳細描述，包括規格、特色等"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
            />
          </div>

          {/* Image Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              上傳商品圖片
            </label>
            
            <div className="flex items-center space-x-6">
              <div className="flex-shrink-0">
                {imagePreview ? (
                  <img 
                    src={imagePreview} 
                    alt="商品預覽" 
                    className="h-32 w-32 object-cover rounded-md"
                  />
                ) : (
                  <div className="h-32 w-32 rounded-md border-2 border-dashed border-gray-300 flex items-center justify-center bg-gray-50">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                )}
              </div>
              
              <div className="flex-1">
                <label className="inline-block px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 cursor-pointer">
                  <span>選擇圖片</span>
                  <input 
                    id="image-upload" 
                    name="image" 
                    type="file" 
                    className="sr-only" 
                    accept="image/*"
                    onChange={handleImageUpload}
                    disabled={imageUploading}
                  />
                </label>
                
                {imageUploading ? (
                  <p className="mt-2 text-sm text-gray-500 flex items-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    上傳中...
                  </p>
                ) : (
                  <p className="mt-2 text-sm text-gray-500">
                    PNG, JPG, GIF 或 WebP，最大 5MB
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Additional Notes */}
          <div>
            <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
              其他備註
            </label>
            <textarea
              id="notes"
              name="notes"
              rows={2}
              value={formData.notes}
              onChange={handleChange}
              placeholder="其他可能影響價格的因素"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
            />
          </div>

          {/* Submit Button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isLoading}
              className={`
                inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white 
                ${isLoading ? 'bg-indigo-400' : 'bg-indigo-600 hover:bg-indigo-700'} 
                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500
              `}
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  分析中...
                </>
              ) : (
                <>
                  開始分析
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProductAnalysisForm;