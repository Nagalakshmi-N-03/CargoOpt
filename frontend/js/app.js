/**
 * CargoOpt Main Application
 * Core application logic and initialization
 */

import { API } from './api.js';
import { ContainerForm } from './components/forms.js';
import { ResultsViewer } from './components/results.js';
import { Dashboard } from './components/dashboard.js';
import { NotificationManager } from './utils/notifications.js';

class CargoOptApp {
  constructor() {
    this.api = new API();
    this.notifications = new NotificationManager();
    
    // Component instances
    this.containerForm = null;
    this.resultsViewer = null;
    this.dashboard = null;
    
    // Application state
    this.state = {
      currentView: 'dashboard',
      optimizationId: null,
      optimizationResult: null,
      container: null,
      items: [],
      isProcessing: false,
    };
    
    // Event listeners
    this.listeners = new Map();
    
    console.log('CargoOpt Application initialized');
  }
  
  /**
   * Initialize the application
   */
  async init() {
    try {
      console.log('Initializing CargoOpt...');
      
      // Check API connection
      await this.checkAPIConnection();
      
      // Initialize components
      this.initializeComponents();
      
      // Set up event listeners
      this.setupEventListeners();
      
      // Load initial data
      await this.loadInitialData();
      
      // Set initial view
      this.navigateTo('dashboard');
      
      // Register service worker for PWA
      this.registerServiceWorker();
      
      console.log('CargoOpt initialized successfully');
      this.notifications.success('Application loaded successfully');
      
    } catch (error) {
      console.error('Initialization error:', error);
      this.notifications.error('Failed to initialize application');
      this.handleError(error);
    }
  }
  
  /**
   * Check API connection
   */
  async checkAPIConnection() {
    try {
      const health = await this.api.checkHealth();
      console.log('API Status:', health.status);
      
      if (health.status !== 'healthy') {
        throw new Error('API is not healthy');
      }
      
      return true;
    } catch (error) {
      console.error('API connection failed:', error);
      throw new Error('Cannot connect to backend API');
    }
  }
  
  /**
   * Initialize all components
   */
  initializeComponents() {
    // Initialize Container Form
    this.containerForm = new ContainerForm({
      containerId: 'container-form',
      onSubmit: this.handleOptimizationSubmit.bind(this),
      onCancel: () => this.navigateTo('dashboard'),
    });
    
    // Initialize Results Viewer
    this.resultsViewer = new ResultsViewer({
      containerId: 'results-viewer',
      onBack: () => this.navigateTo('dashboard'),
      onExport: this.handleExport.bind(this),
    });
    
    // Initialize Dashboard
    this.dashboard = new Dashboard({
      containerId: 'dashboard',
      onNewOptimization: () => this.navigateTo('form'),
      onViewResult: this.handleViewResult.bind(this),
      onDeleteResult: this.handleDeleteResult.bind(this),
    });
    
    console.log('Components initialized');
  }
  
  /**
   * Set up global event listeners
   */
  setupEventListeners() {
    // Navigation events
    document.addEventListener('click', (e) => {
      if (e.target.matches('[data-navigate]')) {
        e.preventDefault();
        const view = e.target.dataset.navigate;
        this.navigateTo(view);
      }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + N: New optimization
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        this.navigateTo('form');
      }
      
      // Escape: Go back to dashboard
      if (e.key === 'Escape' && this.state.currentView !== 'dashboard') {
        this.navigateTo('dashboard');
      }
    });
    
    // Window resize handler
    window.addEventListener('resize', this.handleResize.bind(this));
    
    // Online/offline detection
    window.addEventListener('online', () => {
      this.notifications.success('Connection restored');
      this.handleOnline();
    });
    
    window.addEventListener('offline', () => {
      this.notifications.warning('Connection lost. Working offline.');
      this.handleOffline();
    });
    
