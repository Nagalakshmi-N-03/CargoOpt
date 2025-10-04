import { VisualizationService } from '../services/visualization.js';

export class Dashboard {
    constructor() {
        this.visualizationService = new VisualizationService();
        this.currentOptimizationResult = null;
        this.isLoading = false;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSampleData();
        this.setupRealTimeUpdates();
    }

    bindEvents() {
        // Optimization controls
        document.getElementById('run-optimization')?.addEventListener('click', () => this.runOptimization());
        document.getElementById('reset-view')?.addEventListener('click', () => this.resetView());
        document.getElementById('export-results')?.addEventListener('click', () => this.exportResults());
        
        // View controls
        document.getElementById('toggle-3d-view')?.addEventListener('click', () => this.toggle3DView());
        document.getElementById('toggle-labels')?.addEventListener('click', () => this.toggleLabels());
        document.getElementById('toggle-animation')?.addEventListener('click', () => this.toggleAnimation());
        
        // Filter controls
        document.getElementById('filter-vehicle')?.addEventListener('change', (e) => this.filterByVehicle(e.target.value));
        document.getElementById('filter-container-type')?.addEventListener('change', (e) => this.filterByContainerType(e.target.value));
        document.getElementById('search-containers')?.addEventListener('input', (e) => this.searchContainers(e.target.value));
        
        // Container selection
        document.addEventListener('containerSelected', (e) => this.onContainerSelected(e.detail));
        document.addEventListener('containerFocused', (e) => this.onContainerFocused(e.detail));
        
        // Vehicle selection
        document.addEventListener('vehicleSelected', (e) => this.onVehicleSelected(e.detail));
    }

    async runOptimization() {
        this.setLoadingState(true);
        
        try {
            const containers = this.getContainerData();
            const vehicles = this.getVehicleData();
            const constraints = this.getConstraintData();
            
            const result = await this.visualizationService.runOptimization({
                containers,
                vehicles,
                constraints,
                distance: parseFloat(document.getElementById('distance-input')?.value || 100)
            });
            
            this.currentOptimizationResult = result;
            this.displayResults(result);
            this.updateVisualization(result);
            this.updateMetrics(result);
            
        } catch (error) {
            this.showError('Optimization failed: ' + error.message);
        } finally {
            this.setLoadingState(false);
        }
    }

    displayResults(result) {
        this.updateSummaryPanel(result);
        this.updateAssignmentsTable(result);
        this.updateEmissionStats(result);
        this.updateUtilizationCharts(result);
    }

    updateSummaryPanel(result) {
        const summaryElement = document.getElementById('optimization-summary');
        if (!summaryElement) return;

        summaryElement.innerHTML = `
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="summary-value">${result.vehicle_count || 0}</div>
                    <div class="summary-label">Vehicles Used</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value">${result.total_containers || 0}</div>
                    <div class="summary-label">Containers</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value">${result.utilization ? result.utilization.toFixed(1) + '%' : 'N/A'}</div>
                    <div class="summary-label">Utilization</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value">${result.total_emissions ? result.total_emissions.toFixed(2) + ' kg' : 'N/A'}</div>
                    <div class="summary-label">CO₂ Emissions</div>
                </div>
            </div>
        `;
    }

