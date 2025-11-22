/**
 * Utility Helper Functions
 * Common utility functions used throughout the application
 */

/**
 * Format number with thousands separator
 */
export function formatNumber(number, decimals = 0) {
  if (number === null || number === undefined) return '0';
  
  return Number(number).toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
}

/**
 * Format file size in human readable format
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Format date in various formats
 */
export function formatDate(date, format = 'full') {
  if (!date) return 'N/A';
  
  const d = new Date(date);
  
  if (isNaN(d.getTime())) return 'Invalid Date';
  
  switch (format) {
    case 'short':
      return d.toLocaleDateString();
    case 'long':
      return d.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    case 'time':
      return d.toLocaleTimeString();
    case 'datetime':
      return d.toLocaleString();
    case 'iso':
      return d.toISOString();
    case 'relative':
      return formatRelativeTime(d);
    default:
      return d.toLocaleString();
  }
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date) {
  const now = new Date();
  const diff = now - new Date(date);
  
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  const months = Math.floor(days / 30);
  const years = Math.floor(days / 365);
  
  if (seconds < 60) return 'Just now';
  if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  if (days < 30) return `${days} day${days > 1 ? 's' : ''} ago`;
  if (months < 12) return `${months} month${months > 1 ? 's' : ''} ago`;
  return `${years} year${years > 1 ? 's' : ''} ago`;
}

/**
 * Format duration in seconds to readable format
 */
export function formatDuration(seconds) {
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  }
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  
  if (minutes < 60) {
    return `${minutes}m ${remainingSeconds}s`;
  }
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  
  return `${hours}h ${remainingMinutes}m`;
}

/**
 * Format percentage
 */
export function formatPercentage(value, decimals = 1) {
  if (value === null || value === undefined) return '0%';
  return `${Number(value).toFixed(decimals)}%`;
}

/**
 * Truncate string with ellipsis
 */
export function truncate(str, length = 50, ending = '...') {
  if (!str) return '';
  if (str.length <= length) return str;
  return str.substring(0, length - ending.length) + ending;
}

/**
 * Debounce function
 */
export function debounce(func, wait = 300) {
  let timeout;
  
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Throttle function
 */
export function throttle(func, limit = 300) {
  let inThrottle;
  
  return function executedFunction(...args) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * Deep clone object
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj;
  
  if (obj instanceof Date) return new Date(obj.getTime());
  if (obj instanceof Array) return obj.map(item => deepClone(item));
  if (obj instanceof Object) {
    const clonedObj = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key]);
      }
    }
    return clonedObj;
  }
}

/**
 * Generate unique ID
 */
export function generateId(prefix = 'id') {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Generate UUID v4
 */
export function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * Convert hex color to RGB
 */
export function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
}

/**
 * Convert RGB to hex color
 */
export function rgbToHex(r, g, b) {
  return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

/**
 * Generate random color
 */
export function randomColor() {
  return '#' + Math.floor(Math.random()*16777215).toString(16);
}

/**
 * Calculate distance between two points
 */
export function distance(x1, y1, x2, y2) {
  return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
}

/**
 * Clamp value between min and max
 */
export function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

/**
 * Linear interpolation
 */
export function lerp(start, end, t) {
  return start + (end - start) * t;
}

/**
 * Map value from one range to another
 */
export function mapRange(value, inMin, inMax, outMin, outMax) {
  return (value - inMin) * (outMax - outMin) / (inMax - inMin) + outMin;
}

/**
 * Check if value is numeric
 */
export function isNumeric(value) {
  return !isNaN(parseFloat(value)) && isFinite(value);
}

/**
 * Parse CSV string
 */
export function parseCSV(csv) {
  const lines = csv.split('\n');
  const result = [];
  const headers = lines[0].split(',').map(h => h.trim());
  
  for (let i = 1; i < lines.length; i++) {
    if (!lines[i].trim()) continue;
    
    const values = lines[i].split(',');
    const obj = {};
    
    headers.forEach((header, index) => {
      obj[header] = values[index] ? values[index].trim() : '';
    });
    
    result.push(obj);
  }
  
  return result;
}

/**
 * Convert object to CSV
 */
export function toCSV(data, headers = null) {
  if (!data || data.length === 0) return '';
  
  const keys = headers || Object.keys(data[0]);
  const csvHeaders = keys.join(',');
  
  const csvRows = data.map(row => {
    return keys.map(key => {
      const value = row[key];
      return typeof value === 'string' && value.includes(',') 
        ? `"${value}"` 
        : value;
    }).join(',');
  });
  
  return [csvHeaders, ...csvRows].join('\n');
}

/**
 * Download data as file
 */
export function downloadFile(content, filename, mimeType = 'text/plain') {
  const blob = new Blob([content], { type: mimeType });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

/**
 * Copy text to clipboard
 */
export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    // Fallback for older browsers
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    const success = document.execCommand('copy');
    document.body.removeChild(textarea);
    return success;
  }
}

