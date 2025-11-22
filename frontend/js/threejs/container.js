/**
 * Container 3D Visualization
 * Renders shipping containers and cargo items in 3D
 */

import * as THREE from 'three';

export class Container3D {
  constructor(containerData, options = {}) {
    this.containerData = containerData;
    this.options = {
      showWireframe: options.showWireframe || true,
      wireframeColor: options.wireframeColor || 0x000000,
      containerColor: options.containerColor || 0x3b82f6,
      containerOpacity: options.containerOpacity || 0.1,
      wallThickness: options.wallThickness || 50,
      showFloor: options.showFloor !== false,
      showDimensions: options.showDimensions || false,
      ...options
    };
    
    // Three.js objects
    this.group = new THREE.Group();
    this.containerMesh = null;
    this.wireframe = null;
    this.floor = null;
    this.walls = [];
    this.dimensionLabels = [];
    
    // Items in container
    this.items = [];
    this.itemMeshes = new Map();
    
    this.init();
  }
  
  /**
   * Initialize container
   */
  init() {
    this.createContainer();
    
    if (this.options.showFloor) {
      this.createFloor();
    }
    
    if (this.options.showDimensions) {
      this.createDimensionLabels();
    }
  }
  
  /**
   * Create container structure
   */
  createContainer() {
    const { length, width, height } = this.containerData;
    
    // Create container box geometry
    const geometry = new THREE.BoxGeometry(length, height, width);
    
    // Container material (semi-transparent)
    const material = new THREE.MeshPhongMaterial({
      color: this.options.containerColor,
      transparent: true,
      opacity: this.options.containerOpacity,
      side: THREE.BackSide,
      depthWrite: false
    });
    
    this.containerMesh = new THREE.Mesh(geometry, material);
    this.containerMesh.position.set(length / 2, height / 2, width / 2);
    this.containerMesh.name = 'container_body';
    this.group.add(this.containerMesh);
    
    // Create wireframe
    if (this.options.showWireframe) {
      this.createWireframe();
    }
    
    // Create walls (optional - for better visualization)
    this.createWalls();
  }
  
  /**
   * Create wireframe edges
   */
  createWireframe() {
    const { length, width, height } = this.containerData;
    
    const geometry = new THREE.BoxGeometry(length, height, width);
    const edges = new THREE.EdgesGeometry(geometry);
    const material = new THREE.LineBasicMaterial({
      color: this.options.wireframeColor,
      linewidth: 2
    });
    
    this.wireframe = new THREE.LineSegments(edges, material);
    this.wireframe.position.set(length / 2, height / 2, width / 2);
    this.wireframe.name = 'container_wireframe';
    this.group.add(this.wireframe);
  }
  
  /**
   * Create container walls
   */
  createWalls() {
    const { length, width, height } = this.containerData;
    const thickness = this.options.wallThickness;
    
    const wallMaterial = new THREE.MeshPhongMaterial({
      color: 0x808080,
      transparent: true,
      opacity: 0.2,
      side: THREE.DoubleSide
    });
    
    // Back wall
    const backWall = new THREE.Mesh(
      new THREE.PlaneGeometry(length, height),
      wallMaterial
    );
    backWall.position.set(length / 2, height / 2, 0);
    backWall.name = 'wall_back';
    this.walls.push(backWall);
    this.group.add(backWall);
    
    // Left wall
    const leftWall = new THREE.Mesh(
      new THREE.PlaneGeometry(width, height),
      wallMaterial
    );
    leftWall.rotation.y = Math.PI / 2;
    leftWall.position.set(0, height / 2, width / 2);
    leftWall.name = 'wall_left';
    this.walls.push(leftWall);
    this.group.add(leftWall);
    
    // Right wall
    const rightWall = new THREE.Mesh(
      new THREE.PlaneGeometry(width, height),
      wallMaterial
    );
    rightWall.rotation.y = -Math.PI / 2;
    rightWall.position.set(length, height / 2, width / 2);
    rightWall.name = 'wall_right';
    this.walls.push(rightWall);
    this.group.add(rightWall);
  }
  
