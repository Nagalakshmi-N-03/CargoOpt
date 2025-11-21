/**
 * CargoOpt Dashboard Component
 * Main dashboard with history and statistics
 */

export class Dashboard {
  constructor(options = {}) {
    this.containerId = options.containerId || 'dashboard';
    this.onNewOptimization = options.onNewOptimization || (() => {});
    this.onViewResult = options.onViewResult || (() => {});
    this.onDeleteResult = options.onDeleteResult || (() => {});
    
    this.container = document.getElementById(this.containerId);
    this.history = [];
    this.stats = null;
    
    this.init();
  }
  
  init() {
    this.render();
    this.attachEventListeners();
  }
  
  render() {
    this.container.innerHTML = `
      <div class="dashboard-container">
        <div class="dashboard-header">
          <div class="dashboard-title">
            <h1><i class="fas fa-cubes"></i> CargoOpt Dashboard</h1>
            <p class="text-muted">AI-Powered Container Optimization System</p>
          </div>
          <button class="btn btn-primary btn-lg" id="new-optimization-btn">
            <i class="fas fa-plus"></i> New Optimization
          </button>
        </div>
        
        <div class="dashboard-stats">
          ${this.renderStatsCards()}
        </div>
        
        <div class="dashboard-content">
          <div class="dashboard-section">
            <div class="section-header">
              <h2>Recent Optimizations</h2>
              <div class="section-actions">
                <button class="btn btn-secondary btn-sm" id="refresh-btn">
                  <i class="fas fa-sync"></i> Refresh
                </button>
                <select id="filter-status" class="form-input-sm">
                  <option value="all">All Status</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                  <option value="running">Running</option>
                </select>
              </div>
            </div>
            
            <div class="history-list" id="history-list">
              ${this.renderHistoryList()}
            </div>
          </div>
          
          <div class="dashboard-sidebar">
            <div class="sidebar-section">
              <h3>Quick Stats</h3>
              <div id="quick-stats">
                ${this.renderQuickStats()}
              </div>
            </div>
            
            <div class="sidebar-section">
              <h3>Performance Chart</h3>
              <div id="performance-chart">
                ${this.renderPerformanceChart()}
              </div>
            </div>
            
            <div class="sidebar-section">
              <h3>Getting Started</h3>
              <ul class="help-list">
                <li>
                  <i class="fas fa-box"></i>
                  Define container dimensions
                </li>
                <li>
                  <i class="fas fa-cubes"></i>
                  Add items to pack
                </li>
                <li>
                  <i class="fas fa-magic"></i>
                  Run optimization
                </li>
                <li>
                  <i class="fas fa-chart-bar"></i>
                  View results in 3D
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    `;
  }
  
  renderStatsCards() {
    return `
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-calculator"></i>
        </div>
        <div class="stat-content">
          <h3 id="total-optimizations">--</h3>
          <p>Total Optimizations</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-percentage"></i>
        </div>
        <div class="stat-content">
          <h3 id="avg-utilization">--</h3>
          <p>Average Utilization</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-clock"></i>
        </div>
        <div class="stat-content">
          <h3 id="avg-time">--</h3>
          <p>Average Time</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="stat-content">
          <h3 id="success-rate">--</h3>
          <p>Success Rate</p>
        </div>
      </div>
    `;
  }
  
  renderHistoryList() {
    if (this.history.length === 0) {
      return `
        <div class="empty-state">
          <i class="fas fa-inbox fa-3x"></i>
          <h3>No optimizations yet</h3>
          <p>Click "New Optimization" to get started</p>
        </div>
      `;
    }
    
    return `
      <div class="history-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Date</th>
              <th>Container</th>
              <th>Items</th>
              <th>Utilization</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            ${this.history.map(item => this.renderHistoryItem(item)).join('')}
          </tbody>
        </table>
      </div>
    `;
  }
  
