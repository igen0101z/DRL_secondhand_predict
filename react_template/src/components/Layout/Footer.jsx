import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 md:flex md:items-center md:justify-between">
        <div className="flex justify-center md:justify-start space-x-6">
          <p className="text-sm text-gray-500">
            &copy; {new Date().getFullYear()} DRL 二手價格預測系統
          </p>
        </div>
        <div className="mt-4 md:mt-0">
          <p className="text-xs text-gray-400">
            本系統使用強化學習模型進行預測，僅供參考，不構成投資建議
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;