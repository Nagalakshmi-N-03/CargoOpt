/**
 * Ship 3D Visualization
 * Renders cargo ships with container stowage
 */

import * as THREE from 'three';

export class Ship3D {
  constructor(shipData, options = {}) {
    this.shipData = shipData;
    this.options = {
      shipColor: options.shipColor || 0x2c3e50,
      deckColor: options.deckColor || 0x34495e,
      showGrid: options.showGrid !== false,
      showLabels: options.showLabels || false,
      baySpacing: options.baySpacing || 100,
      ...options
    };
    
    // Three.js objects
    this.group = new THREE.Group();
    this.hull = null;
    this.deck = null;
    this.superstructure = null;
    this.containers = [];
    this.containerMeshes = new Map();
    this.bayMarkers = [];
    
    this.init();
  }
  
  /**
   * Initialize ship
   */
  init() {
    this.createShipHull();
    this.createDeck();
    this.createSuperstructure();
    
    if (this.options.showGrid) {
      this.createStowageGrid();
    }
  }
  
  /**
   * Create ship hull
   */
  createShipHull() {
    const length = this.shipData.length_m * 1000; // Convert to mm
    const width = this.shipData.width_m * 1000;
    const height = this.shipData.draft_m * 1000;
    
    // Create hull shape (simplified)
    const hullGeometry = this.createHullGeometry(length, width, height);
    const hullMaterial = new THREE.MeshPhongMaterial({
      color: this.options.shipColor,
      shininess: 50,
      side: THREE.DoubleSide
    });
    
    this.hull = new THREE.Mesh(hullGeometry, hullMaterial);
    this.hull.position.set(0, -height / 2, 0);
    this.hull.castShadow = true;
    this.hull.receiveShadow = true;
    this.hull.name = 'ship_hull';
    this.group.add(this.hull);
  }
  
  /**
   * Create hull geometry (simplified ship shape)
   */
  createHullGeometry(length, width, height) {
    const shape = new THREE.Shape();
    
    // Create ship profile (simplified)
    const bowCurve = width * 0.3;
    const sternCurve = width * 0.2;
    
    // Bottom profile
    shape.moveTo(-length / 2 + bowCurve, 0);
    shape.lineTo(length / 2 - sternCurve, 0);
    shape.quadraticCurveTo(length / 2, 0, length / 2, height * 0.3);
    shape.lineTo(length / 2, height);
    shape.lineTo(-length / 2, height);
    shape.lineTo(-length / 2, height * 0.3);
    shape.quadraticCurveTo(-length / 2, 0, -length / 2 + bowCurve, 0);
    
    // Extrude to create 3D hull
    const extrudeSettings = {
      depth: width,
      bevelEnabled: true,
      bevelThickness: 50,
      bevelSize: 50,
      bevelSegments: 3
    };
    
    const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
    geometry.center();
    
    return geometry;
  }
  
  /**
   * Create deck
   */
  createDeck() {
    const length = this.shipData.length_m * 1000;
    const width = this.shipData.width_m * 1000;
    
    const deckGeometry = new THREE.BoxGeometry(length, 100, width);
    const deckMaterial = new THREE.MeshStandardMaterial({
      color: this.options.deckColor,
      roughness: 0.7,
      metalness: 0.3
    });
    
    this.deck = new THREE.Mesh(deckGeometry, deckMaterial);
    this.deck.position.set(0, 50, 0);
    this.deck.castShadow = true;
    this.deck.receiveShadow = true;
    this.deck.name = 'ship_deck';
    this.group.add(this.deck);
  }
  
  /**
   * Create superstructure (bridge)
   */
  createSuperstructure() {
    const length = this.shipData.length_m * 1000;
    const width = this.shipData.width_m * 1000;
    
    // Bridge structure
    const bridgeWidth = width * 0.7;
    const bridgeLength = length * 0.15;
    const bridgeHeight = 2000;
    
    const bridgeGeometry = new THREE.BoxGeometry(
      bridgeLength,
      bridgeHeight,
      bridgeWidth
    );
    
    const bridgeMaterial = new THREE.MeshPhongMaterial({
      color: 0xecf0f1,
      shininess: 30
    });
    
    this.superstructure = new THREE.Mesh(bridgeGeometry, bridgeMaterial);
    this.superstructure.position.set(
      length * 0.35,  // Toward stern
      100 + bridgeHeight / 2,
      0
    );
    this.superstructure.castShadow = true;
    this.superstructure.name = 'ship_superstructure';
    this.group.add(this.superstructure);
    
    // Add funnel (chimney)
    this.createFunnel();
  }
  