  renderHistoryItem(item) {
    const statusClass = {
      completed: 'status-success',
      failed: 'status-error',
      running: 'status-warning',
      pending: 'status-info'
    }[item.status] || '';
    
    const statusIcon = {
      completed: 'fa-check-circle',
      failed: 'fa-times-circle',
      running: 'fa-spinner fa-spin',
      pending: 'fa-clock'
    }[item.status] || 'fa-question-circle';
    
    return `
      <tr data-id="${item.optimization_id}">
        <td>
          <code class="text-sm">${item.optimization_id.substring(0, 8)}...</code>
        </td>
        <td>${this.formatDate(item.started_at)}</td>
        <td>${item.container_size || 'N/A'}</td>
        <td>${item.items_packed || 0} / ${item.total_items || 0}</td>
        <td>
          <div class="utilization-bar">
            <div class="utilization-fill" style="width: ${item.utilization || 0}%"></div>
            <span class="utilization-text">${(item.utilization || 0).toFixed(1)}%</span>
          </div>
        </td>
        <td>
          <span class="status-badge ${statusClass}">
            <i class="fas ${statusIcon}"></i>
            ${item.status}
          </span>
        </td>
        <td>
          <div class="action-buttons">
            ${item.status === 'completed' ? `
              <button class="btn-icon" data-action="view" data-id="${item.optimization_id}" title="View Results">
                <i class="fas fa-eye"></i>
              </button>
            ` : ''}
            <button class="btn-icon" data-action="delete" data-id="${item.optimization_id}" title="Delete">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }
  
  renderQuickStats() {
    return `
      <div class="quick-stat">
        <span class="quick-stat-label">Today's Optimizations</span>
        <span class="quick-stat-value" id="today-count">--</span>
      </div>
      <div class="quick-stat">
        <span class="quick-stat-label">This Week</span>
        <span class="quick-stat-value" id="week-count">--</span>
      </div>
      <div class="quick-stat">
        <span class="quick-stat-label">Best Utilization</span>
        <span class="quick-stat-value" id="best-util">--</span>
      </div>
      <div class="quick-stat">
        <span class="quick-stat-label">Active Jobs</span>
        <span class="quick-stat-value" id="active-jobs">--</span>
      </div>
    `;
  }
  
  renderPerformanceChart() {
    return `
      <canvas id="performance-canvas" width="300" height="200"></canvas>
    `;
  }
  
  attachEventListeners() {
    // New optimization button
    document.getElementById('new-optimization-btn')?.addEventListener('click', 
      () => this.onNewOptimization());
    
    // Refresh button
    document.getElementById('refresh-btn')?.addEventListener('click', 
      () => this.refresh());
    
    // Filter
    document.getElementById('filter-status')?.addEventListener('change', 
      (e) => this.filterHistory(e.target.value));
    
    // Action buttons
    this.container.addEventListener('click', (e) => {
      const action = e.target.closest('[data-action]');
      if (!action) return;
      
      const actionType = action.dataset.action;
      const id = action.dataset.id;
      
      if (actionType === 'view') {
        this.onViewResult(id);
      } else if (actionType === 'delete') {
        this.onDeleteResult(id);
      }
    });
  }
  
  updateHistory(history) {
    this.history = history || [];
    this.updateHistoryList();
    this.updateStats();
    this.updateChart();
  }
  
  updateHistoryList() {
    const listElement = document.getElementById('history-list');
    if (listElement) {
      listElement.innerHTML = this.renderHistoryList();
    }
  }
  
  updateStats() {
    if (this.history.length === 0) return;
    
    // Total optimizations
    const totalEl = document.getElementById('total-optimizations');
    if (totalEl) totalEl.textContent = this.history.length;
    
    // Average utilization
    const completed = this.history.filter(h => h.status === 'completed');
    if (completed.length > 0) {
      const avgUtil = completed.reduce((sum, h) => sum + (h.utilization || 0), 0) / completed.length;
      const avgUtilEl = document.getElementById('avg-utilization');
      if (avgUtilEl) avgUtilEl.textContent = `${avgUtil.toFixed(1)}%`;
    }
    
    // Average time
    if (completed.length > 0) {
      const avgTime = completed.reduce((sum, h) => sum + (h.computation_time || 0), 0) / completed.length;
      const avgTimeEl = document.getElementById('avg-time');
      if (avgTimeEl) avgTimeEl.textContent = `${avgTime.toFixed(2)}s`;
    }
    
    // Success rate
    const successRate = (completed.length / this.history.length) * 100;
    const successEl = document.getElementById('success-rate');
    if (successEl) successEl.textContent = `${successRate.toFixed(1)}%`;
    
    // Quick stats
    this.updateQuickStats();
  }
  
  updateQuickStats() {
    // Today's count
    const today = new Date().toDateString();
    const todayCount = this.history.filter(h => 
      new Date(h.started_at).toDateString() === today
    ).length;
    const todayEl = document.getElementById('today-count');
    if (todayEl) todayEl.textContent = todayCount;
    
    // This week
    const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
    const weekCount = this.history.filter(h => 
      new Date(h.started_at) > weekAgo
    ).length;
    const weekEl = document.getElementById('week-count');
    if (weekEl) weekEl.textContent = weekCount;
    
    // Best utilization
    const completed = this.history.filter(h => h.status === 'completed');
    if (completed.length > 0) {
      const bestUtil = Math.max(...completed.map(h => h.utilization || 0));
      const bestEl = document.getElementById('best-util');
      if (bestEl) bestEl.textContent = `${bestUtil.toFixed(1)}%`;
    }
    
    // Active jobs
    const active = this.history.filter(h => h.status === 'running' || h.status === 'pending').length;
    const activeEl = document.getElementById('active-jobs');
    if (activeEl) activeEl.textContent = active;
  }
  
  updateChart() {
    const canvas = document.getElementById('performance-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Get last 10 completed optimizations
    const completed = this.history
      .filter(h => h.status === 'completed')
      .slice(0, 10)
      .reverse();
    
    if (completed.length === 0) {
      ctx.fillStyle = '#9ca3af';
      ctx.font = '14px Inter';
      ctx.textAlign = 'center';
      ctx.fillText('No data yet', canvas.width / 2, canvas.height / 2);
      return;
    }
    
    // Draw simple bar chart
    const barWidth = canvas.width / completed.length;
    const maxUtil = Math.max(...completed.map(h => h.utilization || 0));
    
    completed.forEach((item, i) => {
      const barHeight = (item.utilization / 100) * (canvas.height - 30);
      const x = i * barWidth;
      const y = canvas.height - barHeight - 20;
      
      // Bar color based on utilization
      ctx.fillStyle = item.utilization > 80 ? '#22c55e' : 
                     item.utilization > 60 ? '#f59e0b' : '#ef4444';
      ctx.fillRect(x + 5, y, barWidth - 10, barHeight);
      
      // Value label
      ctx.fillStyle = '#4b5563';
      ctx.font = '10px Inter';
      ctx.textAlign = 'center';
      ctx.fillText(
        `${item.utilization.toFixed(0)}%`, 
        x + barWidth / 2, 
        canvas.height - 5
      );
    });
  }
  
  filterHistory(status) {
    if (status === 'all') {
      this.updateHistoryList();
    } else {
      const filtered = this.history.filter(h => h.status === status);
      this.history = filtered;
      this.updateHistoryList();
    }
  }
  
  formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    // Less than 1 minute
    if (diff < 60000) {
      return 'Just now';
    }
    
    // Less than 1 hour
    if (diff < 3600000) {
      const mins = Math.floor(diff / 60000);
      return `${mins} min${mins > 1 ? 's' : ''} ago`;
    }
    
    // Less than 24 hours
    if (diff < 86400000) {
      const hours = Math.floor(diff / 3600000);
      return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    }
    
    // Format as date
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  }
  
  async refresh() {
    // This would fetch fresh data from API
    console.log('Refreshing dashboard...');
    
    // Show loading indicator
    const refreshBtn = document.getElementById('refresh-btn');
    const icon = refreshBtn?.querySelector('i');
    if (icon) {
      icon.classList.add('fa-spin');
      setTimeout(() => icon.classList.remove('fa-spin'), 1000);
    }
  }
  
  destroy() {
    this.container.innerHTML = '';
  }
}