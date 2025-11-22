/**
 * Three.js Scene Manager
 * Manages the 3D scene, camera, and controls
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

export class SceneManager {
  constructor(containerElement, options = {}) {
    this.containerElement = containerElement;
    this.options = {
      backgroundColor: options.backgroundColor || 0xf0f0f0,
      fogColor: options.fogColor || 0xf0f0f0,
      fogNear: options.fogNear || 1000,
      fogFar: options.fogFar || 10000,
      cameraFov: options.cameraFov || 60,
      cameraNear: options.cameraNear || 0.1,
      cameraFar: options.cameraFar || 20000,
      enableShadows: options.enableShadows !== false,
      enableFog: options.enableFog || false,
      gridSize: options.gridSize || 10000,
      gridDivisions: options.gridDivisions || 100,
      ...options
    };
    
    // Three.js core objects
    this.scene = null;
    this.camera = null;
    this.controls = null;
    this.clock = null;
    
    // Helpers
    this.gridHelper = null;
    this.axesHelper = null;
    
    // Objects registry
    this.objects = new Map();
    this.groups = new Map();
    
    // Animation
    this.animationFrameId = null;
    this.animationCallbacks = [];
    
    this.init();
  }
  
  /**
   * Initialize the scene
   */
  init() {
    // Create scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(this.options.backgroundColor);
    
    // Add fog if enabled
    if (this.options.enableFog) {
      this.scene.fog = new THREE.Fog(
        this.options.fogColor,
        this.options.fogNear,
        this.options.fogFar
      );
    }
    
    // Create camera
    this.createCamera();
    
    // Create controls
    this.createControls();
    
    // Add lights
    this.createLights();
    
    // Add helpers
    this.createHelpers();
    
    // Create clock for animations
    this.clock = new THREE.Clock();
    
    console.log('Scene initialized');
  }
  
  /**
   * Create camera
   */
  createCamera() {
    const width = this.containerElement.clientWidth;
    const height = this.containerElement.clientHeight;
    const aspect = width / height;
    
    this.camera = new THREE.PerspectiveCamera(
      this.options.cameraFov,
      aspect,
      this.options.cameraNear,
      this.options.cameraFar
    );
    
    // Default camera position
    this.camera.position.set(5000, 5000, 5000);
    this.camera.lookAt(0, 0, 0);
    
    console.log('Camera created');
  }
  
  /**
   * Create orbit controls
   */
  createControls() {
    if (!this.camera) return;
    
    // Note: renderer canvas will be passed when renderer is created
    this.controlsTarget = null;
    
    console.log('Controls ready for initialization');
  }
  
  /**
   * Initialize controls with renderer
   */
  initializeControls(rendererDomElement) {
    this.controls = new OrbitControls(this.camera, rendererDomElement);
    
    // Configure controls
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.screenSpacePanning = false;
    this.controls.minDistance = 100;
    this.controls.maxDistance = 15000;
    this.controls.maxPolarAngle = Math.PI / 2;
    
    // Mouse buttons
    this.controls.mouseButtons = {
      LEFT: THREE.MOUSE.ROTATE,
      MIDDLE: THREE.MOUSE.DOLLY,
      RIGHT: THREE.MOUSE.PAN
    };
    
    console.log('Controls initialized');
  }
  
  /**
   * Create lighting
   */
  createLights() {
    // Ambient light for overall illumination
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    ambientLight.name = 'ambient_light';
    this.scene.add(ambientLight);
    
    // Directional light (main light)
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5000, 5000, 5000);
    directionalLight.name = 'main_light';
    
    if (this.options.enableShadows) {
      directionalLight.castShadow = true;
      directionalLight.shadow.mapSize.width = 2048;
      directionalLight.shadow.mapSize.height = 2048;
      directionalLight.shadow.camera.near = 100;
      directionalLight.shadow.camera.far = 15000;
      directionalLight.shadow.camera.left = -5000;
      directionalLight.shadow.camera.right = 5000;
      directionalLight.shadow.camera.top = 5000;
      directionalLight.shadow.camera.bottom = -5000;
    }
    
    this.scene.add(directionalLight);
    
    // Hemisphere light for ambient sky/ground color
    const hemisphereLight = new THREE.HemisphereLight(0xffffbb, 0x080820, 0.3);
    hemisphereLight.name = 'hemisphere_light';
    this.scene.add(hemisphereLight);
    
    // Point lights for additional illumination
    const pointLight1 = new THREE.PointLight(0xffffff, 0.3, 10000);
    pointLight1.position.set(-3000, 3000, 3000);
    pointLight1.name = 'point_light_1';
    this.scene.add(pointLight1);
    
    const pointLight2 = new THREE.PointLight(0xffffff, 0.3, 10000);
    pointLight2.position.set(3000, 3000, -3000);
    pointLight2.name = 'point_light_2';
    this.scene.add(pointLight2);
    
    console.log('Lights created');
  }
  
  /**
   * Create scene helpers (grid, axes)
   */
  createHelpers() {
    // Grid helper
    this.gridHelper = new THREE.GridHelper(
      this.options.gridSize,
      this.options.gridDivisions,
      0x888888,
      0xcccccc
    );
    this.gridHelper.name = 'grid_helper';
    this.gridHelper.material.opacity = 0.3;
    this.gridHelper.material.transparent = true;
    this.scene.add(this.gridHelper);
    
    // Axes helper
    this.axesHelper = new THREE.AxesHelper(2000);
    this.axesHelper.name = 'axes_helper';
    this.scene.add(this.axesHelper);
    
    console.log('Helpers created');
  }
  
  /**
   * Add object to scene
   */
  addObject(object, name = null) {
    if (name) {
      object.name = name;
      this.objects.set(name, object);
    }
    this.scene.add(object);
    return object;
  }
  
  /**
   * Remove object from scene
   */
  removeObject(nameOrObject) {
    let object;
    
    if (typeof nameOrObject === 'string') {
      object = this.objects.get(nameOrObject);
      this.objects.delete(nameOrObject);
    } else {
      object = nameOrObject;
      // Remove from registry if exists
      for (const [name, obj] of this.objects.entries()) {
        if (obj === object) {
          this.objects.delete(name);
          break;
        }
      }
    }
    
    if (object) {
      this.scene.remove(object);
      this.disposeObject(object);
    }
  }
  
  /**
   * Get object by name
   */
  getObject(name) {
    return this.objects.get(name);
  }
  
  /**
   * Create group
   */
  createGroup(name) {
    const group = new THREE.Group();
    group.name = name;
    this.groups.set(name, group);
    this.scene.add(group);
    return group;
  }
  
  /**
   * Get group by name
   */
  getGroup(name) {
    return this.groups.get(name);
  }
  
  /**
   * Clear all objects from scene
   */
  clearObjects() {
    // Remove all registered objects
    this.objects.forEach((object, name) => {
      this.scene.remove(object);
      this.disposeObject(object);
    });
    this.objects.clear();
    
    // Remove all groups
    this.groups.forEach((group, name) => {
      this.scene.remove(group);
      this.disposeObject(group);
    });
    this.groups.clear();
  }
  
  /**
   * Dispose object and its resources
   */
  disposeObject(object) {
    object.traverse((child) => {
      if (child.geometry) {
        child.geometry.dispose();
      }
      
      if (child.material) {
        if (Array.isArray(child.material)) {
          child.material.forEach(material => material.dispose());
        } else {
          child.material.dispose();
        }
      }
      
      if (child.texture) {
        child.texture.dispose();
      }
    });
  }
  
  /**
   * Set camera position
   */
  setCameraPosition(x, y, z) {
    if (this.camera) {
      this.camera.position.set(x, y, z);
    }
  }
  
  /**
   * Set camera view
   */
  setCameraView(view) {
    if (!this.camera || !this.controls) return;
    
    const distance = 6000;
    const target = new THREE.Vector3(0, 0, 0);
    
    switch (view) {
      case 'front':
        this.camera.position.set(0, distance / 2, distance);
        break;
      case 'back':
        this.camera.position.set(0, distance / 2, -distance);
        break;
      case 'left':
        this.camera.position.set(-distance, distance / 2, 0);
        break;
      case 'right':
        this.camera.position.set(distance, distance / 2, 0);
        break;
      case 'top':
        this.camera.position.set(0, distance, 0);
        break;
      case 'bottom':
        this.camera.position.set(0, -distance, 0);
        break;
      case 'isometric':
        this.camera.position.set(distance, distance, distance);
        break;
      default:
        this.camera.position.set(distance, distance, distance);
    }
    
    this.camera.lookAt(target);
    this.controls.target.copy(target);
    this.controls.update();
  }
  
  /**
   * Fit camera to object
   */
  fitCameraToObject(object, offset = 1.5) {
    if (!this.camera || !this.controls) return;
    
    const boundingBox = new THREE.Box3().setFromObject(object);
    const center = boundingBox.getCenter(new THREE.Vector3());
    const size = boundingBox.getSize(new THREE.Vector3());
    
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = this.camera.fov * (Math.PI / 180);
    let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
    cameraZ *= offset;
    
    this.camera.position.set(
      center.x + cameraZ,
      center.y + cameraZ,
      center.z + cameraZ
    );
    this.camera.lookAt(center);
    
    this.controls.target.copy(center);
    this.controls.maxDistance = cameraZ * 3;
    this.controls.update();
  }
  
  /**
   * Fit camera to selection
   */
  fitCameraToSelection(objects, offset = 1.5) {
    if (!this.camera || !this.controls || objects.length === 0) return;
    
    const boundingBox = new THREE.Box3();
    objects.forEach(obj => {
      const box = new THREE.Box3().setFromObject(obj);
      boundingBox.union(box);
    });
    
    const center = boundingBox.getCenter(new THREE.Vector3());
    const size = boundingBox.getSize(new THREE.Vector3());
    
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = this.camera.fov * (Math.PI / 180);
    let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
    cameraZ *= offset;
    
    this.camera.position.set(
      center.x + cameraZ,
      center.y + cameraZ,
      center.z + cameraZ
    );
    this.camera.lookAt(center);
    
    this.controls.target.copy(center);
    this.controls.update();
  }
  
  /**
   * Toggle grid visibility
   */
  toggleGrid(visible) {
    if (this.gridHelper) {
      this.gridHelper.visible = visible;
    }
  }
  
  /**
   * Toggle axes visibility
   */
  toggleAxes(visible) {
    if (this.axesHelper) {
      this.axesHelper.visible = visible;
    }
  }
  
  /**
   * Update camera aspect ratio
   */
  updateCameraAspect() {
    if (!this.camera) return;
    
    const width = this.containerElement.clientWidth;
    const height = this.containerElement.clientHeight;
    
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
  }
  
  /**
   * Update controls
   */
  updateControls() {
    if (this.controls) {
      this.controls.update();
    }
  }
  
  /**
   * Add animation callback
   */
  onAnimate(callback) {
    this.animationCallbacks.push(callback);
  }
  
  /**
   * Remove animation callback
   */
  offAnimate(callback) {
    const index = this.animationCallbacks.indexOf(callback);
    if (index > -1) {
      this.animationCallbacks.splice(index, 1);
    }
  }
  
  /**
   * Animation loop (called by renderer)
   */
  animate() {
    const delta = this.clock.getDelta();
    const elapsed = this.clock.getElapsedTime();
    
    // Update controls
    this.updateControls();
    
    // Call animation callbacks
    this.animationCallbacks.forEach(callback => {
      callback(delta, elapsed);
    });
  }
  
  /**
   * Get scene for rendering
   */
  getScene() {
    return this.scene;
  }
  
  /**
   * Get camera for rendering
   */
  getCamera() {
    return this.camera;
  }
  
  /**
   * Get controls
   */
  getControls() {
    return this.controls;
  }
  
  /**
   * Dispose scene and all resources
   */
  dispose() {
    // Clear all objects
    this.clearObjects();
    
    // Dispose helpers
    if (this.gridHelper) {
      this.gridHelper.geometry.dispose();
      this.gridHelper.material.dispose();
    }
    
    if (this.axesHelper) {
      this.axesHelper.geometry.dispose();
      this.axesHelper.material.dispose();
    }
    
    // Dispose controls
    if (this.controls) {
      this.controls.dispose();
    }
    
    // Clear scene
    if (this.scene) {
      this.scene.traverse((object) => {
        if (object.geometry) object.geometry.dispose();
        if (object.material) {
          if (Array.isArray(object.material)) {
            object.material.forEach(material => material.dispose());
          } else {
            object.material.dispose();
          }
        }
      });
    }
    
    console.log('Scene disposed');
  }
}