    updateAssignmentsTable(result) {
        const tableElement = document.getElementById('assignments-table');
        if (!tableElement || !result.assignments) return;

        let tableHTML = `
            <table class="assignments-table">
                <thead>
                    <tr>
                        <th>Vehicle</th>
                        <th>Containers</th>
                        <th>Total Weight</th>
                        <th>Utilization</th>
                        <th>Emissions</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
        `;

        Object.entries(result.assignments).forEach(([vehicleId, containerIds]) => {
            const vehicle = result.vehicles?.find(v => v.id === vehicleId) || {};
            const containers = result.containers?.filter(c => containerIds.includes(c.id)) || [];
            const totalWeight = containers.reduce((sum, c) => sum + (c.weight || 0), 0);
            const utilization = vehicle.max_weight ? (totalWeight / vehicle.max_weight * 100) : 0;
            const emissions = containers.reduce((sum, c) => sum + (c.weight || 0) * (vehicle.emission_factor || 0) * 100, 0);

            tableHTML += `
                <tr data-vehicle-id="${vehicleId}">
                    <td>
                        <strong>${vehicle.type || vehicleId}</strong>
                        <br><small>Max: ${vehicle.max_weight || 0} kg</small>
                    </td>
                    <td>
                        <div class="container-list">
                            ${containers.map(c => `
                                <span class="container-tag" data-container-id="${c.id}">
                                    ${c.name || c.id}
                                </span>
                            `).join('')}
                        </div>
                    </td>
                    <td>${totalWeight.toFixed(1)} kg</td>
                    <td>
                        <div class="utilization-bar">
                            <div class="utilization-fill" style="width: ${utilization}%"></div>
                            <span class="utilization-text">${utilization.toFixed(1)}%</span>
                        </div>
                    </td>
                    <td>${emissions.toFixed(2)} kg</td>
                    <td>
                        <button class="btn-sm btn-view" onclick="dashboard.highlightVehicle('${vehicleId}')">
                            View
                        </button>
                    </td>
                </tr>
            `;
        });

        tableHTML += '</tbody></table>';
        tableElement.innerHTML = tableHTML;

        // Add click handlers for container tags
        tableElement.querySelectorAll('.container-tag').forEach(tag => {
            tag.addEventListener('click', (e) => {
                e.stopPropagation();
                const containerId = tag.getAttribute('data-container-id');
                this.highlightContainer(containerId);
            });
        });
    }

    updateEmissionStats(result) {
        const emissionsElement = document.getElementById('emission-stats');
        if (!emissionsElement) return;

        const totalEmissions = result.total_emissions || 0;
        const equivalentMetrics = this.calculateEquivalentMetrics(totalEmissions);

        emissionsElement.innerHTML = `
            <div class="emission-metrics">
                <div class="emission-item">
                    <div class="emission-icon">🚗</div>
                    <div class="emission-value">${equivalentMetrics.car_km.toFixed(0)} km</div>
                    <div class="emission-label">Car Distance Equivalent</div>
                </div>
                <div class="emission-item">
                    <div class="emission-icon">🌳</div>
                    <div class="emission-value">${equivalentMetrics.trees.toFixed(1)} trees</div>
                    <div class="emission-label">Annual Tree Absorption</div>
                </div>
                <div class="emission-item">
                    <div class="emission-icon">⛽</div>
                    <div class="emission-value">${equivalentMetrics.gasoline.toFixed(1)} L</div>
                    <div class="emission-label">Gasoline Equivalent</div>
                </div>
                <div class="emission-item">
                    <div class="emission-icon">📱</div>
                    <div class="emission-value">${equivalentMetrics.phone_charges.toFixed(0)}</div>
                    <div class="emission-label">Phone Charges</div>
                </div>
            </div>
        `;
    }

    calculateEquivalentMetrics(emissionsKg) {
        return {
            car_km: emissionsKg * 10, // Average car: 0.2 kg CO2 per km
            trees: emissionsKg * 0.02, // One tree absorbs ~50 kg CO2 per year
            gasoline: emissionsKg * 0.43, // 1L gasoline ≈ 2.3 kg CO2
            phone_charges: emissionsKg * 121 // Based on average smartphone energy use
        };
    }

    updateUtilizationCharts(result) {
        // Initialize or update charts for vehicle utilization
        this.updateVehicleUtilizationChart(result);
        this.updateWeightDistributionChart(result);
    }

