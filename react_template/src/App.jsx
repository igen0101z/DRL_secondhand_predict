import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppContextProvider } from './context/AppContext';
import Header from './components/Layout/Header';
import Sidebar from './components/Layout/Sidebar';
import Footer from './components/Layout/Footer';
import Dashboard from './components/Dashboard/Dashboard';
import ProductAnalysisForm from './components/ProductAnalysis/ProductAnalysisForm';
import PricePrediction from './components/ProductAnalysis/PricePrediction';
import MarketAnalysis from './components/ProductAnalysis/MarketAnalysis';
import HistoryPage from './components/History/HistoryPage';
import SettingsPage from './components/Settings/SettingsPage';

function App() {
  return (
    <AppContextProvider>
      <Router>
        <div className="flex flex-col min-h-screen bg-gray-50">
          <Header />
          <div className="flex flex-1">
            <Sidebar />
            <main className="flex-1 p-6 overflow-auto">
              <div className="max-w-7xl mx-auto">
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/product-analysis" element={<ProductAnalysisForm />} />
                  <Route path="/price-prediction/:id" element={<PricePrediction />} />
                  <Route path="/market-analysis/:id" element={<MarketAnalysis />} />
                  <Route path="/history" element={<HistoryPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                </Routes>
              </div>
            </main>
          </div>
          <Footer />
        </div>
      </Router>
    </AppContextProvider>
  );
}

export default App;