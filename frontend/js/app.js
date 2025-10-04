import { Dashboard } from './components/dashboard.js';
import { visualizationService } from './services/visualization.js';

class CargoOptApp {
    constructor() {
        this.dashboard = null;
        this.isInitialized = false;
        this.currentView = 'dashboard';
        this.theme = 'light';
        this.language = 'en';
        this.userPreferences = {};
        
        // Application state
        this.state = {
            optimizationResults: [],
            currentScenario: null,
            isOnline: true,
            isLoading: false,
            errors: []
        };

        this.init();
    }

    async init() {
        try {
            console.log('🚀 Initializing CargoOpt Application...');
            
            // Show loading screen
            this.showLoadingScreen();
            
            // Check system requirements
            await this.checkSystemRequirements();
            
            // Initialize services
            await this.initializeServices();
            
            // Load user preferences
            await this.loadUserPreferences();
            
            // Setup UI components
            this.setupUI();
            
            // Initialize dashboard
            this.dashboard = new Dashboard();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Setup navigation
            this.setupNavigation();
            
            // Setup error handling
            this.setupErrorHandling();
            
            // Initialize Three.js if container exists
            this.initialize3DVisualization();
            
            // Load initial data
            await this.loadInitialData();
            
            this.isInitialized = true;
            
            // Hide loading screen
            this.hideLoadingScreen();
            
            console.log('✅ CargoOpt Application initialized successfully');
            this.showNotification('Application ready', 'success');
            
        } catch (error) {
            console.error('❌ Application initialization failed:', error);
            this.handleFatalError(error);
        }
    }

    async checkSystemRequirements() {
        const requirements = {
            webGL: this.checkWebGLSupport(),
            localStorage: this.checkLocalStorageSupport(),
            fetch: this.checkFetchSupport(),
            es6: this.checkES6Support()
        };

        const failedRequirements = Object.entries(requirements)
            .filter(([_, supported]) => !supported)
            .map(([feature]) => feature);

        if (failedRequirements.length > 0) {
            throw new Error(`System requirements not met: ${failedRequirements.join(', ')}`);
        }

        console.log('✅ System requirements check passed');
    }