    updateVehicleUtilizationChart(result) {
        const chartElement = document.getElementById('utilization-chart');
        if (!chartElement) return;

        // Simple bar chart implementation
        // In a real app, you might use Chart.js or similar
        const assignments = result.assignments || {};
        const vehicles = result.vehicles || [];
        
        let chartHTML = '<div class="utilization-chart">';
        
        Object.entries(assignments).forEach(([vehicleId, containerIds]) => {
            const vehicle = vehicles.find(v => v.id === vehicleId);
            if (!vehicle) return;
            
            const containers = result.containers?.filter(c => containerIds.includes(c.id)) || [];
            const totalWeight = containers.reduce((sum, c) => sum + (c.weight || 0), 0);
            const utilization = vehicle.max_weight ? (totalWeight / vehicle.max_weight * 100) : 0;
            
            chartHTML += `
                <div class="chart-bar">
                    <div class="bar-label">${vehicle.type || vehicleId}</div>
                    <div class="bar-container">
                        <div class="bar-fill" style="width: ${utilization}%"></div>
                        <div class="bar-text">${utilization.toFixed(1)}%</div>
                    </div>
                </div>
            `;
        });
        
        chartHTML += '</div>';
        chartElement.innerHTML = chartHTML;
    }

    updateWeightDistributionChart(result) {
        // Implementation for weight distribution chart
        const chartElement = document.getElementById('weight-chart');
        if (!chartElement) return;

        // Simple implementation - extend with proper chart library
        chartElement.innerHTML = '<p>Weight distribution visualization</p>';
    }

    updateVisualization(result) {
        if (window.CargoOpt3D && window.CargoOpt3D.loadOptimizationResult) {
            window.CargoOpt3D.loadOptimizationResult(result);
        }
    }

    updateMetrics(result) {
        // Update real-time metrics display
        this.updatePerformanceMetrics(result);
        this.updateEnvironmentalImpact(result);
    }

    updatePerformanceMetrics(result) {
        const metricsElement = document.getElementById('performance-metrics');
        if (!metricsElement) return;

        const assignments = result.assignments || {};
        const totalContainers = result.total_containers || 0;
        const vehicleCount = Object.keys(assignments).length;

        metricsElement.innerHTML = `
            <div class="metrics-grid">
                <div class="metric-card">
                    <h4>Efficiency</h4>
                    <div class="metric-value">${((totalContainers / vehicleCount) || 0).toFixed(1)}</div>
                    <div class="metric-label">Containers per Vehicle</div>
                </div>
                <div class="metric-card">
                    <h4>Capacity Usage</h4>
                    <div class="metric-value">${(result.utilization || 0).toFixed(1)}%</div>
                    <div class="metric-label">Average Utilization</div>
                </div>
                <div class="metric-card">
                    <h4>Cost Savings</h4>
                    <div class="metric-value">${this.calculateCostSavings(result)}%</div>
                    <div class="metric-label">vs. Baseline</div>
                </div>
            </div>
        `;
    }

    calculateCostSavings(result) {
        // Simplified cost savings calculation
        const baselineEmissions = (result.total_containers || 0) * 100 * 0.00015 * 100; // Conservative baseline
        const optimizedEmissions = result.total_emissions || baselineEmissions;
        const savings = ((baselineEmissions - optimizedEmissions) / baselineEmissions) * 100;
        return Math.max(0, savings).toFixed(1);
    }

    updateEnvironmentalImpact(result) {
        const impactElement = document.getElementById('environmental-impact');
        if (!impactElement) return;

        const totalEmissions = result.total_emissions || 0;
        const equivalentMetrics = this.calculateEquivalentMetrics(totalEmissions);

        impactElement.innerHTML = `
            <div class="impact-stats">
                <div class="impact-item">
                    <span class="impact-value">${totalEmissions.toFixed(2)} kg CO₂</span>
                    <span class="impact-label">Total Emissions</span>
                </div>
                <div class="impact-item">
                    <span class="impact-value">${equivalentMetrics.car_km.toFixed(0)} km</span>
                    <span class="impact-label">Equivalent Car Distance</span>
                </div>
                <div class="impact-item">
                    <span class="impact-value">${equivalentMetrics.trees.toFixed(1)}</span>
                    <span class="impact-label">Trees Needed to Absorb</span>
                </div>
            </div>
        `;
    }

    highlightContainer(containerId) {
        if (window.CargoOpt3D && window.CargoOpt3D.scene) {
            window.CargoOpt3D.scene.highlightContainer(containerId);
        }
        
        // Update UI to show container details
        this.showContainerDetails(containerId);
    }

