// Utility functions for formatting and data manipulation

/**
 * Format a number as currency in TWD (NT$)
 * @param {number} amount - The amount to format
 * @returns {string} - Formatted currency string
 */
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('zh-TW', {
    style: 'currency',
    currency: 'TWD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
};

/**
 * Format a date string in locale format
 * @param {string} dateString - ISO date string to format
 * @returns {string} - Formatted date string
 */
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('zh-TW', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date);
};

/**
 * Format a date string to a relative time (e.g. "3 days ago")
 * @param {string} dateString - ISO date string
 * @returns {string} - Relative time string
 */
const formatRelativeTime = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now - date);
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
  const diffMinutes = Math.floor(diffTime / (1000 * 60));

  if (diffDays > 30) {
    return formatDate(dateString);
  } else if (diffDays > 0) {
    return `${diffDays} 天前`;
  } else if (diffHours > 0) {
    return `${diffHours} 小時前`;
  } else if (diffMinutes > 0) {
    return `${diffMinutes} 分鐘前`;
  } else {
    return '剛剛';
  }
};

/**
 * Calculate the percentage difference between two values
 * @param {number} value1 - First value
 * @param {number} value2 - Second value
 * @returns {string} - Percentage difference with sign
 */
const calculatePercentageDiff = (value1, value2) => {
  const diff = ((value1 - value2) / value2) * 100;
  const sign = diff > 0 ? '+' : '';
  return `${sign}${diff.toFixed(1)}%`;
};

/**
 * Truncate text with ellipsis if it exceeds a certain length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length before truncation
 * @returns {string} - Truncated text
 */
const truncateText = (text, maxLength) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

/**
 * Debounce a function call
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} - Debounced function
 */
const debounce = (func, wait) => {
  let timeout;
  return function(...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), wait);
  };
};

/**
 * Generate a random color
 * @returns {string} - Hex color code
 */
const getRandomColor = () => {
  return `#${Math.floor(Math.random()*16777215).toString(16)}`;
};

export {
  formatCurrency,
  formatDate,
  formatRelativeTime,
  calculatePercentageDiff,
  truncateText,
  debounce,
  getRandomColor
};