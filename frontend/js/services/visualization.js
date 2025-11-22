/**
 * Visualization Service
 * Manages 3D visualization and rendering
 */

import { SceneManager } from '../threejs/scene.js';
import { RendererManager } from '../threejs/renderer.js';
import { Container3D } from '../threejs/container.js';
import { Ship3D } from '../threejs/ship.js';

export class VisualizationService {
  constructor(containerElement, options = {}) {
    this.containerElement = containerElement;
    this.options = options;
    
    // Managers
    this.sceneManager = null;
    this.rendererManager = null;
    
    // 3D Objects
    this.container3D = null;
    this.ship3D = null;
    
    // State
    this.currentView = 'container'; // 'container' or 'ship'
    this.isInitialized = false;
    
    // Event callbacks
    this.onItemClick = options.onItemClick || null;
    this.onItemHover = options.onItemHover || null;
  }
  
  /**
   * Initialize visualization
   */
  async init() {
    if (this.isInitialized) return;
    
    try {
      // Create scene manager
      this.sceneManager = new SceneManager(this.containerElement, this.options);
      
      // Create renderer manager
      this.rendererManager = new RendererManager(
        this.containerElement,
        this.sceneManager,
        this.options
      );
      
      // Setup interactions
      this.setupInteractions();
      
      // Start animation
      this.rendererManager.startAnimation();
      
      this.isInitialized = true;
      
      console.log('Visualization initialized');
    } catch (error) {
      console.error('Failed to initialize visualization:', error);
      throw error;
    }
  }
  
  /**
   * Setup user interactions
   */
  setupInteractions() {
    const canvas = this.rendererManager.getRenderer().domElement;
    
    // Mouse click
    canvas.addEventListener('click', this.handleClick.bind(this));
    
    // Mouse move (for hover)
    canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
    
    // Touch support
    canvas.addEventListener('touchstart', this.handleTouch.bind(this));
  }
  
  /**
   * Handle click event
   */
  handleClick(event) {
    const intersected = this.raycast(event);
    
    if (intersected && intersected.userData.type === 'item') {
      if (this.onItemClick) {
        this.onItemClick(intersected.userData);
      }
    }
  }
  
  /**
   * Handle mouse move
   */
  handleMouseMove(event) {
    const intersected = this.raycast(event);
    
    if (intersected && intersected.userData.type === 'item') {
      if (this.onItemHover) {
        this.onItemHover(intersected.userData);
      }
      
      // Change cursor
      this.containerElement.style.cursor = 'pointer';
    } else {
      this.containerElement.style.cursor = 'default';
    }
  }
  
  /**
   * Handle touch event
   */
  handleTouch(event) {
    if (event.touches.length === 1) {
      this.handleClick(event.touches[0]);
    }
  }
  
  /**
   * Raycast for object picking
   */
  raycast(event) {
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    
    const rect = this.containerElement.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    
    const camera = this.sceneManager.getCamera();
    raycaster.setFromCamera(mouse, camera);
    
    const scene = this.sceneManager.getScene();
    const intersects = raycaster.intersectObjects(scene.children, true);
    
    return intersects.length > 0 ? intersects[0].object : null;
  }
  
  /**
   * Display container optimization result
   */
  displayContainerResult(result) {
    this.currentView = 'container';
    
    // Clear existing visualization
    this.clearVisualization();
    
    // Create container
    this.container3D = new Container3D(result.container, this.options);
    
    // Add items
    if (result.placements && result.placements.length > 0) {
      result.placements.forEach((placement, index) => {
        const itemData = result.items ? result.items[placement.item_index] : {};
        this.container3D.addItem(itemData, placement);
      });
    }
    
    // Add to scene
    const containerGroup = this.container3D.getGroup();
    this.sceneManager.addObject(containerGroup, 'container');
    
    // Fit camera
    this.sceneManager.fitCameraToObject(containerGroup, 1.5);
    
    console.log('Container result displayed');
  }
  
  /**
   * Display ship stowage plan
   */
  displayShipStowage(shipData, stowagePlan) {
    this.currentView = 'ship';
    
    // Clear existing visualization
    this.clearVisualization();
    
    // Create ship
    this.ship3D = new Ship3D(shipData, this.options);
    
    // Load stowage plan
    if (stowagePlan) {
      this.ship3D.loadStowagePlan(stowagePlan);
    }
    
    // Add to scene
    const shipGroup = this.ship3D.getGroup();
    this.sceneManager.addObject(shipGroup, 'ship');
    
    // Fit camera
    this.sceneManager.fitCameraToObject(shipGroup, 2.0);
    
    console.log('Ship stowage displayed');
  }
  
  /**
   * Clear visualization
   */
  clearVisualization() {
    // Dispose existing objects
    if (this.container3D) {
      this.container3D.dispose();
      this.container3D = null;
    }
    
    if (this.ship3D) {
      this.ship3D.dispose();
      this.ship3D = null;
    }
    
    // Clear scene objects
    this.sceneManager.clearObjects();
  }
  
  /**
   * Set camera view
   */
  setView(view) {
    this.sceneManager.setCameraView(view);
  }
  