    highlightVehicle(vehicleId) {
        if (window.CargoOpt3D && window.CargoOpt3D.scene) {
            window.CargoOpt3D.scene.highlightVehicle(vehicleId);
        }
        
        // Update UI to show vehicle details
        this.showVehicleDetails(vehicleId);
    }

    showContainerDetails(containerId) {
        const container = this.currentOptimizationResult?.containers?.find(c => c.id === containerId);
        if (!container) return;

        const detailsElement = document.getElementById('container-details');
        if (!detailsElement) return;

        detailsElement.innerHTML = `
            <div class="container-details">
                <h4>${container.name || container.id}</h4>
                <div class="detail-grid">
                    <div class="detail-item">
                        <label>Dimensions:</label>
                        <span>${container.length} × ${container.width} × ${container.height} m</span>
                    </div>
                    <div class="detail-item">
                        <label>Weight:</label>
                        <span>${container.weight} kg</span>
                    </div>
                    <div class="detail-item">
                        <label>Type:</label>
                        <span>${container.type || 'Standard'}</span>
                    </div>
                    ${container.hazard_class ? `
                    <div class="detail-item">
                        <label>Hazard Class:</label>
                        <span class="hazard-warning">${container.hazard_class}</span>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        detailsElement.style.display = 'block';
    }

    showVehicleDetails(vehicleId) {
        const vehicle = this.currentOptimizationResult?.vehicles?.find(v => v.id === vehicleId);
        if (!vehicle) return;

        const detailsElement = document.getElementById('vehicle-details');
        if (!detailsElement) return;

        const assignments = this.currentOptimizationResult?.assignments?.[vehicleId] || [];
        const containers = this.currentOptimizationResult?.containers?.filter(c => assignments.includes(c.id)) || [];
        const totalWeight = containers.reduce((sum, c) => sum + (c.weight || 0), 0);
        const utilization = vehicle.max_weight ? (totalWeight / vehicle.max_weight * 100) : 0;

        detailsElement.innerHTML = `
            <div class="vehicle-details">
                <h4>${vehicle.type || vehicle.id}</h4>
                <div class="detail-grid">
                    <div class="detail-item">
                        <label>Max Weight:</label>
                        <span>${vehicle.max_weight} kg</span>
                    </div>
                    <div class="detail-item">
                        <label>Current Load:</label>
                        <span>${totalWeight} kg (${utilization.toFixed(1)}%)</span>
                    </div>
                    <div class="detail-item">
                        <label>Containers:</label>
                        <span>${containers.length}</span>
                    </div>
                    <div class="detail-item">
                        <label>Emission Factor:</label>
                        <span>${vehicle.emission_factor} kg/km·kg</span>
                    </div>
                </div>
                <div class="containers-list">
                    <h5>Assigned Containers:</h5>
                    ${containers.map(c => `
                        <div class="container-item" onclick="dashboard.highlightContainer('${c.id}')">
                            ${c.name || c.id} (${c.weight} kg)
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        detailsElement.style.display = 'block';
    }

    onContainerSelected(detail) {
        this.showContainerDetails(detail.containerId);
    }

    onContainerFocused(detail) {
        this.highlightContainer(detail.containerId);
    }

    onVehicleSelected(detail) {
        this.showVehicleDetails(detail.vehicleId);
    }

    resetView() {
        if (window.CargoOpt3D && window.CargoOpt3D.scene) {
            window.CargoOpt3D.scene.resetCamera();
        }
        
        // Clear selections
        document.getElementById('container-details').style.display = 'none';
        document.getElementById('vehicle-details').style.display = 'none';
    }

    toggle3DView() {
        const toggleBtn = document.getElementById('toggle-3d-view');
        const is3D = toggleBtn.classList.toggle('active');
        
        // Toggle between 2D and 3D views
        if (window.CargoOpt3D && window.CargoOpt3D.scene) {
            // Implementation depends on your 2D/3D toggle logic
            console.log('Toggle 3D view:', is3D);
        }
    }

    toggleLabels() {
        const toggleBtn = document.getElementById('toggle-labels');
        const showLabels = toggleBtn.classList.toggle('active');
        
        // Toggle container labels in visualization
        if (window.CargoOpt3D && window.CargoOpt3D.scene) {
            // Implementation for label toggling
            console.log('Toggle labels:', showLabels);
        }
    }

