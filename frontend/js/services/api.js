// API Service for handling all backend communication
class ApiService {
    constructor() {
        // FIXED: Changed from port 5000 to 8000 to match your running backend
        this.baseUrl = 'http://localhost:8000/api/v1';
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options,
        };

        try {
            console.log(`🌐 API Request: ${config.method || 'GET'} ${url}`);
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText || response.statusText}`);
            }

            const data = await response.json();
            console.log('✅ API Response:', data);
            return { success: true, data };
        } catch (error) {
            console.error('❌ API request failed:', error);
            return { 
                success: false, 
                error: error.message,
                status: error.status
            };
        }
    }

    // Health and System endpoints
    async getHealth() {
        return await this.request('/health');
    }

    async getSystemStatus() {
        return await this.request('/services/status');
    }

    async getAlgorithms() {
        return await this.request('/algorithms');
    }

    async getContainerTypes() {
        return await this.request('/containers/types');
    }

    // Optimization endpoints
    async optimizeAuto(requestData) {
        return await this.request('/optimize/auto', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
    }

    async optimizePacking(requestData) {
        return await this.request('/optimize/packing', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
    }

    async optimizeGenetic(requestData) {
        return await this.request('/optimize/genetic', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
    }

    async optimizeStowage(requestData) {
        return await this.request('/optimize/stowage', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
    }

    async compareAlgorithms(requestData) {
        return await this.request('/optimize/compare', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
    }

    async batchOptimize(requestData) {
        return await this.request('/optimize/batch', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
    }

    async getBatchStatus(batchId) {
        return await this.request(`/optimize/batch/${batchId}/status`);
    }

    // Validation endpoints
    async validateData(container, items) {
        return await this.request('/validate/data', {
            method: 'POST',
            body: JSON.stringify({ container, items })
        });
    }

    async validatePlacement(requestData) {
        return await this.request('/validate/placement', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
    }

    // History endpoints
    async getOptimizationHistory(limit = 10, algorithm = null, minUtilization = null, maxUtilization = null) {
        let url = `/optimize/history?limit=${limit}`;
        
        if (algorithm) url += `&algorithm=${algorithm}`;
        if (minUtilization !== null) url += `&min_utilization=${minUtilization}`;
        if (maxUtilization !== null) url += `&max_utilization=${maxUtilization}`;
        
        return await this.request(url);
    }

    // Export endpoints
    async exportResult(result, format = 'excel') {
        return await this.request('/export/result', {
            method: 'POST',
            body: JSON.stringify({ result, format })
        });
    }

    async downloadExport(exportId) {
        const response = await fetch(`${this.baseUrl}/export/download/${exportId}`);
        
        if (!response.ok) {
            throw new Error('Download failed');
        }

        const blob = await response.blob();
        return blob;
    }

    // Utility methods for API response handling
    handleApiResponse(response, successMessage = null, errorMessage = null) {
        if (response.success) {
            if (successMessage) {
                this.showNotification(successMessage, 'success');
            }
            return response.data;
        } else {
            const message = errorMessage || response.error || 'Operation failed';
            this.showNotification(message, 'error');
            throw new Error(message);
        }
    }

    // File upload handling (for future use)
    async uploadFile(file, endpoint) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('File upload failed:', error);
            throw error;
        }
    }

    // Real-time updates via WebSocket (for future use)
    connectWebSocket() {
        const wsUrl = this.baseUrl.replace('http', 'ws') + '/ws';
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            // Attempt to reconnect after 5 seconds
            setTimeout(() => this.connectWebSocket(), 5000);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    handleWebSocketMessage(data) {
        // Handle real-time updates from the server
        switch (data.type) {
            case 'optimization_progress':
                this.handleOptimizationProgress(data);
                break;
            case 'system_status':
                this.handleSystemStatusUpdate(data);
                break;
            case 'batch_update':
                this.handleBatchUpdate(data);
                break;
            default:
                console.log('Unknown WebSocket message type:', data.type);
        }
    }

    handleOptimizationProgress(data) {
        // Update UI with optimization progress
        const progressEvent = new CustomEvent('optimizationProgress', {
            detail: data
        });
        window.dispatchEvent(progressEvent);
    }

    handleSystemStatusUpdate(data) {
        // Update system status in UI
        const statusEvent = new CustomEvent('systemStatusUpdate', {
            detail: data
        });
        window.dispatchEvent(statusEvent);
    }

    handleBatchUpdate(data) {
        // Update batch processing status
        const batchEvent = new CustomEvent('batchUpdate', {
            detail: data
        });
        window.dispatchEvent(batchEvent);
    }

    // Method to show notifications (integrated with the app's notification system)
    showNotification(message, type = 'info') {
        // This will be connected to the main app's notification system
        if (window.app && window.app.showNotification) {
            window.app.showNotification(message, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }
}

// Create a singleton instance
const apiService = new ApiService();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = apiService;
} else {
    window.apiService = apiService;
}