    checkWebGLSupport() {
        try {
            const canvas = document.createElement('canvas');
            return !!(window.WebGLRenderingContext && 
                     (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
        } catch (e) {
            return false;
        }
    }

    checkLocalStorageSupport() {
        try {
            const test = 'test';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch (e) {
            return false;
        }
    }

    checkFetchSupport() {
        return 'fetch' in window;
    }

    checkES6Support() {
        try {
            new Function('class Foo {}');
            new Function('const foo = (x) => x');
            new Function('let [a] = [1]');
            return true;
        } catch (e) {
            return false;
        }
    }

    async initializeServices() {
        try {
            await visualizationService.initialize();
            console.log('✅ Services initialized');
        } catch (error) {
            console.warn('⚠️ Some services failed to initialize:', error);
            this.showNotification('Some features may be limited', 'warning');
        }
    }

    async loadUserPreferences() {
        try {
            const savedPreferences = localStorage.getItem('cargoopt_preferences');
            if (savedPreferences) {
                this.userPreferences = JSON.parse(savedPreferences);
                this.theme = this.userPreferences.theme || 'light';
                this.language = this.userPreferences.language || 'en';
                
                // Apply theme
                this.applyTheme(this.theme);
                
                // Apply language
                this.applyLanguage(this.language);
            }
            console.log('✅ User preferences loaded');
        } catch (error) {
            console.warn('⚠️ Failed to load user preferences:', error);
        }
    }

    saveUserPreferences() {
        try {
            this.userPreferences.theme = this.theme;
            this.userPreferences.language = this.language;
            localStorage.setItem('cargoopt_preferences', JSON.stringify(this.userPreferences));
        } catch (error) {
            console.warn('⚠️ Failed to save user preferences:', error);
        }
    }

    setupUI() {
        this.setupHeader();
        this.setupSidebar();
        this.setupMainContent();
        this.setupFooter();
        this.setupModals();
        
        console.log('✅ UI components setup completed');
    }

    setupHeader() {
        const header = document.getElementById('app-header') || this.createHeader();
        
        // Theme toggle
        const themeToggle = header.querySelector('#theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
        
        // Language selector
        const languageSelect = header.querySelector('#language-select');
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => this.changeLanguage(e.target.value));
        }
        
        // User menu
        const userMenu = header.querySelector('#user-menu');
        if (userMenu) {
            userMenu.addEventListener('click', () => this.toggleUserMenu());
        }
    }

    createHeader() {
        const header = document.createElement('header');
        header.id = 'app-header';
        header.className = 'app-header';
        header.innerHTML = `
            <div class="header-left">
                <div class="logo">
                    <h1>🚢 CargoOpt</h1>
                    <span class="version">v1.0.0</span>
                </div>
            </div>
            <div class="header-center">
                <nav class="main-nav">
                    <button class="nav-btn active" data-view="dashboard">Dashboard</button>
                    <button class="nav-btn" data-view="containers">Containers</button>
                    <button class="nav-btn" data-view="vehicles">Vehicles</button>
                    <button class="nav-btn" data-view="scenarios">Scenarios</button>
                    <button class="nav-btn" data-view="analytics">Analytics</button>
                </nav>
            </div>
            <div class="header-right">
                <button id="theme-toggle" class="icon-btn" title="Toggle theme">
                    ${this.theme === 'light' ? '🌙' : '☀️'}
                </button>
                <select id="language-select" class="language-select">
                    <option value="en" ${this.language === 'en' ? 'selected' : ''}>EN</option>
                    <option value="es" ${this.language === 'es' ? 'selected' : ''}>ES</option>
                    <option value="fr" ${this.language === 'fr' ? 'selected' : ''}>FR</option>
                </select>
                <div class="user-menu">
                    <button id="user-menu" class="user-btn">
                        <span class="user-avatar">👤</span>
                    </button>
                    <div class="user-dropdown">
                        <div class="user-info">
                            <strong>User</strong>
                            <span>user@cargoopt.com</span>
                        </div>
                        <div class="dropdown-actions">
                            <button onclick="app.showSettings()">Settings</button>
                            <button onclick="app.showHelp()">Help</button>
                            <button onclick="app.logout()">Logout</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.prepend(header);
        return header;
    }

    setupSidebar() {
        const sidebar = document.getElementById('app-sidebar') || this.createSidebar();
        
        // Setup sidebar toggle
        const sidebarToggle = document.getElementById('sidebar-toggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }
        
        // Setup quick actions
        const quickActions = sidebar.querySelectorAll('.quick-action');
        quickActions.forEach(action => {
            action.addEventListener('click', (e) => {
                const actionType = e.currentTarget.dataset.action;
                this.handleQuickAction(actionType);
            });
        });
    }

    createSidebar() {
        const sidebar = document.createElement('aside');
        sidebar.id = 'app-sidebar';
        sidebar.className = 'app-sidebar';
        sidebar.innerHTML = `
            <button id="sidebar-toggle" class="sidebar-toggle">☰</button>
            <div class="sidebar-content">
                <div class="sidebar-section">
                    <h3>Quick Actions</h3>
                    <div class="quick-actions">
                        <button class="quick-action" data-action="new-optimization">
                            <span class="icon">⚡</span>
                            <span>New Optimization</span>
                        </button>
                        <button class="quick-action" data-action="load-scenario">
                            <span class="icon">📁</span>
                            <span>Load Scenario</span>
                        </button>
                        <button class="quick-action" data-action="export-results">
                            <span class="icon">📊</span>
                            <span>Export Results</span>
                        </button>
                        <button class="quick-action" data-action="3d-view">
                            <span class="icon">🎮</span>
                            <span>3D View</span>
                        </button>
                    </div>
                </div>
                <div class="sidebar-section">
                    <h3>Recent Scenarios</h3>
                    <div id="recent-scenarios" class="recent-list">
                        <div class="empty-state">No recent scenarios</div>
                    </div>
                </div>
                <div class="sidebar-section">
                    <h3>System Status</h3>
                    <div class="status-indicators">
                        <div class="status-item ${this.state.isOnline ? 'online' : 'offline'}">
                            <span class="status-dot"></span>
                            <span>Backend</span>
                        </div>
                        <div class="status-item">
                            <span class="status-dot"></span>
                            <span>Database</span>
                        </div>
                        <div class="status-item">
                            <span class="status-dot"></span>
                            <span>3D Engine</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(sidebar);
        return sidebar;
    }

    setupMainContent() {
        const main = document.getElementById('app-main') || this.createMainContent();
        
        // Setup view containers
        this.setupViewContainers();
    }

    createMainContent() {
        const main = document.createElement('main');
        main.id = 'app-main';
        main.className = 'app-main';
        main.innerHTML = `
            <div id="view-container" class="view-container">
                <div id="dashboard-view" class="view active">
                    <!-- Dashboard content will be loaded by Dashboard component -->
                </div>
                <div id="containers-view" class="view">
                    <h2>Container Management</h2>
                    <div class="view-content">
                        <p>Container management interface coming soon...</p>
                    </div>
                </div>
                <div id="vehicles-view" class="view">
                    <h2>Vehicle Fleet</h2>
                    <div class="view-content">
                        <p>Vehicle fleet management interface coming soon...</p>
                    </div>
                </div>
                <div id="scenarios-view" class="view">
                    <h2>Scenarios</h2>
                    <div class="view-content">
                        <p>Scenario management interface coming soon...</p>
                    </div>
                </div>
                <div id="analytics-view" class="view">
                    <h2>Analytics</h2>
                    <div class="view-content">
                        <p>Analytics dashboard coming soon...</p>
                    </div>
                </div>
            </div>
            
            <!-- 3D Visualization Container -->
            <div id="visualization-container" class="visualization-container">
                <div class="visualization-header">
                    <h3>3D Visualization</h3>
                    <div class="visualization-controls">
                        <button id="toggle-3d-view" class="control-btn">3D/2D</button>
                        <button id="reset-camera" class="control-btn">Reset View</button>
                        <button id="toggle-labels" class="control-btn">Labels</button>
                        <button id="screenshot" class="control-btn">📸</button>
                    </div>
                </div>
                <div id="threejs-container" class="threejs-container"></div>
            </div>
        `;
        
        document.body.appendChild(main);
        return main;
    }

    setupViewContainers() {
        // This will be handled by the navigation system
    }

    setupFooter() {
        const footer = document.getElementById('app-footer') || this.createFooter();
    }

    createFooter() {
        const footer = document.createElement('footer');
        footer.id = 'app-footer';
        footer.className = 'app-footer';
        footer.innerHTML = `
            <div class="footer-content">
                <div class="footer-left">
                    <span>© 2024 CargoOpt. All rights reserved.</span>
                </div>
                <div class="footer-center">
                    <span id="connection-status" class="status-badge online">
                        ● Online
                    </span>
                </div>
                <div class="footer-right">
                    <button onclick="app.showAbout()">About</button>
                    <button onclick="app.showPrivacy()">Privacy</button>
                    <button onclick="app.showTerms()">Terms</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(footer);
        return footer;
    }

    setupModals() {
        this.createModal('settings-modal', 'Settings', `
            <div class="modal-content">
                <div class="settings-section">
                    <h4>Application Settings</h4>
                    <div class="setting-item">
                        <label>Theme:</label>
                        <select id="theme-select">
                            <option value="light">Light</option>
                            <option value="dark">Dark</option>
                            <option value="auto">Auto</option>
                        </select>
                    </div>
                    <div class="setting-item">
                        <label>Language:</label>
                        <select id="language-select-modal">
                            <option value="en">English</option>
                            <option value="es">Español</option>
                            <option value="fr">Français</option>
                        </select>
                    </div>
                </div>
                <div class="modal-actions">
                    <button onclick="app.saveSettings()" class="btn-primary">Save</button>
                    <button onclick="app.hideModal('settings-modal')" class="btn-secondary">Cancel</button>
                </div>
            </div>
        `);

        this.createModal('help-modal', 'Help & Documentation', `
            <div class="modal-content">
                <div class="help-section">
                    <h4>Getting Started</h4>
                    <p>Welcome to CargoOpt! Here's how to get started:</p>
                    <ol>
                        <li>Add containers in the Containers view</li>
                        <li>Configure vehicles in the Vehicles view</li>
                        <li>Run optimization from the Dashboard</li>
                        <li>View results in 3D visualization</li>
                    </ol>
                </div>
                <div class="modal-actions">
                    <button onclick="app.hideModal('help-modal')" class="btn-primary">Close</button>
                </div>
            </div>
        `);
    }

    createModal(id, title, content) {
        const modal = document.createElement('div');
        modal.id = id;
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-dialog">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close" onclick="app.hideModal('${id}')">×</button>
                </div>
                ${content}
            </div>
        `;
        document.body.appendChild(modal);
    }

    setupEventListeners() {
        // Navigation
        document.addEventListener('click', (e) => {
            if (e.target.matches('.nav-btn')) {
                const view = e.target.dataset.view;
                this.navigateTo(view);
            }
        });

        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });

        // Online/offline detection
        window.addEventListener('online', () => this.handleOnlineStatus(true));
        window.addEventListener('offline', () => this.handleOnlineStatus(false));

        // Resize handling
        window.addEventListener('resize', () => this.handleResize());

        // Service events
        document.addEventListener('optimizationComplete', (e) => {
            this.handleOptimizationComplete(e.detail.result);
        });

        document.addEventListener('serviceError', (e) => {
            this.handleServiceError(e.detail);
        });

        console.log('✅ Event listeners setup completed');
    }