  /**
   * Create floor
   */
  createFloor() {
    const { length, width } = this.containerData;
    
    const floorGeometry = new THREE.PlaneGeometry(length, width);
    const floorMaterial = new THREE.MeshStandardMaterial({
      color: 0x8B4513,
      roughness: 0.8,
      metalness: 0.2
    });
    
    this.floor = new THREE.Mesh(floorGeometry, floorMaterial);
    this.floor.rotation.x = -Math.PI / 2;
    this.floor.position.set(length / 2, 0, width / 2);
    this.floor.receiveShadow = true;
    this.floor.name = 'container_floor';
    this.group.add(this.floor);
  }
  
  /**
   * Create dimension labels
   */
  createDimensionLabels() {
    // This would use THREE.TextGeometry or CSS2DRenderer for labels
    // Simplified version - would need actual text rendering
    console.log('Dimension labels would be shown here');
  }
  
  /**
   * Add item to container
   */
  addItem(itemData, placement) {
    const itemMesh = this.createItemMesh(itemData, placement);
    
    if (itemMesh) {
      this.items.push({ data: itemData, placement, mesh: itemMesh });
      this.itemMeshes.set(placement.item_index || this.items.length - 1, itemMesh);
      this.group.add(itemMesh);
    }
    
    return itemMesh;
  }
  