  /**
   * Reset camera
   */
  resetCamera() {
    if (this.currentView === 'container' && this.container3D) {
      this.sceneManager.fitCameraToObject(this.container3D.getGroup(), 1.5);
    } else if (this.currentView === 'ship' && this.ship3D) {
      this.sceneManager.fitCameraToObject(this.ship3D.getGroup(), 2.0);
    }
  }
  
  /**
   * Toggle wireframe
   */
  toggleWireframe(enabled) {
    if (this.container3D) {
      this.container3D.toggleWireframe(enabled);
    }
  }
  
  /**
   * Toggle grid
   */
  toggleGrid(enabled) {
    this.sceneManager.toggleGrid(enabled);
  }
  
  /**
   * Toggle axes
   */
  toggleAxes(enabled) {
    this.sceneManager.toggleAxes(enabled);
  }
  
  /**
   * Highlight item
   */
  highlightItem(itemIndex, highlight = true) {
    if (this.container3D) {
      this.container3D.highlightItem(itemIndex, highlight);
    }
  }
  
  /**
   * Set item opacity
   */
  setItemOpacity(itemIndex, opacity) {
    if (this.container3D) {
      this.container3D.setItemOpacity(itemIndex, opacity);
    }
  }
  
  /**
   * Set container opacity
   */
  setContainerOpacity(opacity) {
    if (this.container3D) {
      this.container3D.setContainerOpacity(opacity);
    }
  }
  
  /**
   * Take screenshot
   */
  takeScreenshot(width = null, height = null, format = 'image/png') {
    return this.rendererManager.takeScreenshot(width, height, format);
  }
  
  /**
   * Download screenshot
   */
  downloadScreenshot(filename = 'screenshot.png', width = null, height = null) {
    this.rendererManager.downloadScreenshot(filename, width, height);
  }
  
  /**
   * Get statistics
   */
  getStatistics() {
    const renderStats = this.rendererManager.getStats();
    
    let vizStats = {};
    
    if (this.container3D) {
      vizStats = this.container3D.getUtilizationVisualization();
    } else if (this.ship3D) {
      vizStats = this.ship3D.getStatistics();
    }
    
    return {
      rendering: renderStats,
      visualization: vizStats
    };
  }
  
  /**
   * Set render quality
   */
  setRenderQuality(quality) {
    // Quality can be 'low', 'medium', 'high', 'ultra'
    const qualitySettings = {
      low: { pixelRatio: 1, antialias: false, enableShadows: false },
      medium: { pixelRatio: 1.5, antialias: true, enableShadows: true },
      high: { pixelRatio: 2, antialias: true, enableShadows: true },
      ultra: { pixelRatio: 2, antialias: true, enableShadows: true, enablePostProcessing: true }
    };
    
    const settings = qualitySettings[quality] || qualitySettings.medium;
    
    if (settings.pixelRatio !== undefined) {
      this.rendererManager.setPixelRatio(settings.pixelRatio);
    }
    
    if (settings.enableShadows !== undefined) {
      this.rendererManager.setShadowsEnabled(settings.enableShadows);
    }
  }
  
  /**
   * Enable/disable animations
   */
  setAnimationEnabled(enabled) {
    if (enabled) {
      this.rendererManager.startAnimation();
    } else {
      this.rendererManager.stopAnimation();
    }
  }
  
  /**
   * Add animation callback
   */
  onAnimate(callback) {
    this.sceneManager.onAnimate(callback);
  }
  
  /**
   * Remove animation callback
   */
  offAnimate(callback) {
    this.sceneManager.offAnimate(callback);
  }
  
  /**
   * Handle resize
   */
  handleResize() {
    if (this.rendererManager) {
      this.rendererManager.handleResize();
    }
  }
  
  /**
   * Get current view
   */
  getCurrentView() {
    return this.currentView;
  }
  
  /**
   * Get container 3D object
   */
  getContainer3D() {
    return this.container3D;
  }
  
  /**
   * Get ship 3D object
   */
  getShip3D() {
    return this.ship3D;
  }
  
  /**
   * Get scene manager
   */
  getSceneManager() {
    return this.sceneManager;
  }
  
  /**
   * Get renderer manager
   */
  getRendererManager() {
    return this.rendererManager;
  }
  
  /**
   * Dispose visualization
   */
  dispose() {
    // Clear visualization
    this.clearVisualization();
    
    // Dispose managers
    if (this.rendererManager) {
      this.rendererManager.dispose();
    }
    
    if (this.sceneManager) {
      this.sceneManager.dispose();
    }
    
    this.isInitialized = false;
    
    console.log('Visualization disposed');
  }
}

/**
 * Visualization presets
 */
export const VisualizationPresets = {
  container: {
    showWireframe: true,
    showFloor: true,
    containerOpacity: 0.1,
    enableShadows: true
  },
  ship: {
    showGrid: true,
    showLabels: false,
    enableShadows: true
  },
  presentation: {
    showWireframe: false,
    showFloor: true,
    containerOpacity: 0.05,
    enableShadows: true,
    enablePostProcessing: true,
    enableBloom: true
  },
  technical: {
    showWireframe: true,
    showFloor: true,
    showGrid: true,
    showAxes: true,
    containerOpacity: 0.2,
    enableShadows: false
  }
};

export default VisualizationService;