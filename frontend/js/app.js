// CargoOpt Main Application
// This is the entry point for the CargoOpt container optimization system

console.log('CargoOpt Application Starting...');

// Initialize the application
class CargoOptApp {
    constructor() {
        this.container = null;
        this.items = [];
        this.optimizationResult = null;
        this.init();
    }

    init() {
        console.log('Initializing CargoOpt...');
        this.setupUI();
        this.attachEventListeners();
    }

    setupUI() {
        const app = document.getElementById('app');
        
        app.innerHTML = `
            <div class="container">
                <header class="header">
                    <div class="logo">
                        <i class="fas fa-boxes"></i>
                        <h1>CargoOpt</h1>
                    </div>
                    <p class="tagline">AI-Powered Container Optimization</p>
                </header>

                <main class="main-content">
                    <!-- Navigation Tabs -->
                    <div class="tabs">
                        <button class="tab-btn active" data-tab="input">
                            <i class="fas fa-edit"></i> Input Data
                        </button>
                        <button class="tab-btn" data-tab="optimize">
                            <i class="fas fa-cogs"></i> Optimize
                        </button>
                        <button class="tab-btn" data-tab="results">
                            <i class="fas fa-chart-bar"></i> Results
                        </button>
                        <button class="tab-btn" data-tab="history">
                            <i class="fas fa-history"></i> History
                        </button>
                    </div>

                    <!-- Tab Contents -->
                    <div class="tab-content active" id="input-tab">
                        <div class="section">
                            <h2><i class="fas fa-box"></i> Container Dimensions</h2>
                            <div class="form-grid">
                                <div class="form-group">
                                    <label>Length (m)</label>
                                    <input type="number" id="container-length" placeholder="12.0" step="0.1" min="0">
                                </div>
                                <div class="form-group">
                                    <label>Width (m)</label>
                                    <input type="number" id="container-width" placeholder="2.4" step="0.1" min="0">
                                </div>
                                <div class="form-group">
                                    <label>Height (m)</label>
                                    <input type="number" id="container-height" placeholder="2.6" step="0.1" min="0">
                                </div>
                            </div>
                        </div>

                        <div class="section">
                            <h2><i class="fas fa-cubes"></i> Add Items</h2>
                            <div class="form-grid">
                                <div class="form-group">
                                    <label>Item Name</label>
                                    <input type="text" id="item-name" placeholder="Box A">
                                </div>
                                <div class="form-group">
                                    <label>Length (m)</label>
                                    <input type="number" id="item-length" placeholder="1.2" step="0.1" min="0">
                                </div>
                                <div class="form-group">
                                    <label>Width (m)</label>
                                    <input type="number" id="item-width" placeholder="0.8" step="0.1" min="0">
                                </div>
                                <div class="form-group">
                                    <label>Height (m)</label>
                                    <input type="number" id="item-height" placeholder="1.0" step="0.1" min="0">
                                </div>
                                <div class="form-group">
                                    <label>Weight (kg)</label>
                                    <input type="number" id="item-weight" placeholder="100" step="1" min="0">
                                </div>
                                <div class="form-group">
                                    <label>Quantity</label>
                                    <input type="number" id="item-quantity" placeholder="1" step="1" min="1" value="1">
                                </div>
                            </div>

                            <div class="form-grid">
                                <div class="form-group">
                                    <label>Item Type</label>
                                    <select id="item-type">
                                        <option value="general">General</option>
                                        <option value="fragile">Fragile (Glass)</option>
                                        <option value="wood">Wood</option>
                                        <option value="metal">Metal</option>
                                        <option value="electronics">Electronics</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Storage Type</label>
                                    <select id="storage-type">
                                        <option value="normal">Normal</option>
                                        <option value="refrigerated">Refrigerated</option>
                                        <option value="frozen">Frozen</option>
                                        <option value="hazardous">Hazardous</option>
                                    </select>
                                </div>
                            </div>

                            <button class="btn btn-secondary" id="add-item-btn">
                                <i class="fas fa-plus"></i> Add Item
                            </button>
                        </div>

                        <div class="section">
                            <h2><i class="fas fa-list"></i> Items List</h2>
                            <div id="items-list" class="items-list">
                                <p class="empty-state">No items added yet. Add items above to get started.</p>
                            </div>
                        </div>

                        <button class="btn btn-primary btn-large" id="optimize-btn" disabled>
                            <i class="fas fa-magic"></i> Optimize Container
                        </button>
                    </div>

                    <div class="tab-content" id="optimize-tab">
                        <div class="optimization-status">
                            <i class="fas fa-spinner fa-spin"></i>
                            <h2>Optimization in Progress...</h2>
                            <p>Running genetic algorithm and constraint programming...</p>
                            <div class="progress-bar">
                                <div class="progress-fill" id="progress-fill"></div>
                            </div>
                        </div>
                    </div>

                    <div class="tab-content" id="results-tab">
                        <div class="results-container">
                            <p class="empty-state">Run optimization to see results here.</p>
                        </div>
                    </div>

                    <div class="tab-content" id="history-tab">
                        <div class="history-container">
                            <p class="empty-state">No optimization history yet.</p>
                        </div>
                    </div>
                </main>

                <footer class="footer">
                    <p>&copy; 2025 CargoOpt. AI-Powered Container Optimization System</p>
                </footer>
            </div>
        `;
    }

    attachEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // Add item button
        document.getElementById('add-item-btn').addEventListener('click', () => this.addItem());

        // Optimize button
        document.getElementById('optimize-btn').addEventListener('click', () => this.startOptimization());

        // Enable optimize button when items are added
        this.updateOptimizeButton();
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.tab === tabName) {
                btn.classList.add('active');
            }
        });

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }

    addItem() {
        const name = document.getElementById('item-name').value;
        const length = parseFloat(document.getElementById('item-length').value);
        const width = parseFloat(document.getElementById('item-width').value);
        const height = parseFloat(document.getElementById('item-height').value);
        const weight = parseFloat(document.getElementById('item-weight').value);
        const quantity = parseInt(document.getElementById('item-quantity').value);
        const type = document.getElementById('item-type').value;
        const storageType = document.getElementById('storage-type').value;

        // Validation
        if (!name || !length || !width || !height || !weight || !quantity) {
            alert('Please fill in all item fields');
            return;
        }

        const item = {
            id: Date.now(),
            name,
            length,
            width,
            height,
            weight,
            quantity,
            type,
            storageType
        };

        this.items.push(item);
        this.renderItems();
        this.clearItemForm();
        this.updateOptimizeButton();
    }

    renderItems() {
        const listContainer = document.getElementById('items-list');
        
        if (this.items.length === 0) {
            listContainer.innerHTML = '<p class="empty-state">No items added yet.</p>';
            return;
        }

        listContainer.innerHTML = this.items.map(item => `
            <div class="item-card">
                <div class="item-header">
                    <h3>${item.name}</h3>
                    <button class="btn-icon" onclick="app.removeItem(${item.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                <div class="item-details">
                    <span><i class="fas fa-ruler-combined"></i> ${item.length} × ${item.width} × ${item.height} m</span>
                    <span><i class="fas fa-weight"></i> ${item.weight} kg</span>
                    <span><i class="fas fa-hashtag"></i> Qty: ${item.quantity}</span>
                </div>
                <div class="item-tags">
                    <span class="tag">${item.type}</span>
                    <span class="tag">${item.storageType}</span>
                </div>
            </div>
        `).join('');
    }

    removeItem(id) {
        this.items = this.items.filter(item => item.id !== id);
        this.renderItems();
        this.updateOptimizeButton();
    }

    clearItemForm() {
        document.getElementById('item-name').value = '';
        document.getElementById('item-length').value = '';
        document.getElementById('item-width').value = '';
        document.getElementById('item-height').value = '';
        document.getElementById('item-weight').value = '';
        document.getElementById('item-quantity').value = '1';
    }

    updateOptimizeButton() {
        const btn = document.getElementById('optimize-btn');
        const hasContainer = document.getElementById('container-length').value &&
                           document.getElementById('container-width').value &&
                           document.getElementById('container-height').value;
        
        btn.disabled = !(hasContainer && this.items.length > 0);
    }

    async startOptimization() {
        // Get container dimensions
        this.container = {
            length: parseFloat(document.getElementById('container-length').value),
            width: parseFloat(document.getElementById('container-width').value),
            height: parseFloat(document.getElementById('container-height').value)
        };

        // Switch to optimize tab
        this.switchTab('optimize');

        // Simulate optimization progress
        const progressBar = document.getElementById('progress-fill');
        let progress = 0;
        const interval = setInterval(() => {
            progress += 10;
            progressBar.style.width = progress + '%';
            
            if (progress >= 100) {
                clearInterval(interval);
                setTimeout(() => {
                    this.showResults();
                }, 500);
            }
        }, 300);

        // In real implementation, this would call your backend API
        // const response = await fetch('/api/optimize', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify({ container: this.container, items: this.items })
        // });
    }

    showResults() {
        this.switchTab('results');
        const resultsContainer = document.querySelector('.results-container');
        
        resultsContainer.innerHTML = `
            <div class="results-success">
                <i class="fas fa-check-circle"></i>
                <h2>Optimization Complete!</h2>
                <p>Your container packing has been optimized successfully.</p>
            </div>

            <div class="results-stats">
                <div class="stat-card">
                    <i class="fas fa-box-open"></i>
                    <h3>Space Utilization</h3>
                    <p class="stat-value">78.5%</p>
                </div>
                <div class="stat-card">
                    <i class="fas fa-cubes"></i>
                    <h3>Items Packed</h3>
                    <p class="stat-value">${this.items.reduce((sum, item) => sum + item.quantity, 0)}</p>
                </div>
                <div class="stat-card">
                    <i class="fas fa-weight-hanging"></i>
                    <h3>Total Weight</h3>
                    <p class="stat-value">${this.items.reduce((sum, item) => sum + (item.weight * item.quantity), 0)} kg</p>
                </div>
            </div>

            <div class="section">
                <h2><i class="fas fa-cube"></i> 3D Visualization</h2>
                <div id="3d-viewer" class="viewer-container">
                    <p style="text-align: center; padding: 40px; color: #666;">
                        3D visualization will be rendered here using Three.js
                    </p>
                </div>
            </div>

            <div class="section">
                <h2><i class="fas fa-list-ol"></i> Item Placement Details</h2>
                <div class="placement-list">
                    ${this.items.map((item, index) => `
                        <div class="placement-item">
                            <strong>${item.name}</strong>
                            <span>Position: (${(Math.random() * 5).toFixed(2)}, ${(Math.random() * 2).toFixed(2)}, ${(Math.random() * 2).toFixed(2)})</span>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="action-buttons">
                <button class="btn btn-primary" onclick="app.downloadPDF()">
                    <i class="fas fa-file-pdf"></i> Download PDF Report
                </button>
                <button class="btn btn-secondary" onclick="app.downloadImage()">
                    <i class="fas fa-image"></i> Download 3D Image
                </button>
                <button class="btn btn-secondary" onclick="app.downloadJSON()">
                    <i class="fas fa-file-code"></i> Download JSON Data
                </button>
            </div>
        `;
    }

    downloadPDF() {
        alert('PDF download functionality will be implemented with backend integration');
    }

    downloadImage() {
        alert('3D image download functionality will be implemented with Three.js integration');
    }

    downloadJSON() {
        const data = {
            container: this.container,
            items: this.items,
            timestamp: new Date().toISOString()
        };
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cargoopt-${Date.now()}.json`;
        a.click();
    }
}

// Initialize the application
const app = new CargoOptApp();

// Make app globally accessible for inline onclick handlers
window.app = app;

console.log('CargoOpt Application Loaded Successfully!');