    setupNavigation() {
        // Set initial active view
        this.navigateTo(this.currentView);
        console.log('✅ Navigation system initialized');
    }

    setupErrorHandling() {
        window.addEventListener('error', (e) => {
            this.handleGlobalError(e.error);
        });

        window.addEventListener('unhandledrejection', (e) => {
            this.handlePromiseRejection(e.reason);
        });

        console.log('✅ Error handling setup completed');
    }

    async initialize3DVisualization() {
        const container = document.getElementById('threejs-container');
        if (!container) {
            console.warn('3D visualization container not found');
            return;
        }

        try {
            // Dynamically import Three.js components
            const { CargoScene } = await import('./threejs/scene.js');
            
            // Initialize 3D scene
            window.CargoOpt3D = {
                scene: new CargoScene('threejs-container'),
                loadOptimizationResult: (result) => {
                    if (window.CargoOpt3D.scene) {
                        window.CargoOpt3D.scene.loadOptimizationResult(result);
                    }
                }
            };

            // Setup 3D controls
            this.setup3DControls();
            
            console.log('✅ 3D visualization initialized');
        } catch (error) {
            console.error('❌ Failed to initialize 3D visualization:', error);
            this.showNotification('3D visualization unavailable', 'error');
        }
    }

    setup3DControls() {
        const toggle3dBtn = document.getElementById('toggle-3d-view');
        const resetCameraBtn = document.getElementById('reset-camera');
        const toggleLabelsBtn = document.getElementById('toggle-labels');
        const screenshotBtn = document.getElementById('screenshot');

        if (toggle3dBtn) {
            toggle3dBtn.addEventListener('click', () => {
                if (window.CargoOpt3D && window.CargoOpt3D.scene) {
                    window.CargoOpt3D.scene.toggle3DView();
                }
            });
        }

        if (resetCameraBtn) {
            resetCameraBtn.addEventListener('click', () => {
                if (window.CargoOpt3D && window.CargoOpt3D.scene) {
                    window.CargoOpt3D.scene.resetCamera();
                }
            });
        }

        if (toggleLabelsBtn) {
            toggleLabelsBtn.addEventListener('click', () => {
                if (window.CargoOpt3D && window.CargoOpt3D.scene) {
                    window.CargoOpt3D.scene.toggleLabels();
                }
            });
        }

        if (screenshotBtn) {
            screenshotBtn.addEventListener('click', () => {
                if (window.CargoOpt3D && window.CargoOpt3D.scene) {
                    window.CargoOpt3D.scene.renderer.takeScreenshot();
                }
            });
        }
    }