    // Before unload warning
    window.addEventListener('beforeunload', (e) => {
      if (this.state.isProcessing) {
        e.preventDefault();
        e.returnValue = 'Optimization in progress. Are you sure you want to leave?';
        return e.returnValue;
      }
    });
  }
  
  /**
   * Load initial data from API
   */
  async loadInitialData() {
    try {
      // Load configuration
      const config = await this.api.getConfig();
      this.state.config = config;
      
      // Load recent optimizations
      const history = await this.api.getOptimizationHistory({ limit: 10 });
      this.state.history = history;
      
      // Update dashboard
      if (this.dashboard) {
        this.dashboard.updateHistory(history);
      }
      
      console.log('Initial data loaded');
    } catch (error) {
      console.error('Failed to load initial data:', error);
      // Non-critical error, continue with defaults
    }
  }
  
  /**
   * Navigate to a view
   */
  navigateTo(view) {
    console.log(`Navigating to: ${view}`);
    
    // Hide all views
    document.querySelectorAll('.view').forEach(el => {
      el.classList.add('hidden');
    });
    
    // Show target view
    const targetView = document.getElementById(`${view}-view`);
    if (targetView) {
      targetView.classList.remove('hidden');
      targetView.classList.add('animate-fade-in');
    }
    
    // Update navigation state
    this.updateNavigation(view);
    
    // Update state
    this.state.currentView = view;
    
    // Trigger view-specific actions
    this.onViewChange(view);
  }
  
  /**
   * Update navigation UI
   */
  updateNavigation(activeView) {
    document.querySelectorAll('[data-navigate]').forEach(el => {
      if (el.dataset.navigate === activeView) {
        el.classList.add('active');
      } else {
        el.classList.remove('active');
      }
    });
  }
  
  /**
   * Handle view change
   */
  onViewChange(view) {
    switch (view) {
      case 'dashboard':
        this.dashboard?.refresh();
        break;
      case 'form':
        this.containerForm?.reset();
        break;
      case 'results':
        // Results are loaded when navigating
        break;
    }
  }
  
  /**
   * Handle optimization submission
   */
  async handleOptimizationSubmit(data) {
    try {
      this.state.isProcessing = true;
      this.notifications.info('Starting optimization...');
      
      console.log('Submitting optimization:', data);
      
      // Submit optimization request
      const result = await this.api.optimize({
        container: data.container,
        items: data.items,
        algorithm: data.algorithm || 'genetic',
        parameters: data.parameters,
      });
      
      this.state.optimizationId = result.optimization_id;
      
      // Poll for results if async
      if (result.status === 'pending' || result.status === 'running') {
        await this.pollOptimizationStatus(result.optimization_id);
      } else {
        this.handleOptimizationComplete(result);
      }
      
    } catch (error) {
      console.error('Optimization error:', error);
      this.notifications.error('Optimization failed: ' + error.message);
      this.handleError(error);
    } finally {
      this.state.isProcessing = false;
    }
  }
  
  /**
   * Poll optimization status
   */
  async pollOptimizationStatus(optimizationId) {
    const maxAttempts = 60; // 5 minutes with 5 second intervals
    let attempts = 0;
    
    const poll = async () => {
      try {
        attempts++;
        
        const status = await this.api.getOptimizationStatus(optimizationId);
        console.log('Optimization status:', status.status);
        
        if (status.status === 'completed') {
          const result = await this.api.getOptimizationResult(optimizationId);
          this.handleOptimizationComplete(result);
          return;
        }
        
        if (status.status === 'failed') {
          throw new Error(status.error || 'Optimization failed');
        }
        
        if (status.status === 'cancelled') {
          this.notifications.warning('Optimization was cancelled');
          return;
        }
        
        if (attempts >= maxAttempts) {
          throw new Error('Optimization timeout');
        }
        
        // Update progress if available
        if (status.progress !== undefined) {
          this.updateProgress(status.progress);
        }
        
        // Continue polling
        setTimeout(poll, 5000);
        
      } catch (error) {
        console.error('Polling error:', error);
        this.notifications.error('Failed to get optimization status');
        this.state.isProcessing = false;
      }
    };
    
    poll();
  }
  
  /**
   * Handle optimization completion
   */
  handleOptimizationComplete(result) {
    console.log('Optimization completed:', result);
    
    this.state.optimizationResult = result;
    this.state.isProcessing = false;
    
    // Show results
    this.resultsViewer.displayResults(result);
    this.navigateTo('results');
    
    // Show success notification
    this.notifications.success(
      `Optimization complete! Utilization: ${result.utilization.toFixed(1)}%`
    );
    
    // Refresh dashboard history
    this.loadInitialData();
  }
  
  /**
   * Update progress indicator
   */
  updateProgress(progress) {
    const progressBar = document.getElementById('optimization-progress');
    if (progressBar) {
      progressBar.style.width = `${progress}%`;
      progressBar.textContent = `${Math.round(progress)}%`;
    }
  }
  
  /**
   * Handle viewing a result from history
   */
  async handleViewResult(optimizationId) {
    try {
      this.notifications.info('Loading optimization result...');
      
      const result = await this.api.getOptimizationResult(optimizationId);
      
      this.state.optimizationResult = result;
      this.resultsViewer.displayResults(result);
      this.navigateTo('results');
      
    } catch (error) {
      console.error('Failed to load result:', error);
      this.notifications.error('Failed to load optimization result');
    }
  }
  
  /**
   * Handle deleting a result
   */
  async handleDeleteResult(optimizationId) {
    if (!confirm('Are you sure you want to delete this optimization?')) {
      return;
    }
    
    try {
      await this.api.deleteOptimization(optimizationId);
      this.notifications.success('Optimization deleted');
      
      // Refresh history
      await this.loadInitialData();
      
    } catch (error) {
      console.error('Failed to delete:', error);
      this.notifications.error('Failed to delete optimization');
    }
  }
  
  /**
   * Handle export request
   */
  async handleExport(format, optimizationId) {
    try {
      this.notifications.info(`Exporting as ${format.toUpperCase()}...`);
      
      const blob = await this.api.exportResult(optimizationId, format);
      
      // Download file
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `optimization_${optimizationId}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      this.notifications.success('Export complete');
      
    } catch (error) {
      console.error('Export error:', error);
      this.notifications.error('Export failed');
    }
  }
  
  /**
   * Handle window resize
   */
  handleResize() {
    // Update 3D viewer if visible
    if (this.state.currentView === 'results' && this.resultsViewer) {
      this.resultsViewer.handleResize();
    }
  }
  
  /**
   * Handle online event
   */
  handleOnline() {
    // Retry any failed requests
    this.api.retryFailedRequests();
  }
  
  /**
   * Handle offline event
   */
  handleOffline() {
    // Switch to offline mode
    this.state.isOffline = true;
  }
  
  /**
   * Handle errors
   */
  handleError(error) {
    console.error('Application error:', error);
    
    // Log to error tracking service (e.g., Sentry)
    if (window.Sentry) {
      window.Sentry.captureException(error);
    }
    
    // Show user-friendly error message
    const message = this.getErrorMessage(error);
    this.notifications.error(message);
  }
  
  /**
   * Get user-friendly error message
   */
  getErrorMessage(error) {
    if (error.response) {
      return error.response.data.message || 'Server error occurred';
    }
    
    if (error.request) {
      return 'Cannot connect to server. Please check your connection.';
    }
    
    return error.message || 'An unexpected error occurred';
  }
  
  /**
   * Register service worker for PWA
   */
  registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/service-worker.js')
        .then(registration => {
          console.log('Service Worker registered:', registration);
        })
        .catch(error => {
          console.log('Service Worker registration failed:', error);
        });
    }
  }
  
  /**
   * Get current state
   */
  getState() {
    return { ...this.state };
  }
  
  /**
   * Update state
   */
  setState(updates) {
    this.state = { ...this.state, ...updates };
    this.emit('stateChange', this.state);
  }
  
  /**
   * Event emitter
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }
  
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => callback(data));
    }
  }
  
  /**
   * Cleanup
   */
  destroy() {
    // Remove event listeners
    this.listeners.clear();
    
    // Destroy components
    this.containerForm?.destroy();
    this.resultsViewer?.destroy();
    this.dashboard?.destroy();
    
    console.log('CargoOpt application destroyed');
  }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.cargoApp = new CargoOptApp();
  window.cargoApp.init();
});

// Export for use in other modules
export default CargoOptApp;