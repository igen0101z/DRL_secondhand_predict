import React, { createContext, useContext, useState, useEffect } from 'react';

// Create context
const AppContext = createContext();

// Custom hook to use the AppContext
export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppContextProvider');
  }
  return context;
};

export const AppContextProvider = ({ children }) => {
  // Initialize state from localStorage if available
  const [history, setHistory] = useState(() => {
    const savedHistory = localStorage.getItem('priceAnalysisHistory');
    return savedHistory ? JSON.parse(savedHistory) : [];
  });

  const [settings, setSettings] = useState(() => {
    const savedSettings = localStorage.getItem('priceAnalysisSettings');
    return savedSettings ? JSON.parse(savedSettings) : {
      defaultCategory: '',
      confidenceThreshold: 70,
      preferredPriceStrategy: 'recommended',
      showMarketInsights: true,
      notifyPriceDrops: true,
      ebayApiKey: '',
      theme: 'light',
      language: 'zh-TW'
    };
  });

  // Save to localStorage whenever state changes
  useEffect(() => {
    localStorage.setItem('priceAnalysisHistory', JSON.stringify(history));
  }, [history]);

  useEffect(() => {
    localStorage.setItem('priceAnalysisSettings', JSON.stringify(settings));
  }, [settings]);

  // History management functions
  const addToHistory = (item) => {
    setHistory(prevHistory => {
      // Check if the item already exists
      const existingItemIndex = prevHistory.findIndex(historyItem => historyItem.id === item.id);
      
      if (existingItemIndex >= 0) {
        // Replace the existing item
        const updatedHistory = [...prevHistory];
        updatedHistory[existingItemIndex] = item;
        return updatedHistory;
      } else {
        // Add new item to the beginning of the array
        return [item, ...prevHistory];
      }
    });
  };

  const removeFromHistory = (id) => {
    setHistory(prevHistory => prevHistory.filter(item => item.id !== id));
  };

  const clearHistory = () => {
    setHistory([]);
  };

  // Settings management
  const updateSettings = (newSettings) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      ...newSettings
    }));
  };

  // Context value
  const value = {
    history,
    settings,
    addToHistory,
    removeFromHistory,
    clearHistory,
    updateSettings,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

export default AppContext;