  /**
   * Create funnel
   */
  createFunnel() {
    const funnelGeometry = new THREE.CylinderGeometry(200, 300, 1000, 8);
    const funnelMaterial = new THREE.MeshPhongMaterial({
      color: 0xe74c3c
    });
    
    const funnel = new THREE.Mesh(funnelGeometry, funnelMaterial);
    funnel.position.copy(this.superstructure.position);
    funnel.position.y += 1500;
    funnel.castShadow = true;
    funnel.name = 'ship_funnel';
    this.group.add(funnel);
  }
  
  /**
   * Create stowage grid
   */
  createStowageGrid() {
    const { bays, rows } = this.shipData;
    const length = this.shipData.length_m * 1000;
    const width = this.shipData.width_m * 1000;
    
    // Container dimensions (standard 20ft)
    const containerLength = 6058; // 20ft with spacing
    const containerWidth = 2438;
    
    // Grid lines
    const gridMaterial = new THREE.LineBasicMaterial({
      color: 0x95a5a6,
      opacity: 0.5,
      transparent: true
    });
    
    // Bay lines (longitudinal)
    for (let i = 0; i <= bays; i++) {
      const x = -length / 2 + (i * containerLength);
      
      const points = [
        new THREE.Vector3(x, 150, -width / 2),
        new THREE.Vector3(x, 150, width / 2)
      ];
      
      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      const line = new THREE.Line(geometry, gridMaterial);
      line.name = `bay_line_${i}`;
      this.group.add(line);
    }
    
    // Row lines (transverse)
    for (let i = 0; i <= rows; i++) {
      const z = -width / 2 + (i * containerWidth);
      
      const points = [
        new THREE.Vector3(-length / 2, 150, z),
        new THREE.Vector3(length / 2, 150, z)
      ];
      
      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      const line = new THREE.Line(geometry, gridMaterial);
      line.name = `row_line_${i}`;
      this.group.add(line);
    }
  }
  
  /**
   * Add container to ship
   */
  addContainer(containerData, position) {
    const { bay, row, tier, is_above_deck } = position;
    
    // Calculate 3D position
    const pos = this.calculateContainerPosition(bay, row, tier, is_above_deck);
    
    // Create container mesh
    const containerMesh = this.createContainerMesh(containerData, pos);
    
    if (containerMesh) {
      this.containers.push({
        data: containerData,
        position: position,
        mesh: containerMesh
      });
      
      const key = `${bay}-${row}-${tier}-${is_above_deck ? 'above' : 'below'}`;
      this.containerMeshes.set(key, containerMesh);
      this.group.add(containerMesh);
    }
    
    return containerMesh;
  }
  
  /**
   * Calculate container 3D position from bay/row/tier
   */
  calculateContainerPosition(bay, row, tier, isAboveDeck) {
    const length = this.shipData.length_m * 1000;
    const width = this.shipData.width_m * 1000;
    
    // Standard container dimensions
    const containerLength = 6058;
    const containerWidth = 2438;
    const containerHeight = 2591;
    
    const x = -length / 2 + (bay * containerLength) + containerLength / 2;
    const z = -width / 2 + (row * containerWidth) + containerWidth / 2;
    
    let y;
    if (isAboveDeck) {
      y = 100 + (tier * containerHeight) + containerHeight / 2;
    } else {
      y = 100 - ((tier + 1) * containerHeight) + containerHeight / 2;
    }
    
    return { x, y, z };
  }
  