    toggleAnimation() {
        const toggleBtn = document.getElementById('toggle-animation');
        const animate = toggleBtn.classList.toggle('active');
        
        if (window.CargoOpt3D && window.CargoOpt3D.scene) {
            window.CargoOpt3D.scene.toggleAnimation();
        }
    }

    filterByVehicle(vehicleId) {
        if (!vehicleId) {
            // Show all
            this.resetFilters();
            return;
        }
        
        // Filter visualization to show only selected vehicle
        this.highlightVehicle(vehicleId);
    }

    filterByContainerType(type) {
        if (!type) {
            this.resetFilters();
            return;
        }
        
        // Filter containers by type in visualization
        console.log('Filter by container type:', type);
    }

    searchContainers(query) {
        if (!query) {
            this.resetFilters();
            return;
        }
        
        // Search and highlight matching containers
        const containers = this.currentOptimizationResult?.containers || [];
        const matchingContainers = containers.filter(c => 
            c.name?.toLowerCase().includes(query.toLowerCase()) || 
            c.id.toLowerCase().includes(query.toLowerCase())
        );
        
        matchingContainers.forEach(container => {
            this.highlightContainer(container.id);
        });
    }

    resetFilters() {
        // Reset all filters and show everything
        document.getElementById('filter-vehicle').value = '';
        document.getElementById('filter-container-type').value = '';
        document.getElementById('search-containers').value = '';
        
        // Reset visualization highlights
        if (window.CargoOpt3D && window.CargoOpt3D.scene) {
            // Implementation to reset highlights
        }
    }

    async exportResults() {
        if (!this.currentOptimizationResult) {
            this.showError('No optimization results to export');
            return;
        }

        try {
            const format = document.getElementById('export-format')?.value || 'json';
            const result = await this.visualizationService.exportResults(this.currentOptimizationResult, format);
            
            // Create download link
            const blob = new Blob([result.data], { type: result.contentType });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = result.filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            this.showSuccess('Results exported successfully');
        } catch (error) {
            this.showError('Export failed: ' + error.message);
        }
    }

    setLoadingState(loading) {
        this.isLoading = loading;
        const loader = document.getElementById('loading-indicator');
        const runBtn = document.getElementById('run-optimization');
        
        if (loader) loader.style.display = loading ? 'block' : 'none';
        if (runBtn) runBtn.disabled = loading;
    }

    showError(message) {
        // Show error message in UI
        console.error('Dashboard Error:', message);
        // You might use a toast notification system here
        alert('Error: ' + message);
    }

    showSuccess(message) {
        // Show success message in UI
        console.log('Dashboard Success:', message);
        // You might use a toast notification system here
        alert('Success: ' + message);
    }

    getContainerData() {
        // Get container data from form inputs or stored state
        // This would integrate with your container management UI
        return [];
    }

    getVehicleData() {
        // Get vehicle data from form inputs or stored state
        // This would integrate with your vehicle management UI
        return [];
    }

    getConstraintData() {
        // Get constraint data from UI
        return {
            maxDistance: parseFloat(document.getElementById('distance-input')?.value || 100),
            priority: document.getElementById('optimization-priority')?.value || 'emissions',
            constraints: {
                weightLimit: true,
                volumeLimit: true,
                hazardSegregation: document.getElementById('hazard-segregation')?.checked || false
            }
        };
    }

    loadSampleData() {
        // Load sample data for demonstration
        // This would be replaced with actual data loading
        console.log('Loading sample data...');
    }

    setupRealTimeUpdates() {
        // Setup real-time updates for metrics
        setInterval(() => {
            if (this.currentOptimizationResult) {
                this.updateRealTimeMetrics();
            }
        }, 5000);
    }

    updateRealTimeMetrics() {
        // Update real-time metrics if needed
        // This could include live data from backend
    }

    destroy() {
        // Cleanup event listeners and resources
        console.log('Dashboard destroyed');
    }
}

// Global instance for easy access
window.dashboard = new Dashboard();