/**
 * Get query parameters from URL
 */
export function getQueryParams() {
  const params = {};
  const queryString = window.location.search.substring(1);
  const pairs = queryString.split('&');
  
  pairs.forEach(pair => {
    const [key, value] = pair.split('=');
    if (key) {
      params[decodeURIComponent(key)] = decodeURIComponent(value || '');
    }
  });
  
  return params;
}

/**
 * Set query parameter in URL
 */
export function setQueryParam(key, value) {
  const url = new URL(window.location);
  url.searchParams.set(key, value);
  window.history.pushState({}, '', url);
}

/**
 * Validate email
 */
export function isValidEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

/**
 * Validate URL
 */
export function isValidURL(url) {
  try {
    new URL(url);
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Calculate volume (L x W x H)
 */
export function calculateVolume(length, width, height) {
  return length * width * height;
}

/**
 * Calculate volume in cubic meters from mm
 */
export function volumeToM3(volumeMm3) {
  return volumeMm3 / 1e9;
}

/**
 * Calculate weight utilization percentage
 */
export function calculateWeightUtilization(usedWeight, maxWeight) {
  if (maxWeight === 0) return 0;
  return (usedWeight / maxWeight) * 100;
}

/**
 * Calculate space utilization percentage
 */
export function calculateSpaceUtilization(usedVolume, totalVolume) {
  if (totalVolume === 0) return 0;
  return (usedVolume / totalVolume) * 100;
}

/**
 * Sort array by property
 */
export function sortBy(array, property, ascending = true) {
  return array.sort((a, b) => {
    const aVal = a[property];
    const bVal = b[property];
    
    if (aVal < bVal) return ascending ? -1 : 1;
    if (aVal > bVal) return ascending ? 1 : -1;
    return 0;
  });
}

/**
 * Group array by property
 */
export function groupBy(array, property) {
  return array.reduce((groups, item) => {
    const key = item[property];
    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(item);
    return groups;
  }, {});
}

/**
 * Get unique values from array
 */
export function unique(array) {
  return [...new Set(array)];
}

/**
 * Sleep/delay function
 */
export function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Retry function with exponential backoff
 */
export async function retry(fn, maxAttempts = 3, delay = 1000) {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxAttempts) throw error;
      await sleep(delay * Math.pow(2, attempt - 1));
    }
  }
}

/**
 * Check if object is empty
 */
export function isEmpty(obj) {
  return Object.keys(obj).length === 0;
}

/**
 * Merge objects deeply
 */
export function mergeDeep(target, ...sources) {
  if (!sources.length) return target;
  const source = sources.shift();
  
  if (isObject(target) && isObject(source)) {
    for (const key in source) {
      if (isObject(source[key])) {
        if (!target[key]) Object.assign(target, { [key]: {} });
        mergeDeep(target[key], source[key]);
      } else {
        Object.assign(target, { [key]: source[key] });
      }
    }
  }
  
  return mergeDeep(target, ...sources);
}

/**
 * Check if value is object
 */
function isObject(item) {
  return item && typeof item === 'object' && !Array.isArray(item);
}

/**
 * Capitalize first letter
 */
export function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

/**
 * Convert snake_case to camelCase
 */
export function snakeToCamel(str) {
  return str.replace(/_([a-z])/g, (match, letter) => letter.toUpperCase());
}

/**
 * Convert camelCase to snake_case
 */
export function camelToSnake(str) {
  return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
}

/**
 * Get nested property value safely
 */
export function getNestedValue(obj, path, defaultValue = null) {
  const keys = path.split('.');
  let value = obj;
  
  for (const key of keys) {
    if (value && typeof value === 'object' && key in value) {
      value = value[key];
    } else {
      return defaultValue;
    }
  }
  
  return value;
}

/**
 * Set nested property value
 */
export function setNestedValue(obj, path, value) {
  const keys = path.split('.');
  const lastKey = keys.pop();
  let target = obj;
  
  for (const key of keys) {
    if (!(key in target) || typeof target[key] !== 'object') {
      target[key] = {};
    }
    target = target[key];
  }
  
  target[lastKey] = value;
}