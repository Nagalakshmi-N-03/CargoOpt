/**
 * Three.js Renderer Manager
 * Manages WebGL renderer and post-processing
 */

import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { SSAARenderPass } from 'three/examples/jsm/postprocessing/SSAARenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';

export class RendererManager {
  constructor(containerElement, sceneManager, options = {}) {
    this.containerElement = containerElement;
    this.sceneManager = sceneManager;
    this.options = {
      antialias: options.antialias !== false,
      pixelRatio: options.pixelRatio || window.devicePixelRatio,
      maxPixelRatio: options.maxPixelRatio || 2,
      enableShadows: options.enableShadows !== false,
      shadowMapType: options.shadowMapType || THREE.PCFSoftShadowMap,
      toneMapping: options.toneMapping || THREE.ACESFilmicToneMapping,
      toneMappingExposure: options.toneMappingExposure || 1.0,
      enablePostProcessing: options.enablePostProcessing || false,
      enableBloom: options.enableBloom || false,
      ...options
    };
    
    // Renderer
    this.renderer = null;
    
    // Post-processing
    this.composer = null;
    this.renderPass = null;
    this.bloomPass = null;
    
    // Animation
    this.animationFrameId = null;
    this.isAnimating = false;
    
    // Performance
    this.frameCount = 0;
    this.lastTime = performance.now();
    this.fps = 0;
    
    // Stats
    this.stats = {
      fps: 0,
      frameTime: 0,
      drawCalls: 0,
      triangles: 0,
      points: 0,
      lines: 0,
      memory: 0
    };
    
    this.init();
  }
  
  /**
   * Initialize renderer
   */
  init() {
    // Create WebGL renderer
    this.createRenderer();
    
    // Initialize controls in scene manager
    if (this.renderer && this.sceneManager) {
      this.sceneManager.initializeControls(this.renderer.domElement);
    }
    
    // Create post-processing if enabled
    if (this.options.enablePostProcessing) {
      this.createPostProcessing();
    }
    
    // Add resize listener
    window.addEventListener('resize', this.handleResize.bind(this));
    
    console.log('Renderer initialized');
  }
  
  /**
   * Create WebGL renderer
   */
  createRenderer() {
    const width = this.containerElement.clientWidth;
    const height = this.containerElement.clientHeight;
    
    // Create renderer
    this.renderer = new THREE.WebGLRenderer({
      antialias: this.options.antialias,
      alpha: true,
      preserveDrawingBuffer: true, // For screenshots
      powerPreference: 'high-performance'
    });
    
    // Set size and pixel ratio
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(
      Math.min(this.options.pixelRatio, this.options.maxPixelRatio)
    );
    
    // Enable shadows
    if (this.options.enableShadows) {
      this.renderer.shadowMap.enabled = true;
      this.renderer.shadowMap.type = this.options.shadowMapType;
    }
    
    // Tone mapping
    this.renderer.toneMapping = this.options.toneMapping;
    this.renderer.toneMappingExposure = this.options.toneMappingExposure;
    
    // Output encoding
    this.renderer.outputEncoding = THREE.sRGBEncoding;
    
    // Append to container
    this.containerElement.appendChild(this.renderer.domElement);
    
    console.log('WebGL renderer created');
  }
  
  /**
   * Create post-processing pipeline
   */
  createPostProcessing() {
    if (!this.renderer || !this.sceneManager) return;
    
    const scene = this.sceneManager.getScene();
    const camera = this.sceneManager.getCamera();
    
    // Create composer
    this.composer = new EffectComposer(this.renderer);
    
    // Render pass
    this.renderPass = new RenderPass(scene, camera);
    this.composer.addPass(this.renderPass);
    
    // SSAA (Super Sampling Anti-Aliasing) pass
    if (this.options.enableSSAA) {
      const ssaaPass = new SSAARenderPass(scene, camera);
      ssaaPass.sampleLevel = 2;
      this.composer.addPass(ssaaPass);
    }
    
    // Bloom pass
    if (this.options.enableBloom) {
      const bloomPass = new UnrealBloomPass(
        new THREE.Vector2(
          this.containerElement.clientWidth,
          this.containerElement.clientHeight
        ),
        0.5,  // strength
        0.4,  // radius
        0.85  // threshold
      );
      this.bloomPass = bloomPass;
      this.composer.addPass(bloomPass);
    }
    
    console.log('Post-processing created');
  }
  
  /**
   * Start animation loop
   */
  startAnimation() {
    if (this.isAnimating) return;
    
    this.isAnimating = true;
    this.animate();
    
    console.log('Animation started');
  }
  
  /**
   * Stop animation loop
   */
  stopAnimation() {
    if (!this.isAnimating) return;
    
    this.isAnimating = false;
    
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
    
    console.log('Animation stopped');
  }
  
  /**
   * Animation loop
   */
  animate() {
    if (!this.isAnimating) return;
    
    this.animationFrameId = requestAnimationFrame(this.animate.bind(this));
    
    // Update scene
    if (this.sceneManager) {
      this.sceneManager.animate();
    }
    
    // Render
    this.render();
    
    // Update stats
    this.updateStats();
  }
  
  /**
   * Render scene
   */
  render() {
    if (!this.renderer || !this.sceneManager) return;
    
    const scene = this.sceneManager.getScene();
    const camera = this.sceneManager.getCamera();
    
    if (!scene || !camera) return;
    
    // Render with post-processing or directly
    if (this.composer) {
      this.composer.render();
    } else {
      this.renderer.render(scene, camera);
    }
  }
  