  /**
   * Create item mesh
   */
  createItemMesh(itemData, placement) {
    const geometry = new THREE.BoxGeometry(
      placement.length,
      placement.height,
      placement.width
    );
    
    // Get color from item data or generate random
    const color = this.getItemColor(itemData);
    
    const material = new THREE.MeshPhongMaterial({
      color: color,
      transparent: true,
      opacity: 0.8,
      shininess: 30
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    
    // Position item (center of box)
    mesh.position.set(
      placement.position_x + placement.length / 2,
      placement.position_z + placement.height / 2,
      placement.position_y + placement.width / 2
    );
    
    // Rotation if needed
    if (placement.rotation) {
      mesh.rotation.y = THREE.MathUtils.degToRad(placement.rotation);
    }
    
    // Add wireframe to item
    const edges = new THREE.EdgesGeometry(geometry);
    const edgeMaterial = new THREE.LineBasicMaterial({ color: 0x000000 });
    const wireframe = new THREE.LineSegments(edges, edgeMaterial);
    mesh.add(wireframe);
    
    // Shadow
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    
    // User data
    mesh.userData = {
      itemData,
      placement,
      type: 'item'
    };
    
    mesh.name = `item_${placement.item_index || this.items.length}`;
    
    return mesh;
  }
  
  /**
   * Get item color
   */
  getItemColor(itemData) {
    // Use color from item data if available
    if (itemData.color) {
      return new THREE.Color(itemData.color);
    }
    
    // Color by item type
    const typeColors = {
      glass: 0x87CEEB,
      wood: 0x8B4513,
      metal: 0x708090,
      plastic: 0xFFB6C1,
      electronics: 0x4169E1,
      textiles: 0xDDA0DD,
      food: 0xFFA500,
      chemicals: 0xFF4500,
      other: 0xA9A9A9
    };
    
    const itemType = itemData.item_type || 'other';
    return typeColors[itemType] || typeColors.other;
  }
  
  /**
   * Remove item
   */
  removeItem(itemIndex) {
    const mesh = this.itemMeshes.get(itemIndex);
    
    if (mesh) {
      this.group.remove(mesh);
      this.disposeMesh(mesh);
      this.itemMeshes.delete(itemIndex);
      
      // Remove from items array
      this.items = this.items.filter((item, idx) => 
        (item.placement.item_index || idx) !== itemIndex
      );
    }
  }
  
  /**
   * Clear all items
   */
  clearItems() {
    this.itemMeshes.forEach((mesh, index) => {
      this.group.remove(mesh);
      this.disposeMesh(mesh);
    });
    
    this.items = [];
    this.itemMeshes.clear();
  }
  
  /**
   * Add multiple items (optimized)
   */
  addItems(itemsData, placements) {
    placements.forEach((placement, index) => {
      const itemData = itemsData[placement.item_index] || {};
      this.addItem(itemData, placement);
    });
  }
  
  /**
   * Highlight item
   */
  highlightItem(itemIndex, highlight = true) {
    const mesh = this.itemMeshes.get(itemIndex);
    
    if (mesh) {
      if (highlight) {
        mesh.material.emissive = new THREE.Color(0xffff00);
        mesh.material.emissiveIntensity = 0.3;
      } else {
        mesh.material.emissive = new THREE.Color(0x000000);
        mesh.material.emissiveIntensity = 0;
      }
    }
  }
  
  /**
   * Set item opacity
   */
  setItemOpacity(itemIndex, opacity) {
    const mesh = this.itemMeshes.get(itemIndex);
    
    if (mesh) {
      mesh.material.opacity = opacity;
    }
  }
  
  /**
   * Toggle wireframe visibility
   */
  toggleWireframe(visible) {
    if (this.wireframe) {
      this.wireframe.visible = visible;
    }
  }
  
  /**
   * Toggle walls visibility
   */
  toggleWalls(visible) {
    this.walls.forEach(wall => {
      wall.visible = visible;
    });
  }
  
  /**
   * Toggle floor visibility
   */
  toggleFloor(visible) {
    if (this.floor) {
      this.floor.visible = visible;
    }
  }
  
  /**
   * Set container opacity
   */
  setContainerOpacity(opacity) {
    if (this.containerMesh) {
      this.containerMesh.material.opacity = opacity;
    }
    
    this.walls.forEach(wall => {
      wall.material.opacity = opacity * 0.5;
    });
  }
  
  /**
   * Get group (for adding to scene)
   */
  getGroup() {
    return this.group;
  }
  
  /**
   * Get bounding box
   */
  getBoundingBox() {
    const box = new THREE.Box3().setFromObject(this.group);
    return box;
  }
  
  /**
   * Get center point
   */
  getCenter() {
    const box = this.getBoundingBox();
    return box.getCenter(new THREE.Vector3());
  }
  
  /**
   * Get item by index
   */
  getItem(itemIndex) {
    return this.items.find((item, idx) => 
      (item.placement.item_index || idx) === itemIndex
    );
  }
  
  /**
   * Get all items
   */
  getItems() {
    return this.items;
  }
  
  /**
   * Get utilization visualization
   */
  getUtilizationVisualization() {
    const containerVolume = this.containerData.length * 
                           this.containerData.width * 
                           this.containerData.height;
    
    const usedVolume = this.items.reduce((sum, item) => {
      return sum + (item.placement.length * 
                   item.placement.width * 
                   item.placement.height);
    }, 0);
    
    const utilization = (usedVolume / containerVolume) * 100;
    
    return {
      containerVolume,
      usedVolume,
      utilization,
      itemCount: this.items.length
    };
  }
  
  /**
   * Dispose mesh
   */
  disposeMesh(mesh) {
    if (mesh.geometry) {
      mesh.geometry.dispose();
    }
    
    if (mesh.material) {
      if (Array.isArray(mesh.material)) {
        mesh.material.forEach(mat => mat.dispose());
      } else {
        mesh.material.dispose();
      }
    }
    
    // Dispose children
    mesh.children.forEach(child => {
      this.disposeMesh(child);
    });
  }
  
  /**
   * Dispose container
   */
  dispose() {
    // Clear items
    this.clearItems();
    
    // Dispose container
    if (this.containerMesh) {
      this.disposeMesh(this.containerMesh);
    }
    
    // Dispose wireframe
    if (this.wireframe) {
      this.disposeMesh(this.wireframe);
    }
    
    // Dispose floor
    if (this.floor) {
      this.disposeMesh(this.floor);
    }
    
    // Dispose walls
    this.walls.forEach(wall => {
      this.disposeMesh(wall);
    });
    
    // Clear group
    this.group.clear();
  }
}

/**
 * Standard container presets
 */
export const ContainerPresets = {
  '20ft': {
    name: '20ft Standard',
    length: 5898,
    width: 2352,
    height: 2393,
    max_weight: 28180
  },
  '40ft': {
    name: '40ft Standard',
    length: 12032,
    width: 2352,
    height: 2393,
    max_weight: 26680
  },
  '40ft_hc': {
    name: '40ft High Cube',
    length: 12032,
    width: 2352,
    height: 2698,
    max_weight: 26560
  },
  '45ft_hc': {
    name: '45ft High Cube',
    length: 13556,
    width: 2352,
    height: 2698,
    max_weight: 27700
  }
};