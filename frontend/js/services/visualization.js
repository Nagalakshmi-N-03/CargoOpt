export class VisualizationService {
    constructor() {
        this.baseUrl = '/api'; // Your backend API base URL
        this.cache = new Map();
        this.isInitialized = false;
    }

    async initialize() {
        if (this.isInitialized) return;
        
        try {
            // Check backend connectivity
            await this.healthCheck();
            this.isInitialized = true;
            console.log('VisualizationService initialized');
        } catch (error) {
            console.error('Failed to initialize VisualizationService:', error);
            throw error;
        }
    }

    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`);
        if (!response.ok) {
            throw new Error('Backend service unavailable');
        }
        return await response.json();
    }

    async runOptimization(optimizationData) {
        try {
            console.log('Running optimization with data:', optimizationData);
            
            const response = await fetch(`${this.baseUrl}/optimize`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(optimizationData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Optimization failed');
            }

            const result = await response.json();
            
            // Cache the result
            this.cache.set('last_optimization', result);
            
            // Emit event for real-time updates
            this.emitOptimizationComplete(result);
            
            return result;
        } catch (error) {
            console.error('Optimization error:', error);
            throw error;
        }
    }

    async validateContainers(containers) {
        try {
            const response = await fetch(`${this.baseUrl}/validate/containers`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ containers })
            });

            if (!response.ok) {
                throw new Error('Validation failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Validation error:', error);
            throw error;
        }
    }

    async validateVehicles(vehicles) {
        try {
            const response = await fetch(`${this.baseUrl}/validate/vehicles`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ vehicles })
            });

            if (!response.ok) {
                throw new Error('Validation failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Validation error:', error);
            throw error;
        }
    }

    async calculateEmissions(assignments, containers, vehicles, distance = 100) {
        try {
            const response = await fetch(`${this.baseUrl}/calculate/emissions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    assignments,
                    containers,
                    vehicles,
                    distance
                })
            });

            if (!response.ok) {
                throw new Error('Emission calculation failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Emission calculation error:', error);
            throw error;
        }
    }

    async exportResults(optimizationResult, format = 'json') {
        try {
            const response = await fetch(`${this.baseUrl}/export/results`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    result: optimizationResult,
                    format: format
                })
            });

            if (!response.ok) {
                throw new Error('Export failed');
            }

            const blob = await response.blob();
            const filename = this.getExportFilename(format);
            
            return {
                data: blob,
                contentType: response.headers.get('content-type'),
                filename: filename
            };
        } catch (error) {
            console.error('Export error:', error);
            throw error;
        }
    }

    getExportFilename(format) {
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        const baseName = `cargoopt_optimization_${timestamp}`;
        
        const extensions = {
            'json': '.json',
            'csv': '.csv',
            'xml': '.xml',
            'pdf': '.pdf'
        };
        
        return baseName + (extensions[format] || '.json');
    }

    async getOptimizationHistory() {
        try {
            const response = await fetch(`${this.baseUrl}/optimization/history`);
            
            if (!response.ok) {
                throw new Error('Failed to fetch optimization history');
            }

            return await response.json();
        } catch (error) {
            console.error('History fetch error:', error);
            throw error;
        }
    }

    async saveOptimizationScenario(scenarioData) {
        try {
            const response = await fetch(`${this.baseUrl}/scenarios/save`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(scenarioData)
            });

            if (!response.ok) {
                throw new Error('Failed to save scenario');
            }

            return await response.json();
        } catch (error) {
            console.error('Scenario save error:', error);
            throw error;
        }
    }

    async loadOptimizationScenario(scenarioId) {
        try {
            const response = await fetch(`${this.baseUrl}/scenarios/${scenarioId}`);
            
            if (!response.ok) {
                throw new Error('Failed to load scenario');
            }

            return await response.json();
        } catch (error) {
            console.error('Scenario load error:', error);
            throw error;
        }
    }

    async getReferenceData(type) {
        // Check cache first
        const cacheKey = `reference_${type}`;
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }

        try {
            const response = await fetch(`${this.baseUrl}/reference/${type}`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch ${type} reference data`);
            }

            const data = await response.json();
            this.cache.set(cacheKey, data);
            
            return data;
        } catch (error) {
            console.error('Reference data fetch error:', error);
            throw error;
        }
    }

    async getRealTimeMetrics() {
        try {
            const response = await fetch(`${this.baseUrl}/metrics/realtime`);
            
            if (!response.ok) {
                throw new Error('Failed to fetch real-time metrics');
            }

            return await response.json();
        } catch (error) {
            console.error('Real-time metrics error:', error);
            throw error;
        }
    }

    async simulateLoadingProcess(assignments, speed = 1) {
        try {
            const response = await fetch(`${this.baseUrl}/simulate/loading`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    assignments,
                    speed
                })
            });

            if (!response.ok) {
                throw new Error('Simulation failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Simulation error:', error);
            throw error;
        }
    }

    // Event system for real-time updates
    emitOptimizationComplete(result) {
        const event = new CustomEvent('optimizationComplete', {
            detail: { result }
        });
        document.dispatchEvent(event);
    }

    emitValidationComplete(validationResult) {
        const event = new CustomEvent('validationComplete', {
            detail: { validationResult }
        });
        document.dispatchEvent(event);
    }

    emitExportComplete(exportResult) {
        const event = new CustomEvent('exportComplete', {
            detail: { exportResult }
        });
        document.dispatchEvent(event);
    }

    // Utility methods
    formatContainerData(containers) {
        return containers.map(container => ({
            id: container.id,
            name: container.name,
            length: parseFloat(container.length),
            width: parseFloat(container.width),
            height: parseFloat(container.height),
            weight: parseFloat(container.weight),
            type: container.type,
            hazard_class: container.hazardClass,
            requires_refrigeration: container.requiresRefrigeration || false
        }));
    }

    formatVehicleData(vehicles) {
        return vehicles.map(vehicle => ({
            id: vehicle.id,
            type: vehicle.type,
            max_weight: parseFloat(vehicle.maxWeight),
            length: parseFloat(vehicle.length),
            width: parseFloat(vehicle.width),
            height: parseFloat(vehicle.height),
            emission_factor: parseFloat(vehicle.emissionFactor),
            can_carry_hazardous: vehicle.canCarryHazardous || false,
            has_refrigeration: vehicle.hasRefrigeration || false
        }));
    }

    calculateStatistics(optimizationResult) {
        const assignments = optimizationResult.assignments || {};
        const containers = optimizationResult.containers || [];
        const vehicles = optimizationResult.vehicles || [];

        const stats = {
            totalContainers: containers.length,
            totalVehicles: Object.keys(assignments).length,
            totalWeight: containers.reduce((sum, c) => sum + (c.weight || 0), 0),
            totalCapacity: vehicles.reduce((sum, v) => sum + (v.max_weight || 0), 0),
            averageUtilization: 0,
            emissionIntensity: 0
        };

        // Calculate average utilization
        let totalUtilization = 0;
        Object.entries(assignments).forEach(([vehicleId, containerIds]) => {
            const vehicle = vehicles.find(v => v.id === vehicleId);
            if (vehicle && vehicle.max_weight) {
                const assignedContainers = containers.filter(c => containerIds.includes(c.id));
                const totalWeight = assignedContainers.reduce((sum, c) => sum + (c.weight || 0), 0);
                totalUtilization += (totalWeight / vehicle.max_weight) * 100;
            }
        });

        stats.averageUtilization = totalUtilization / Object.keys(assignments).length;
        
        // Calculate emission intensity
        if (stats.totalWeight > 0) {
            stats.emissionIntensity = (optimizationResult.total_emissions || 0) / stats.totalWeight;
        }

        return stats;
    }

    generateReport(optimizationResult, format = 'summary') {
        const stats = this.calculateStatistics(optimizationResult);
        
        const report = {
            timestamp: new Date().toISOString(),
            summary: {
                status: optimizationResult.status,
                vehiclesUsed: stats.totalVehicles,
                containersAssigned: stats.totalContainers,
                totalEmissions: optimizationResult.total_emissions,
                averageUtilization: stats.averageUtilization,
                emissionIntensity: stats.emissionIntensity
            },
            assignments: optimizationResult.assignments,
            statistics: stats
        };

        if (format === 'detailed') {
            report.containers = optimizationResult.containers;
            report.vehicles = optimizationResult.vehicles;
            report.constraints = optimizationResult.constraints;
        }

        return report;
    }

    // Cache management
    clearCache() {
        this.cache.clear();
    }

    setCache(key, value, ttl = 300000) { // 5 minutes default TTL
        this.cache.set(key, {
            value,
            timestamp: Date.now(),
            ttl
        });
    }

    getCache(key) {
        const cached = this.cache.get(key);
        if (!cached) return null;

        if (Date.now() - cached.timestamp > cached.ttl) {
            this.cache.delete(key);
            return null;
        }

        return cached.value;
    }

    // Error handling
    handleError(error, context = '') {
        const errorMessage = `${context ? context + ': ' : ''}${error.message}`;
        console.error('VisualizationService Error:', errorMessage);
        
        // Emit error event
        const errorEvent = new CustomEvent('serviceError', {
            detail: { error: errorMessage, context }
        });
        document.dispatchEvent(errorEvent);
        
        throw new Error(errorMessage);
    }

    // Cleanup
    destroy() {
        this.clearCache();
        this.isInitialized = false;
        console.log('VisualizationService destroyed');
    }
}

// Singleton instance
export const visualizationService = new VisualizationService();

// Initialize service when module loads
visualizationService.initialize().catch(console.error);