    async loadInitialData() {
        try {
            this.setLoadingState(true);
            
            // Load reference data
            await this.loadReferenceData();
            
            // Load recent scenarios
            await this.loadRecentScenarios();
            
            // Check backend connectivity
            await this.checkBackendConnectivity();
            
            this.setLoadingState(false);
            
        } catch (error) {
            console.warn('⚠️ Failed to load some initial data:', error);
            this.setLoadingState(false);
        }
    }

    async loadReferenceData() {
        try {
            const [imdgCodes, stabilityRules] = await Promise.all([
                visualizationService.getReferenceData('imdg_codes'),
                visualizationService.getReferenceData('stability_rules')
            ]);
            
            console.log('✅ Reference data loaded');
            return { imdgCodes, stabilityRules };
        } catch (error) {
            console.warn('⚠️ Failed to load reference data:', error);
            return {};
        }
    }

    async loadRecentScenarios() {
        try {
            const scenarios = await visualizationService.getOptimizationHistory();
            this.updateRecentScenariosList(scenarios);
        } catch (error) {
            console.warn('⚠️ Failed to load recent scenarios:', error);
        }
    }

    updateRecentScenariosList(scenarios) {
        const container = document.getElementById('recent-scenarios');
        if (!container) return;

        if (!scenarios || scenarios.length === 0) {
            container.innerHTML = '<div class="empty-state">No recent scenarios</div>';
            return;
        }

        container.innerHTML = scenarios.slice(0, 5).map(scenario => `
            <div class="recent-item" onclick="app.loadScenario('${scenario.id}')">
                <div class="recent-name">${scenario.name}</div>
                <div class="recent-date">${new Date(scenario.date).toLocaleDateString()}</div>
            </div>
        `).join('');
    }

