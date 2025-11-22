/**
 * API Service
 * Handles all HTTP requests to the backend API
 */

import { API_BASE_URL, API_ENDPOINTS, HTTP_STATUS } from '../utils/constants.js';

export class API {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
    
    // Request queue for retry
    this.failedRequests = [];
    
    // Request interceptors
    this.requestInterceptors = [];
    this.responseInterceptors = [];
  }
  
  /**
   * Make HTTP request
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      method: options.method || 'GET',
      headers: {
        ...this.defaultHeaders,
        ...options.headers
      },
      ...options
    };
    
    // Add body if present
    if (options.body && typeof options.body === 'object') {
      config.body = JSON.stringify(options.body);
    }
    
    // Apply request interceptors
    this.requestInterceptors.forEach(interceptor => {
      interceptor(config);
    });
    
    try {
      const response = await fetch(url, config);
      
      // Apply response interceptors
      this.responseInterceptors.forEach(interceptor => {
        interceptor(response);
      });
      
      // Handle errors
      if (!response.ok) {
        await this.handleError(response);
      }
      
      // Parse response
      const data = await this.parseResponse(response);
      
      return data;
      
    } catch (error) {
      console.error('API request failed:', error);
      
      // Add to failed requests for retry
      if (options.retry !== false) {
        this.failedRequests.push({ endpoint, options });
      }
      
      throw error;
    }
  }
  
  /**
   * Parse response based on content type
   */
  async parseResponse(response) {
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    
    if (contentType && contentType.includes('text/')) {
      return await response.text();
    }
    
    if (contentType && contentType.includes('application/octet-stream')) {
      return await response.blob();
    }
    
    return response;
  }
  
  /**
   * Handle API errors
   */
  async handleError(response) {
    let errorMessage = 'An error occurred';
    
    try {
      const errorData = await response.json();
      errorMessage = errorData.message || errorData.error || errorMessage;
    } catch (e) {
      errorMessage = response.statusText || errorMessage;
    }
    
    const error = new Error(errorMessage);
    error.status = response.status;
    error.response = response;
    
    throw error;
  }
  
  /**
   * GET request
   */
  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    
    return this.request(url, { method: 'GET' });
  }
  
  /**
   * POST request
   */
  async post(endpoint, body = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body
    });
  }
  
  /**
   * PUT request
   */
  async put(endpoint, body = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body
    });
  }
  
  /**
   * DELETE request
   */
  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE'
    });
  }
  
  /**
   * Upload file
   */
  async uploadFile(endpoint, file, additionalData = {}) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Add additional data
    Object.keys(additionalData).forEach(key => {
      formData.append(key, additionalData[key]);
    });
    
    return this.request(endpoint, {
      method: 'POST',
      body: formData,
      headers: {
        // Don't set Content-Type, let browser set it with boundary
      }
    });
  }
  
  /**
   * Download file
   */
  async downloadFile(endpoint, filename) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      headers: this.defaultHeaders
    });
    
    if (!response.ok) {
      throw new Error('Download failed');
    }
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }
  
  // ============================================================================
  // API Endpoints
  // ============================================================================
  
  /**
   * Check API health
   */
  async checkHealth() {
    return this.get(API_ENDPOINTS.HEALTH);
  }
  
  /**
   * Get API info
   */
  async getInfo() {
    return this.get(API_ENDPOINTS.INFO);
  }
  
  /**
   * Get configuration
   */
  async getConfig() {
    return this.get(API_ENDPOINTS.CONFIG);
  }
  
  /**
   * Submit optimization request
   */
  async optimize(data) {
    return this.post(API_ENDPOINTS.OPTIMIZE, data);
  }
  
  /**
   * Get optimization status
   */
  async getOptimizationStatus(optimizationId) {
    return this.get(`${API_ENDPOINTS.OPTIMIZE}/${optimizationId}/status`);
  }
  
  /**
   * Get optimization result
   */
  async getOptimizationResult(optimizationId) {
    return this.get(`${API_ENDPOINTS.OPTIMIZE}/${optimizationId}`);
  }
  
  /**
   * Cancel optimization
   */
  async cancelOptimization(optimizationId) {
    return this.post(`${API_ENDPOINTS.OPTIMIZE}/${optimizationId}/cancel`);
  }
  
  /**
   * Delete optimization
   */
  async deleteOptimization(optimizationId) {
    return this.delete(`${API_ENDPOINTS.OPTIMIZE}/${optimizationId}`);
  }
  
  /**
   * Get optimization history
   */
  async getOptimizationHistory(params = {}) {
    return this.get(API_ENDPOINTS.HISTORY, params);
  }
  
  /**
   * Export optimization result
   */
  async exportResult(optimizationId, format = 'pdf') {
    const response = await fetch(
      `${this.baseURL}${API_ENDPOINTS.EXPORTS}/${optimizationId}?format=${format}`,
      { headers: this.defaultHeaders }
    );
    
    if (!response.ok) {
      throw new Error('Export failed');
    }
    
    return await response.blob();
  }
  
  /**
   * Validate optimization data
   */
  async validateOptimization(data) {
    return this.post(API_ENDPOINTS.VALIDATE, data);
  }
  
  /**
   * Get containers
   */
  async getContainers(params = {}) {
    return this.get(API_ENDPOINTS.CONTAINERS, params);
  }
  
  /**
   * Get container by ID
   */
  async getContainer(containerId) {
    return this.get(`${API_ENDPOINTS.CONTAINERS}/${containerId}`);
  }
  
  /**
   * Create container
   */
  async createContainer(data) {
    return this.post(API_ENDPOINTS.CONTAINERS, data);
  }
  
  /**
   * Update container
   */
  async updateContainer(containerId, data) {
    return this.put(`${API_ENDPOINTS.CONTAINERS}/${containerId}`, data);
  }
  
  /**
   * Delete container
   */
  async deleteContainer(containerId) {
    return this.delete(`${API_ENDPOINTS.CONTAINERS}/${containerId}`);
  }
  
  /**
   * Get items
   */
  async getItems(params = {}) {
    return this.get(API_ENDPOINTS.ITEMS, params);
  }
  
  /**
   * Get item by ID
   */
  async getItem(itemId) {
    return this.get(`${API_ENDPOINTS.ITEMS}/${itemId}`);
  }
  
  /**
   * Create item
   */
  async createItem(data) {
    return this.post(API_ENDPOINTS.ITEMS, data);
  }
  
  /**
   * Update item
   */
  async updateItem(itemId, data) {
    return this.put(`${API_ENDPOINTS.ITEMS}/${itemId}`, data);
  }
  
  /**
   * Delete item
   */
  async deleteItem(itemId) {
    return this.delete(`${API_ENDPOINTS.ITEMS}/${itemId}`);
  }
  
  /**
   * Bulk create items
   */
  async bulkCreateItems(items) {
    return this.post(`${API_ENDPOINTS.ITEMS}/bulk`, { items });
  }
  
  /**
   * Import items from CSV
   */
  async importItemsCSV(file) {
    return this.uploadFile(`${API_ENDPOINTS.ITEMS}/import`, file);
  }
  
  /**
   * Get statistics
   */
  async getStatistics() {
    return this.get(API_ENDPOINTS.STATS);
  }
  
  /**
   * Calculate emissions
   */
  async calculateEmissions(data) {
    return this.post(`${API_ENDPOINTS.OPTIMIZE}/emissions`, data);
  }
  
  /**
   * Get stowage plan
   */
  async getStowagePlan(planId) {
    return this.get(`${API_ENDPOINTS.STOWAGE}/${planId}`);
  }
  
  /**
   * Create stowage plan
   */
  async createStowagePlan(data) {
    return this.post(API_ENDPOINTS.STOWAGE, data);
  }
  
  /**
   * Validate stowage plan
   */
  async validateStowagePlan(data) {
    return this.post(`${API_ENDPOINTS.STOWAGE}/validate`, data);
  }
  
  // ============================================================================
  // Utility Methods
  // ============================================================================
  
  /**
   * Add request interceptor
   */
  addRequestInterceptor(interceptor) {
    this.requestInterceptors.push(interceptor);
  }
  
  /**
   * Add response interceptor
   */
  addResponseInterceptor(interceptor) {
    this.responseInterceptors.push(interceptor);
  }
  
  /**
   * Set authentication token
   */
  setAuthToken(token) {
    this.defaultHeaders['Authorization'] = `Bearer ${token}`;
  }
  
  /**
   * Remove authentication token
   */
  removeAuthToken() {
    delete this.defaultHeaders['Authorization'];
  }
  
  /**
   * Retry failed requests
   */
  async retryFailedRequests() {
    const requests = [...this.failedRequests];
    this.failedRequests = [];
    
    const results = [];
    
    for (const { endpoint, options } of requests) {
      try {
        const result = await this.request(endpoint, { ...options, retry: false });
        results.push({ success: true, result });
      } catch (error) {
        results.push({ success: false, error });
      }
    }
    
    return results;
  }
  
  /**
   * Clear failed requests
   */
  clearFailedRequests() {
    this.failedRequests = [];
  }
}

// Create singleton instance
export const api = new API();

// Export default
export default API;