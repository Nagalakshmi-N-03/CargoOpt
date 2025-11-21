/**
 * CargoOpt Results Viewer Component
 * Displays optimization results with 3D visualization
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

export class ResultsViewer {
  constructor(options = {}) {
    this.containerId = options.containerId || 'results-viewer';
    this.onBack = options.onBack || (() => {});
    this.onExport = options.onExport || (() => {});
    
    this.container = document.getElementById(this.containerId);
    this.result = null;
    
    // Three.js
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    
    this.init();
  }
  
  init() {
    this.render();
  }
  
  render() {
    this.container.innerHTML = `
      <div class="results-container">
        <div class="results-header">
          <button class="btn btn-secondary" id="back-btn">
            <i class="fas fa-arrow-left"></i> Back
          </button>
          <h2>Optimization Results</h2>
          <div class="results-actions">
            <button class="btn btn-secondary" id="export-pdf-btn">
              <i class="fas fa-file-pdf"></i> PDF
            </button>
            <button class="btn btn-secondary" id="export-json-btn">
              <i class="fas fa-file-code"></i> JSON
            </button>
            <button class="btn btn-secondary" id="export-csv-btn">
              <i class="fas fa-file-csv"></i> CSV
            </button>
          </div>
        </div>
        
        <div class="results-body">
          <div class="results-sidebar">
            <div class="results-metrics">
              <h3>Optimization Metrics</h3>
              <div class="metric-card" id="utilization-metric">
                <div class="metric-icon">
                  <i class="fas fa-percentage"></i>
                </div>
                <div class="metric-content">
                  <span class="metric-label">Space Utilization</span>
                  <span class="metric-value">--</span>
                </div>
              </div>
              
              <div class="metric-card" id="items-metric">
                <div class="metric-icon">
                  <i class="fas fa-boxes"></i>
                </div>
                <div class="metric-content">
                  <span class="metric-label">Items Packed</span>
                  <span class="metric-value">--</span>
                </div>
              </div>
              
              <div class="metric-card" id="weight-metric">
                <div class="metric-icon">
                  <i class="fas fa-weight"></i>
                </div>
                <div class="metric-content">
                  <span class="metric-label">Weight Utilization</span>
                  <span class="metric-value">--</span>
                </div>
              </div>
              
              <div class="metric-card" id="time-metric">
                <div class="metric-icon">
                  <i class="fas fa-clock"></i>
                </div>
                <div class="metric-content">
                  <span class="metric-label">Computation Time</span>
                  <span class="metric-value">--</span>
                </div>
              </div>
            </div>
            
            <div class="results-controls">
              <h3>View Controls</h3>
              <button class="control-btn" id="view-front">
                <i class="fas fa-eye"></i> Front View
              </button>
              <button class="control-btn" id="view-side">
                <i class="fas fa-eye"></i> Side View
              </button>
              <button class="control-btn" id="view-top">
                <i class="fas fa-eye"></i> Top View
              </button>
              <button class="control-btn" id="reset-camera">
                <i class="fas fa-sync"></i> Reset Camera
              </button>
              
              <div class="view-options">
                <label>
                  <input type="checkbox" id="show-wireframe"> Wireframe
                </label>
                <label>
                  <input type="checkbox" id="show-axes" checked> Show Axes
                </label>
                <label>
                  <input type="checkbox" id="show-labels"> Labels
                </label>
              </div>
            </div>
          </div>
          
          <div class="results-main">
            <div id="viewer-3d" class="viewer-3d"></div>
            
            <div class="results-tabs">
              <button class="tab-btn active" data-tab="placements">
                <i class="fas fa-list"></i> Placements
              </button>
              <button class="tab-btn" data-tab="statistics">
                <i class="fas fa-chart-bar"></i> Statistics
              </button>
              <button class="tab-btn" data-tab="violations">
                <i class="fas fa-exclamation-triangle"></i> Violations
              </button>
            </div>
            
            <div class="tab-content">
              <div class="tab-pane active" id="placements-tab"></div>
              <div class="tab-pane" id="statistics-tab"></div>
              <div class="tab-pane" id="violations-tab"></div>
            </div>
          </div>
        </div>
      </div>
    `;
    
    this.attachEventListeners();
  }
  
  attachEventListeners() {
    // Navigation
    document.getElementById('back-btn')?.addEventListener('click', () => this.onBack());
    
    // Export buttons
    document.getElementById('export-pdf-btn')?.addEventListener('click', 
      () => this.onExport('pdf', this.result?.optimization_id));
    document.getElementById('export-json-btn')?.addEventListener('click', 
      () => this.onExport('json', this.result?.optimization_id));
    document.getElementById('export-csv-btn')?.addEventListener('click', 
      () => this.onExport('csv', this.result?.optimization_id));
    
    // View controls
    document.getElementById('view-front')?.addEventListener('click', 
      () => this.setView('front'));
    document.getElementById('view-side')?.addEventListener('click', 
      () => this.setView('side'));
    document.getElementById('view-top')?.addEventListener('click', 
      () => this.setView('top'));
    document.getElementById('reset-camera')?.addEventListener('click', 
      () => this.resetCamera());
    
    // View options
    document.getElementById('show-wireframe')?.addEventListener('change', 
      (e) => this.toggleWireframe(e.target.checked));
    document.getElementById('show-axes')?.addEventListener('change', 
      (e) => this.toggleAxes(e.target.checked));
    document.getElementById('show-labels')?.addEventListener('change', 
      (e) => this.toggleLabels(e.target.checked));
    
    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => this.switchTab(btn.dataset.tab));
    });
  }
  
  displayResults(result) {
    this.result = result;
    
    // Update metrics
    this.updateMetrics(result);
    
    // Initialize 3D viewer
    this.init3DViewer();
    
    // Render container and placements
    this.render3DScene(result);
    
    // Update tabs
    this.updatePlacementsTab(result);
    this.updateStatisticsTab(result);
    this.updateViolationsTab(result);
  }
  
  updateMetrics(result) {
    // Utilization
    const utilizationValue = document.querySelector('#utilization-metric .metric-value');
    if (utilizationValue) {
      const util = result.utilization || 0;
      utilizationValue.textContent = `${util.toFixed(1)}%`;
      utilizationValue.style.color = util > 80 ? '#22c55e' : util > 60 ? '#f59e0b' : '#ef4444';
    }
    
    // Items
    const itemsValue = document.querySelector('#items-metric .metric-value');
    if (itemsValue) {
      const packed = result.items_packed || 0;
      const total = result.total_items || 0;
      itemsValue.textContent = `${packed} / ${total}`;
    }
    
    // Weight
    const weightValue = document.querySelector('#weight-metric .metric-value');
    if (weightValue && result.metrics) {
      const weightUtil = result.metrics.weight_utilization || 0;
      weightValue.textContent = `${weightUtil.toFixed(1)}%`;
    }
    
    // Time
    const timeValue = document.querySelector('#time-metric .metric-value');
    if (timeValue) {
      const time = result.computation_time || 0;
      timeValue.textContent = `${time.toFixed(2)}s`;
    }
  }
  
  init3DViewer() {
    const viewerElement = document.getElementById('viewer-3d');
    if (!viewerElement) return;
    
    const width = viewerElement.clientWidth;
    const height = viewerElement.clientHeight || 600;
    
    // Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xf0f0f0);
    
    // Camera
    this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 10000);
    this.camera.position.set(2000, 2000, 2000);
    
    // Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(width, height);
    this.renderer.shadowMap.enabled = true;
    viewerElement.appendChild(this.renderer.domElement);
    
    // Controls
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    
    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    this.scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1000, 1000, 1000);
    directionalLight.castShadow = true;
    this.scene.add(directionalLight);
    
    // Axes helper
    const axesHelper = new THREE.AxesHelper(1000);
    axesHelper.name = 'axes';
    this.scene.add(axesHelper);
    
    // Grid
    const gridHelper = new THREE.GridHelper(5000, 50);
    this.scene.add(gridHelper);
    
    // Animation loop
    this.animate();
  }
  
  render3DScene(result) {
    if (!this.scene) return;
    
    // Clear previous objects
    const objectsToRemove = [];
    this.scene.traverse(obj => {
      if (obj.userData.isContainer || obj.userData.isItem) {
        objectsToRemove.push(obj);
      }
    });
    objectsToRemove.forEach(obj => this.scene.remove(obj));
    
    // Render container
    this.renderContainer(result.container);
    
    // Render placements
    if (result.placements) {
      result.placements.forEach(placement => {
        this.renderPlacement(placement);
      });
    }
    
    // Reset camera to fit scene
    this.fitCameraToScene();
  }
  
  renderContainer(container) {
    const geometry = new THREE.BoxGeometry(
      container.length,
      container.height,
      container.width
    );
    
    const edges = new THREE.EdgesGeometry(geometry);
    const material = new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 });
    const containerMesh = new THREE.LineSegments(edges, material);
    
    containerMesh.position.set(
      container.length / 2,
      container.height / 2,
      container.width / 2
    );
    
    containerMesh.userData.isContainer = true;
    this.scene.add(containerMesh);
  }
  
  renderPlacement(placement) {
    const geometry = new THREE.BoxGeometry(
      placement.length,
      placement.height,
      placement.width
    );
    
    // Random color or from placement
    const color = placement.color || this.getRandomColor();
    const material = new THREE.MeshPhongMaterial({
      color: color,
      transparent: true,
      opacity: 0.8,
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    
    mesh.position.set(
      placement.position_x + placement.length / 2,
      placement.position_z + placement.height / 2,
      placement.position_y + placement.width / 2
    );
    
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.userData.isItem = true;
    mesh.userData.placement = placement;
    
    this.scene.add(mesh);
    
    // Add wireframe
    const edges = new THREE.EdgesGeometry(geometry);
    const lineMaterial = new THREE.LineBasicMaterial({ color: 0x000000 });
    const wireframe = new THREE.LineSegments(edges, lineMaterial);
    wireframe.position.copy(mesh.position);
    wireframe.userData.isWireframe = true;
    this.scene.add(wireframe);
  }
  
  getRandomColor() {
    const colors = [
      0x3b82f6, 0x8b5cf6, 0x22c55e, 0xf59e0b, 
      0xef4444, 0x06b6d4, 0xec4899, 0x10b981
    ];
    return colors[Math.floor(Math.random() * colors.length)];
  }
  
  animate() {
    requestAnimationFrame(() => this.animate());
    
    if (this.controls) {
      this.controls.update();
    }
    
    if (this.renderer && this.scene && this.camera) {
      this.renderer.render(this.scene, this.camera);
    }
  }
  
  setView(view) {
    if (!this.camera) return;
    
    const distance = 3000;
    
    switch (view) {
      case 'front':
        this.camera.position.set(0, distance / 2, distance);
        break;
      case 'side':
        this.camera.position.set(distance, distance / 2, 0);
        break;
      case 'top':
        this.camera.position.set(0, distance, 0);
        break;
    }
    
    this.camera.lookAt(0, 0, 0);
    this.controls?.update();
  }
  
  resetCamera() {
    this.fitCameraToScene();
  }
  
  fitCameraToScene() {
    if (!this.camera || !this.scene) return;
    
    const box = new THREE.Box3().setFromObject(this.scene);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = this.camera.fov * (Math.PI / 180);
    let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
    cameraZ *= 1.5;
    
    this.camera.position.set(center.x + cameraZ, center.y + cameraZ, center.z + cameraZ);
    this.camera.lookAt(center);
    this.controls?.target.copy(center);
    this.controls?.update();
  }
  
  toggleWireframe(show) {
    // Implementation for wireframe toggle
  }
  
  toggleAxes(show) {
    const axes = this.scene?.getObjectByName('axes');
    if (axes) {
      axes.visible = show;
    }
  }
  
  toggleLabels(show) {
    // Implementation for labels toggle
  }
  
  switchTab(tabName) {
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    
    // Update panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
      pane.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`)?.classList.add('active');
  }
  
  updatePlacementsTab(result) {
    const tab = document.getElementById('placements-tab');
    if (!tab) return;
    
    const placements = result.placements || [];
    
    tab.innerHTML = `
      <div class="placements-table">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Item</th>
              <th>Position (X, Y, Z)</th>
              <th>Dimensions</th>
              <th>Weight</th>
            </tr>
          </thead>
          <tbody>
            ${placements.map((p, i) => `
              <tr>
                <td>${i + 1}</td>
                <td>${p.item_name || 'Item ' + (i + 1)}</td>
                <td>${p.position_x}, ${p.position_y}, ${p.position_z}</td>
                <td>${p.length} × ${p.width} × ${p.height}</td>
                <td>${p.weight} kg</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  }
  
  updateStatisticsTab(result) {
    const tab = document.getElementById('statistics-tab');
    if (!tab) return;
    
    tab.innerHTML = `
      <div class="statistics-grid">
        <div class="stat-card">
          <h4>Algorithm</h4>
          <p>${result.algorithm_used || 'N/A'}</p>
        </div>
        <div class="stat-card">
          <h4>Fitness Score</h4>
          <p>${result.fitness_score?.toFixed(3) || 'N/A'}</p>
        </div>
        <div class="stat-card">
          <h4>Total Volume</h4>
          <p>${((result.container?.volume || 0) / 1e9).toFixed(2)} m³</p>
        </div>
        <div class="stat-card">
          <h4>Used Volume</h4>
          <p>${((result.utilization / 100) * (result.container?.volume || 0) / 1e9).toFixed(2)} m³</p>
        </div>
      </div>
    `;
  }
  
  updateViolationsTab(result) {
    const tab = document.getElementById('violations-tab');
    if (!tab) return;
    
    const violations = result.violations || [];
    
    if (violations.length === 0) {
      tab.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-check-circle fa-3x" style="color: #22c55e;"></i>
          <p>No violations detected</p>
        </div>
      `;
    } else {
      tab.innerHTML = `
        <div class="violations-list">
          ${violations.map(v => `
            <div class="violation-item">
              <i class="fas fa-exclamation-triangle"></i>
              <span>${v}</span>
            </div>
          `).join('')}
        </div>
      `;
    }
  }
  
  handleResize() {
    if (!this.camera || !this.renderer) return;
    
    const viewerElement = document.getElementById('viewer-3d');
    if (!viewerElement) return;
    
    const width = viewerElement.clientWidth;
    const height = viewerElement.clientHeight;
    
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }
  
  destroy() {
    if (this.renderer) {
      this.renderer.dispose();
      this.renderer.domElement.remove();
    }
    
    if (this.scene) {
      this.scene.traverse(obj => {
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) obj.material.dispose();
      });
    }
  }
}