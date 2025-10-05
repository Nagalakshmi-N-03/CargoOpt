// Main Application
class CargoOptApp {
    constructor() {
        this.containers = [];
        this.items = [];
        this.optimizationResult = null;
        this.currentTab = 'optimization';
        
        this.init();
    }

    init() {
        console.log('🚀 Initializing CargoOpt Application...');
        
        // Initialize components
        this.forms = new FormsManager(this);
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Check API status
        this.checkApiStatus();
        
        // Initialize tab system
        this.initializeTabs();
        
        // Load standard containers
        this.loadStandardContainers();
        
        console.log('✅ Application initialized');
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Algorithm selector
        const algorithmSelect = document.getElementById('algorithm-select');
        if (algorithmSelect) {
            algorithmSelect.addEventListener('change', (e) => {
                this.handleAlgorithmChange(e.target.value);
            });
        }

        // Optimization buttons
        const validateBtn = document.getElementById('validate-btn');
        if (validateBtn) {
            validateBtn.addEventListener('click', () => this.validateData());
        }

        const optimizeBtn = document.getElementById('optimize-btn');
        if (optimizeBtn) {
            optimizeBtn.addEventListener('click', () => this.runOptimization());
        }

        const compareBtn = document.getElementById('compare-btn');
        if (compareBtn) {
            compareBtn.addEventListener('click', () => this.compareAlgorithms());
        }

        // Container management
        const addContainerBtn = document.getElementById('add-container-btn');
        if (addContainerBtn) {
            addContainerBtn.addEventListener('click', () => this.forms.showContainerModal());
        }

        const saveContainerBtn = document.getElementById('save-container');
        if (saveContainerBtn) {
            saveContainerBtn.addEventListener('click', () => this.forms.saveContainer());
        }

        // Item management
        const addItemBtn = document.getElementById('add-item-btn');
        if (addItemBtn) {
            addItemBtn.addEventListener('click', () => this.forms.showItemModal());
        }

        const saveItemBtn = document.getElementById('save-item');
        if (saveItemBtn) {
            saveItemBtn.addEventListener('click', () => this.forms.saveItem());
        }

        const loadSampleItemsBtn = document.getElementById('load-sample-items');
        if (loadSampleItemsBtn) {
            loadSampleItemsBtn.addEventListener('click', () => this.forms.generateSampleData());
        }

        // Quick actions
        const loadSampleDataBtn = document.getElementById('load-sample-data');
        if (loadSampleDataBtn) {
            loadSampleDataBtn.addEventListener('click', () => this.forms.generateSampleData());
        }

        const exportResultsBtn = document.getElementById('export-results');
        if (exportResultsBtn) {
            exportResultsBtn.addEventListener('click', () => this.exportResults());
        }

        const clearDataBtn = document.getElementById('clear-data');
        if (clearDataBtn) {
            clearDataBtn.addEventListener('click', () => this.clearAllData());
        }

        // History
        const refreshHistoryBtn = document.getElementById('refresh-history');
        if (refreshHistoryBtn) {
            refreshHistoryBtn.addEventListener('click', () => this.loadHistory());
        }

        // Modal close buttons
        document.querySelectorAll('.modal-close, .modal-cancel').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.target.closest('.modal').classList.remove('active');
            });
        });

        // Close modals on backdrop click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.remove('active');
                }
            });
        });
    }

    initializeTabs() {
        this.switchTab('optimization');
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === tabName);
        });

        this.currentTab = tabName;

        // Load data for specific tabs
        if (tabName === 'history') {
            this.loadHistory();
        }
    }

    handleAlgorithmChange(algorithm) {
        const geneticParams = document.getElementById('genetic-params');
        if (geneticParams) {
            geneticParams.style.display = algorithm === 'genetic' ? 'block' : 'none';
        }
    }

    async checkApiStatus() {
        try {
            const response = await apiService.getHealth();
            
            const apiStatus = document.getElementById('api-status');
            const dbStatus = document.getElementById('db-status');
            
            if (response.success) {
                if (apiStatus) apiStatus.textContent = '✅ Online';
                if (dbStatus) dbStatus.textContent = '✅ Connected';
                this.updateLastUpdate();
            } else {
                if (apiStatus) apiStatus.textContent = '❌ Offline';
                if (dbStatus) dbStatus.textContent = '❌ Disconnected';
            }
        } catch (error) {
            console.error('Failed to check API status:', error);
            const apiStatus = document.getElementById('api-status');
            if (apiStatus) apiStatus.textContent = '❌ Offline';
        }
    }

    updateLastUpdate() {
        const lastUpdate = document.getElementById('last-update');
        if (lastUpdate) {
            lastUpdate.textContent = new Date().toLocaleTimeString();
        }
    }

    async validateData() {
        if (this.containers.length === 0) {
            this.showNotification('Please add at least one container', 'error');
            return;
        }

        if (this.items.length === 0) {
            this.showNotification('Please add at least one item', 'error');
            return;
        }

        this.showLoading(true);

        try {
            const response = await apiService.validateData(this.containers[0], this.items);
            
            if (response.success) {
                this.showNotification('✅ Data validation passed!', 'success');
            } else {
                this.showNotification(`❌ Validation failed: ${response.error}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Validation error: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async runOptimization() {
        if (this.containers.length === 0) {
            this.showNotification('Please add at least one container', 'error');
            return;
        }

        if (this.items.length === 0) {
            this.showNotification('Please add at least one item', 'error');
            return;
        }

        const algorithm = document.getElementById('algorithm-select').value;
        const strategy = document.getElementById('strategy-select').value;

        this.showLoading(true);

        try {
            const requestData = {
                container: this.containers[0],
                items: this.items,
                strategy: strategy
            };

            // Add genetic algorithm parameters if selected
            if (algorithm === 'genetic') {
                requestData.generations = parseInt(document.getElementById('generations').value);
                requestData.population_size = parseInt(document.getElementById('population-size').value);
                requestData.mutation_rate = parseFloat(document.getElementById('mutation-rate').value);
            }

            let response;
            switch (algorithm) {
                case 'packing':
                    response = await apiService.optimizePacking(requestData);
                    break;
                case 'genetic':
                    response = await apiService.optimizeGenetic(requestData);
                    break;
                case 'stowage':
                    response = await apiService.optimizeStowage(requestData);
                    break;
                default:
                    response = await apiService.optimizeAuto(requestData);
            }

            if (response.success) {
                this.optimizationResult = response.data;
                this.displayResults(response.data);
                this.showNotification('✅ Optimization completed successfully!', 'success');
                
                // Switch to results tab
                this.switchTab('results');
            } else {
                this.showNotification(`❌ Optimization failed: ${response.error}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Optimization error: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async compareAlgorithms() {
        if (this.containers.length === 0 || this.items.length === 0) {
            this.showNotification('Please add containers and items first', 'error');
            return;
        }

        this.showLoading(true);

        try {
            const requestData = {
                container: this.containers[0],
                items: this.items
            };

            const response = await apiService.compareAlgorithms(requestData);

            if (response.success) {
                this.displayComparisonResults(response.data);
                this.showNotification('Algorithm comparison completed', 'success');
            } else {
                this.showNotification(`Comparison failed: ${response.error}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Comparison error: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    displayResults(result) {
        // Update metrics
        document.getElementById('metric-utilization').textContent = 
            `${(result.utilization_rate * 100).toFixed(1)}%`;
        document.getElementById('metric-items').textContent = result.total_items_packed;
        document.getElementById('metric-weight').textContent = 
            `${((result.total_weight_used / this.containers[0].max_weight) * 100).toFixed(1)}%`;
        document.getElementById('metric-efficiency').textContent = 
            `${(result.utilization_rate * 100).toFixed(0)}%`;

        // Display placements table
        this.displayPlacementsTable(result.placements);

        // Show visualization placeholder
        const vizContainer = document.getElementById('visualization-container');
        if (vizContainer) {
            vizContainer.innerHTML = `
                <div class="visualization-active">
                    <p>✅ ${result.total_items_packed} items packed</p>
                    <p>📦 Space utilization: ${(result.utilization_rate * 100).toFixed(1)}%</p>
                    <p>⚖️ Weight utilization: ${((result.total_weight_used / this.containers[0].max_weight) * 100).toFixed(1)}%</p>
                    <small>3D visualization integration coming soon</small>
                </div>
            `;
        }
    }

    displayPlacementsTable(placements) {
        const tbody = document.getElementById('placements-table-body');
        if (!tbody) return;

        tbody.innerHTML = placements.map(p => `
            <tr>
                <td>${p.item_id}</td>
                <td>(${p.position[0].toFixed(1)}, ${p.position[1].toFixed(1)}, ${p.position[2].toFixed(1)})</td>
                <td>${p.dimensions[0]} × ${p.dimensions[1]} × ${p.dimensions[2]} cm</td>
                <td>${p.rotated ? 'Yes' : 'No'}</td>
                <td>${p.volume.toFixed(2)} cm³</td>
            </tr>
        `).join('');
    }

    displayComparisonResults(results) {
        // Display comparison in a modal or alert
        const summary = results.algorithms.map(algo => 
            `${algo.algorithm}: ${(algo.utilization_rate * 100).toFixed(1)}% utilization`
        ).join('\n');

        alert(`Algorithm Comparison Results:\n\n${summary}\n\nBest: ${results.best_algorithm}`);
    }

    async loadHistory() {
        const limit = document.getElementById('history-limit')?.value || 10;
        const algorithm = document.getElementById('history-algorithm')?.value || null;

        try {
            const response = await apiService.getOptimizationHistory(limit, algorithm);

            if (response.success) {
                this.displayHistory(response.data.history);
            }
        } catch (error) {
            console.error('Failed to load history:', error);
        }
    }

    displayHistory(history) {
        const tbody = document.getElementById('history-table-body');
        if (!tbody) return;

        if (!history || history.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6">No history available</td></tr>';
            return;
        }

        tbody.innerHTML = history.map(item => `
            <tr>
                <td>${new Date(item.created_at).toLocaleString()}</td>
                <td>${item.algorithm}</td>
                <td>${(item.utilization_rate * 100).toFixed(1)}%</td>
                <td>${item.total_items_packed}</td>
                <td>${item.execution_time ? item.execution_time.toFixed(2) + 's' : 'N/A'}</td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="app.loadHistoryItem(${item.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    loadStandardContainers() {
        const standardContainers = [
            { name: "20ft Standard", length: 589, width: 235, height: 239, max_weight: 28200, type: "standard_20ft" },
            { name: "40ft Standard", length: 1203, width: 235, height: 239, max_weight: 26700, type: "standard_40ft" },
            { name: "40ft High Cube", length: 1203, width: 235, height: 269, max_weight: 26700, type: "high_cube_40ft" },
            { name: "20ft Reefer", length: 542, width: 228, height: 216, max_weight: 27400, type: "reefer_20ft" }
        ];

        const container = document.getElementById('standard-containers');
        if (!container) return;

        container.innerHTML = standardContainers.map(c => `
            <div class="standard-container-card" onclick="app.forms.showContainerModal(${JSON.stringify(c).replace(/"/g, '&quot;')})">
                <h4>${c.name}</h4>
                <p>${c.length}×${c.width}×${c.height} cm</p>
                <p>Max: ${c.max_weight} kg</p>
            </div>
        `).join('');
    }

    renderContainers() {
        const grid = document.getElementById('containers-grid');
        if (!grid) return;

        if (this.containers.length === 0) {
            grid.innerHTML = '<div class="empty-state">No containers added yet</div>';
            return;
        }

        grid.innerHTML = this.containers.map((c, i) => `
            <div class="container-card">
                <h4>${c.name}</h4>
                <p>📏 ${c.length}×${c.width}×${c.height} cm</p>
                <p>⚖️ Max: ${c.max_weight} kg</p>
                <div class="card-actions">
                    <button class="btn btn-sm btn-outline" onclick="app.forms.editContainer(${i})">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="app.deleteContainer(${i})">Delete</button>
                </div>
            </div>
        `).join('');
    }

    renderItems() {
        const tbody = document.getElementById('items-table-body');
        if (!tbody) return;

        if (this.items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7">No items added yet</td></tr>';
            return;
        }

        tbody.innerHTML = this.items.map((item, i) => `
            <tr>
                <td>${item.id}</td>
                <td>${item.name}</td>
                <td>${item.length}×${item.width}×${item.height}</td>
                <td>${item.weight}</td>
                <td>${item.quantity}</td>
                <td>
                    ${item.fragile ? '⚠️' : ''}
                    ${item.stackable ? '📚' : ''}
                    ${item.rotation_allowed ? '🔄' : ''}
                </td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="app.forms.editItem(${i})">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="app.deleteItem(${i})">Delete</button>
                </td>
            </tr>
        `).join('');

        this.updateItemsSummary();
    }

    updateItemsSummary() {
        const totalItems = this.items.reduce((sum, item) => sum + item.quantity, 0);
        const totalVolume = this.items.reduce((sum, item) => 
            sum + (item.length * item.width * item.height * item.quantity / 1000000), 0);
        const totalWeight = this.items.reduce((sum, item) => 
            sum + (item.weight * item.quantity), 0);

        document.getElementById('total-items').textContent = totalItems;
        document.getElementById('total-volume').textContent = totalVolume.toFixed(2) + ' m³';
        document.getElementById('total-weight').textContent = totalWeight.toFixed(0) + ' kg';
    }

    updatePreviewStats() {
        document.getElementById('preview-containers').textContent = this.containers.length;
        document.getElementById('preview-items').textContent = 
            this.items.reduce((sum, item) => sum + item.quantity, 0);
        
        const totalVolume = this.items.reduce((sum, item) => 
            sum + (item.length * item.width * item.height * item.quantity / 1000000), 0);
        document.getElementById('preview-volume').textContent = totalVolume.toFixed(2) + ' m³';
    }

    deleteContainer(index) {
        if (confirm('Are you sure you want to delete this container?')) {
            this.containers.splice(index, 1);
            this.renderContainers();
            this.updatePreviewStats();
            this.showNotification('Container deleted', 'success');
        }
    }

    deleteItem(index) {
        if (confirm('Are you sure you want to delete this item?')) {
            this.items.splice(index, 1);
            this.renderItems();
            this.updatePreviewStats();
            this.showNotification('Item deleted', 'success');
        }
    }

    clearAllData() {
        if (confirm('Are you sure you want to clear all data?')) {
            this.containers = [];
            this.items = [];
            this.optimizationResult = null;
            
            this.renderContainers();
            this.renderItems();
            this.updatePreviewStats();
            
            this.showNotification('All data cleared', 'success');
        }
    }

    async exportResults() {
        if (!this.optimizationResult) {
            this.showNotification('No results to export', 'error');
            return;
        }

        try {
            const response = await apiService.exportResult(this.optimizationResult, 'excel');
            
            if (response.success) {
                this.showNotification('Export successful!', 'success');
                // Trigger download
                window.open(response.data.download_url, '_blank');
            }
        } catch (error) {
            this.showNotification(`Export failed: ${error.message}`, 'error');
        }
    }

    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notifications');
        if (!container) {
            console.log(`[${type}] ${message}`);
            return;
        }

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">×</button>
        `;

        container.appendChild(notification);

        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
}

// Initialize app when DOM is ready
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new CargoOptApp();
    window.app = app; // Make available globally for onclick handlers
});