  /**
   * Update performance stats
   */
  updateStats() {
    this.frameCount++;
    
    const currentTime = performance.now();
    const elapsed = currentTime - this.lastTime;
    
    if (elapsed >= 1000) {
      this.fps = Math.round((this.frameCount * 1000) / elapsed);
      this.frameCount = 0;
      this.lastTime = currentTime;
      
      // Get renderer info
      if (this.renderer) {
        const info = this.renderer.info;
        
        this.stats = {
          fps: this.fps,
          frameTime: elapsed / this.frameCount,
          drawCalls: info.render.calls,
          triangles: info.render.triangles,
          points: info.render.points,
          lines: info.render.lines,
          memory: info.memory.geometries + info.memory.textures
        };
      }
    }
  }
  
  /**
   * Get current stats
   */
  getStats() {
    return { ...this.stats };
  }
  
  /**
   * Handle window resize
   */
  handleResize() {
    if (!this.renderer || !this.sceneManager) return;
    
    const width = this.containerElement.clientWidth;
    const height = this.containerElement.clientHeight;
    
    // Update camera
    this.sceneManager.updateCameraAspect();
    
    // Update renderer
    this.renderer.setSize(width, height);
    
    // Update composer
    if (this.composer) {
      this.composer.setSize(width, height);
    }
    
    // Update bloom pass
    if (this.bloomPass) {
      this.bloomPass.resolution.set(width, height);
    }
    
    // Re-render
    this.render();
  }
  
  /**
   * Take screenshot
   */
  takeScreenshot(width = null, height = null, format = 'image/png') {
    if (!this.renderer) return null;
    
    const originalWidth = this.renderer.domElement.width;
    const originalHeight = this.renderer.domElement.height;
    
    // Set custom size if provided
    if (width && height) {
      this.renderer.setSize(width, height, false);
      this.sceneManager.updateCameraAspect();
      this.render();
    }
    
    // Get screenshot
    const dataURL = this.renderer.domElement.toDataURL(format);
    
    // Restore original size
    if (width && height) {
      this.renderer.setSize(originalWidth, originalHeight, false);
      this.sceneManager.updateCameraAspect();
      this.render();
    }
    
    return dataURL;
  }
  
  /**
   * Download screenshot
   */
  downloadScreenshot(filename = 'screenshot.png', width = null, height = null) {
    const dataURL = this.takeScreenshot(width, height);
    
    if (!dataURL) return;
    
    const link = document.createElement('a');
    link.download = filename;
    link.href = dataURL;
    link.click();
  }
  
  /**
   * Enable/disable shadows
   */
  setShadowsEnabled(enabled) {
    if (this.renderer) {
      this.renderer.shadowMap.enabled = enabled;
      this.options.enableShadows = enabled;
    }
  }
  
  /**
   * Set tone mapping
   */
  setToneMapping(type, exposure = 1.0) {
    if (this.renderer) {
      this.renderer.toneMapping = type;
      this.renderer.toneMappingExposure = exposure;
    }
  }
  
  /**
   * Set pixel ratio
   */
  setPixelRatio(ratio) {
    if (this.renderer) {
      const clampedRatio = Math.min(ratio, this.options.maxPixelRatio);
      this.renderer.setPixelRatio(clampedRatio);
      this.options.pixelRatio = clampedRatio;
    }
  }
  
  /**
   * Enable/disable bloom
   */
  setBloomEnabled(enabled) {
    if (this.bloomPass) {
      this.bloomPass.enabled = enabled;
    }
  }
  
  /**
   * Set bloom parameters
   */
  setBloomParams(strength, radius, threshold) {
    if (this.bloomPass) {
      this.bloomPass.strength = strength;
      this.bloomPass.radius = radius;
      this.bloomPass.threshold = threshold;
    }
  }
  
  /**
   * Get renderer
   */
  getRenderer() {
    return this.renderer;
  }
  
  /**
   * Get composer
   */
  getComposer() {
    return this.composer;
  }
  
  /**
   * Clear renderer
   */
  clear() {
    if (this.renderer) {
      this.renderer.clear();
    }
  }
  
  /**
   * Dispose renderer and resources
   */
  dispose() {
    // Stop animation
    this.stopAnimation();
    
    // Remove resize listener
    window.removeEventListener('resize', this.handleResize.bind(this));
    
    // Dispose composer
    if (this.composer) {
      this.composer.dispose();
    }
    
    // Dispose renderer
    if (this.renderer) {
      this.renderer.dispose();
      this.renderer.forceContextLoss();
      
      // Remove canvas
      if (this.renderer.domElement.parentNode) {
        this.renderer.domElement.parentNode.removeChild(this.renderer.domElement);
      }
    }
    
    console.log('Renderer disposed');
  }
}

/**
 * Render quality presets
 */
export const RenderQuality = {
  LOW: {
    pixelRatio: 1,
    antialias: false,
    enableShadows: false,
    enablePostProcessing: false,
    shadowMapType: THREE.BasicShadowMap
  },
  MEDIUM: {
    pixelRatio: 1.5,
    antialias: true,
    enableShadows: true,
    enablePostProcessing: false,
    shadowMapType: THREE.PCFShadowMap
  },
  HIGH: {
    pixelRatio: 2,
    antialias: true,
    enableShadows: true,
    enablePostProcessing: true,
    shadowMapType: THREE.PCFSoftShadowMap
  },
  ULTRA: {
    pixelRatio: 2,
    antialias: true,
    enableShadows: true,
    enablePostProcessing: true,
    enableSSAA: true,
    enableBloom: true,
    shadowMapType: THREE.PCFSoftShadowMap
  }
};