    async checkBackendConnectivity() {
        try {
            await visualizationService.healthCheck();
            this.state.isOnline = true;
            this.updateConnectionStatus(true);
        } catch (error) {
            this.state.isOnline = false;
            this.updateConnectionStatus(false);
            this.showNotification('Backend connection lost', 'warning');
        }
    }

    // Navigation methods
    navigateTo(view) {
        // Update navigation buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === view);
        });

        // Hide all views
        document.querySelectorAll('.view').forEach(viewEl => {
            viewEl.classList.remove('active');
        });

        // Show target view
        const targetView = document.getElementById(`${view}-view`);
        if (targetView) {
            targetView.classList.add('active');
            this.currentView = view;
            
            // Update browser history
            history.pushState({ view }, '', `#${view}`);
            
            console.log(`📍 Navigated to: ${view}`);
        }
    }

    // Theme methods
    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.theme);
        this.saveUserPreferences();
        
        // Update theme toggle button
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.textContent = this.theme === 'light' ? '🌙' : '☀️';
        }
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
    }

    // Language methods
    changeLanguage(lang) {
        this.language = lang;
        this.applyLanguage(lang);
        this.saveUserPreferences();
    }

    applyLanguage(lang) {
        document.documentElement.lang = lang;
        // Here you would typically load language files and update UI text
    }

    // Quick actions
    handleQuickAction(action) {
        switch (action) {
            case 'new-optimization':
                this.runNewOptimization();
                break;
            case 'load-scenario':
                this.showScenarioBrowser();
                break;
            case 'export-results':
                this.exportCurrentResults();
                break;
            case '3d-view':
                this.toggle3DView();
                break;
        }
    }

    async runNewOptimization() {
        if (this.dashboard) {
            await this.dashboard.runOptimization();
        }
    }

    showScenarioBrowser() {
        this.showNotification('Scenario browser coming soon', 'info');
    }

    async exportCurrentResults() {
        if (this.dashboard) {
            await this.dashboard.exportResults();
        }
    }

    toggle3DView() {
        const vizContainer = document.getElementById('visualization-container');
        if (vizContainer) {
            vizContainer.classList.toggle('collapsed');
        }
    }

    // Event handlers
    handleKeyboardShortcuts(e) {
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case '1':
                    e.preventDefault();
                    this.navigateTo('dashboard');
                    break;
                case '2':
                    e.preventDefault();
                    this.navigateTo('containers');
                    break;
                case '3':
                    e.preventDefault();
                    this.navigateTo('vehicles');
                    break;
                case 'r':
                    e.preventDefault();
                    this.runNewOptimization();
                    break;
                case 'e':
                    e.preventDefault();
                    this.exportCurrentResults();
                    break;
            }
        }
    }

    handleOnlineStatus(online) {
        this.state.isOnline = online;
        this.updateConnectionStatus(online);
        
        if (online) {
            this.showNotification('Connection restored', 'success');
            this.checkBackendConnectivity();
        } else {
            this.showNotification('You are offline', 'warning');
        }
    }

    handleResize() {
        // Handle responsive layout changes
        if (window.CargoOpt3D && window.CargoOpt3D.scene) {
            window.CargoOpt3D.scene.onWindowResize();
        }
    }

    handleOptimizationComplete(result) {
        this.state.optimizationResults.push({
            ...result,
            timestamp: new Date().toISOString()
        });
        
        this.showNotification('Optimization completed successfully', 'success');
    }

    handleServiceError(errorDetail) {
        this.state.errors.push({
            message: errorDetail.error,
            context: errorDetail.context,
            timestamp: new Date().toISOString()
        });
        
        this.showNotification(`Error: ${errorDetail.error}`, 'error');
    }

    // UI helper methods
    showLoadingScreen() {
        let loadingScreen = document.getElementById('loading-screen');
        if (!loadingScreen) {
            loadingScreen = document.createElement('div');
            loadingScreen.id = 'loading-screen';
            loadingScreen.className = 'loading-screen';
            loadingScreen.innerHTML = `
                <div class="loading-content">
                    <div class="loading-spinner"></div>
                    <h2>CargoOpt</h2>
                    <p>Loading application...</p>
                </div>
            `;
            document.body.appendChild(loadingScreen);
        }
        loadingScreen.style.display = 'flex';
    }

    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.style.display = 'none';
        }
    }

    setLoadingState(loading) {
        this.state.isLoading = loading;
        const appMain = document.getElementById('app-main');
        if (appMain) {
            appMain.classList.toggle('loading', loading);
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        // Add to notification container
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }

        container.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    updateConnectionStatus(online) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.className = `status-badge ${online ? 'online' : 'offline'}`;
            statusElement.textContent = online ? '● Online' : '● Offline';
        }
    }

    // Modal methods
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'block';
        }
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    }

    showSettings() {
        this.showModal('settings-modal');
    }

    showHelp() {
        this.showModal('help-modal');
    }

    saveSettings() {
        // Save settings logic here
        this.hideModal('settings-modal');
        this.showNotification('Settings saved', 'success');
    }

    // Error handling methods
    handleGlobalError(error) {
        console.error('Global error:', error);
        this.showNotification('An unexpected error occurred', 'error');
    }

    handlePromiseRejection(reason) {
        console.error('Unhandled promise rejection:', reason);
        this.showNotification('An operation failed', 'error');
    }

    handleFatalError(error) {
        const errorScreen = document.createElement('div');
        errorScreen.id = 'error-screen';
        errorScreen.className = 'error-screen';
        errorScreen.innerHTML = `
            <div class="error-content">
                <h2>😕 Application Error</h2>
                <p>Failed to initialize CargoOpt application.</p>
                <div class="error-details">
                    <code>${error.message}</code>
                </div>
                <div class="error-actions">
                    <button onclick="location.reload()" class="btn-primary">Reload Application</button>
                    <button onclick="app.showHelp()" class="btn-secondary">Get Help</button>
                </div>
            </div>
        `;
        
        document.body.innerHTML = '';
        document.body.appendChild(errorScreen);
    }

    // Utility methods
    async loadScenario(scenarioId) {
        try {
            const scenario = await visualizationService.loadOptimizationScenario(scenarioId);
            this.state.currentScenario = scenario;
            
            if (this.dashboard) {
                this.dashboard.loadOptimizationResult(scenario);
            }
            
            this.showNotification(`Scenario "${scenario.name}" loaded`, 'success');
        } catch (error) {
            this.showNotification(`Failed to load scenario: ${error.message}`, 'error');
        }
    }

    toggleSidebar() {
        const sidebar = document.getElementById('app-sidebar');
        if (sidebar) {
            sidebar.classList.toggle('collapsed');
        }
    }

    toggleUserMenu() {
        const dropdown = document.querySelector('.user-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('show');
        }
    }

    // Placeholder methods for future features
    showAbout() {
        this.showNotification('About CargoOpt v1.0.0', 'info');
    }

    showPrivacy() {
        this.showNotification('Privacy policy information', 'info');
    }

    showTerms() {
        this.showNotification('Terms of service information', 'info');
    }

    logout() {
        if (confirm('Are you sure you want to logout?')) {
            localStorage.removeItem('cargoopt_preferences');
            location.reload();
        }
    }

    // Cleanup method
    destroy() {
        // Cleanup Three.js
        if (window.CargoOpt3D && window.CargoOpt3D.scene) {
            window.CargoOpt3D.scene.dispose();
        }

        // Cleanup dashboard
        if (this.dashboard) {
            this.dashboard.destroy();
        }

        // Cleanup services
        visualizationService.destroy();

        console.log('🧹 CargoOpt application destroyed');
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new CargoOptApp();
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (window.app) {
        window.app.destroy();
    }
});

// Export for module usage
export default CargoOptApp;