  /**
   * Create container mesh
   */
  createContainerMesh(containerData, position) {
    // Standard 20ft container dimensions
    const length = 6058;
    const width = 2438;
    const height = 2591;
    
    const geometry = new THREE.BoxGeometry(length, height, width);
    
    // Color based on container type or random
    const color = this.getContainerColor(containerData);
    
    const material = new THREE.MeshPhongMaterial({
      color: color,
      shininess: 50
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(position.x, position.y, position.z);
    
    // Add edges
    const edges = new THREE.EdgesGeometry(geometry);
    const edgeMaterial = new THREE.LineBasicMaterial({ color: 0x000000 });
    const wireframe = new THREE.LineSegments(edges, edgeMaterial);
    mesh.add(wireframe);
    
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    
    mesh.userData = {
      containerData,
      type: 'container'
    };
    
    mesh.name = `container_${containerData.container_id || 'unknown'}`;
    
    return mesh;
  }
  
  /**
   * Get container color
   */
  getContainerColor(containerData) {
    if (containerData.color) {
      return new THREE.Color(containerData.color);
    }
    
    // Color by type
    const colors = {
      refrigerated: 0x3498db,
      hazardous: 0xe74c3c,
      standard: 0x2ecc71,
      open_top: 0xf39c12
    };
    
    const type = containerData.container_type || 'standard';
    return colors[type] || colors.standard;
  }
  
  /**
   * Remove container
   */
  removeContainer(bay, row, tier, isAboveDeck) {
    const key = `${bay}-${row}-${tier}-${isAboveDeck ? 'above' : 'below'}`;
    const mesh = this.containerMeshes.get(key);
    
    if (mesh) {
      this.group.remove(mesh);
      this.disposeMesh(mesh);
      this.containerMeshes.delete(key);
      
      this.containers = this.containers.filter(c => {
        const pos = c.position;
        return !(pos.bay === bay && pos.row === row && 
                pos.tier === tier && pos.is_above_deck === isAboveDeck);
      });
    }
  }
  
  /**
   * Clear all containers
   */
  clearContainers() {
    this.containerMeshes.forEach((mesh) => {
      this.group.remove(mesh);
      this.disposeMesh(mesh);
    });
    
    this.containers = [];
    this.containerMeshes.clear();
  }
  
  /**
   * Load stowage plan
   */
  loadStowagePlan(stowagePlan) {
    this.clearContainers();
    
    if (stowagePlan.positions) {
      stowagePlan.positions.forEach(position => {
        const containerData = {
          container_id: position.container_id,
          weight_kg: position.weight_kg,
          is_reefer: position.is_reefer,
          hazard_class: position.hazard_class
        };
        
        this.addContainer(containerData, position);
      });
    }
  }
  
  /**
   * Highlight container
   */
  highlightContainer(bay, row, tier, isAboveDeck, highlight = true) {
    const key = `${bay}-${row}-${tier}-${isAboveDeck ? 'above' : 'below'}`;
    const mesh = this.containerMeshes.get(key);
    
    if (mesh) {
      if (highlight) {
        mesh.material.emissive = new THREE.Color(0xffff00);
        mesh.material.emissiveIntensity = 0.5;
      } else {
        mesh.material.emissive = new THREE.Color(0x000000);
        mesh.material.emissiveIntensity = 0;
      }
    }
  }
  
  /**
   * Get ship statistics
   */
  getStatistics() {
    const totalSlots = this.shipData.bays * 
                      this.shipData.rows * 
                      (this.shipData.tiers_above_deck + this.shipData.tiers_below_deck);
    
    const occupiedSlots = this.containers.length;
    const utilization = (occupiedSlots / totalSlots) * 100;
    
    const totalWeight = this.containers.reduce((sum, c) => 
      sum + (c.data.weight_kg || 0), 0
    );
    
    const reefers = this.containers.filter(c => c.data.is_reefer).length;
    const hazmat = this.containers.filter(c => c.data.hazard_class).length;
    
    return {
      totalSlots,
      occupiedSlots,
      emptySlots: totalSlots - occupiedSlots,
      utilization: utilization.toFixed(1),
      totalWeight,
      reefers,
      hazmat,
      containerCount: this.containers.length
    };
  }
  
  /**
   * Get group
   */
  getGroup() {
    return this.group;
  }
  
  /**
   * Get bounding box
   */
  getBoundingBox() {
    return new THREE.Box3().setFromObject(this.group);
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
    
    mesh.children.forEach(child => {
      this.disposeMesh(child);
    });
  }
  
  /**
   * Dispose ship
   */
  dispose() {
    this.clearContainers();
    
    if (this.hull) this.disposeMesh(this.hull);
    if (this.deck) this.disposeMesh(this.deck);
    if (this.superstructure) this.disposeMesh(this.superstructure);
    
    this.group.clear();
  }
}

/**
 * Ship type presets
 */
export const ShipPresets = {
  feeder: {
    name: 'Feeder',
    length_m: 135,
    width_m: 23,
    draft_m: 8,
    teu_capacity: 1000,
    bays: 12,
    rows: 6,
    tiers_above_deck: 3,
    tiers_below_deck: 4
  },
  panamax: {
    name: 'Panamax',
    length_m: 294,
    width_m: 32,
    draft_m: 12,
    teu_capacity: 5000,
    bays: 20,
    rows: 13,
    tiers_above_deck: 6,
    tiers_below_deck: 8
  },
  post_panamax: {
    name: 'Post-Panamax',
    length_m: 366,
    width_m: 48,
    draft_m: 15,
    teu_capacity: 12000,
    bays: 24,
    rows: 22,
    tiers_above_deck: 8,
    tiers_below_deck: 10
  }
};