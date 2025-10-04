import * as THREE from 'three';
import { Renderer } from './renderer.js';
import { ContainerManager } from './container.js';
import { Ship } from './ship.js';

export class CargoScene {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = new THREE.Scene();
        this.camera = null;
        this.renderer = new Renderer(this.container);
        this.containerManager = new ContainerManager(this.scene);
        this.ship = new Ship(this.scene);
        
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.selectedObject = null;
        
        this.init();
        this.setupEventListeners();
    }

    init() {
        // Setup camera
        this.camera = new THREE.PerspectiveCamera(
            75,
            this.container.clientWidth / this.container.clientHeight,
            0.1,
            1000
        );
        this.camera.position.set(15, 10, 15);
        this.camera.lookAt(0, 0, 0);

        // Setup lighting
        this.setupLighting();

        // Add coordinate helpers
        this.addHelpers();

        // Add ground plane
        this.addGround();

        // Start animation loop
        this.animate();
    }

    setupLighting() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);

        // Directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 20, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);

        // Hemisphere light for natural outdoor lighting
        const hemisphereLight = new THREE.HemisphereLight(0xffffbb, 0x080820, 0.4);
        this.scene.add(hemisphereLight);
    }

    addHelpers() {
        // Axes helper
        const axesHelper = new THREE.AxesHelper(5);
        this.scene.add(axesHelper);

        // Grid helper
        const gridHelper = new THREE.GridHelper(20, 20, 0x444444, 0x222222);
        gridHelper.position.y = -0.1;
        this.scene.add(gridHelper);
    }

    addGround() {
        const groundGeometry = new THREE.PlaneGeometry(40, 40);
        const groundMaterial = new THREE.MeshLambertMaterial({ 
            color: 0x3a3a3a,
            side: THREE.DoubleSide 
        });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = Math.PI / 2;
        ground.position.y = -0.1;
        ground.receiveShadow = true;
        this.scene.add(ground);
    }

    setupEventListeners() {
        // Window resize
        window.addEventListener('resize', () => this.onWindowResize());

        // Mouse events for interaction
        this.container.addEventListener('mousemove', (event) => this.onMouseMove(event));
        this.container.addEventListener('click', (event) => this.onMouseClick(event));
        this.container.addEventListener('dblclick', (event) => this.onDoubleClick(event));

        // Keyboard controls
        document.addEventListener('keydown', (event) => this.onKeyDown(event));
    }

    onWindowResize() {
        this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    }

    onMouseMove(event) {
        const rect = this.container.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / this.container.clientWidth) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / this.container.clientHeight) * 2 + 1;

        // Update raycaster
        this.raycaster.setFromCamera(this.mouse, this.camera);
        
        // Highlight hovered objects
        const intersects = this.raycaster.intersectObjects(this.scene.children, true);
        
        // Remove highlight from all containers
        this.containerManager.removeAllHighlights();
        
        if (intersects.length > 0) {
            const object = intersects[0].object;
            const container = this.findParentContainer(object);
            if (container) {
                this.containerManager.highlightContainer(container.userData.containerId);
            }
        }
    }

    onMouseClick(event) {
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.scene.children, true);

        if (intersects.length > 0) {
            const object = intersects[0].object;
            const container = this.findParentContainer(object);
            
            if (container) {
                this.selectContainer(container.userData.containerId);
                
                // Dispatch custom event
                const containerSelectedEvent = new CustomEvent('containerSelected', {
                    detail: {
                        containerId: container.userData.containerId,
                        containerData: container.userData
                    }
                });
                document.dispatchEvent(containerSelectedEvent);
            }
        } else {
            this.deselectContainer();
        }
    }

    onDoubleClick(event) {
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.scene.children, true);

        if (intersects.length > 0) {
            const object = intersects[0].object;
            const container = this.findParentContainer(object);
            
            if (container) {
                // Focus camera on container
                this.focusOnObject(container);
                
                // Dispatch custom event
                const containerFocusedEvent = new CustomEvent('containerFocused', {
                    detail: {
                        containerId: container.userData.containerId
                    }
                });
                document.dispatchEvent(containerFocusedEvent);
            }
        }
    }

    onKeyDown(event) {
        switch(event.key) {
            case 'r':
            case 'R':
                // Reset camera
                this.resetCamera();
                break;
            case ' ':
                // Toggle animation
                this.toggleAnimation();
                break;
            case 'h':
            case 'H':
                // Toggle helpers
                this.toggleHelpers();
                break;
        }
    }

    findParentContainer(object) {
        let current = object;
        while (current !== null) {
            if (current.userData && current.userData.isContainer) {
                return current;
            }
            current = current.parent;
        }
        return null;
    }

    selectContainer(containerId) {
        this.deselectContainer();
        this.selectedObject = this.containerManager.selectContainer(containerId);
    }

    deselectContainer() {
        if (this.selectedObject) {
            this.containerManager.deselectContainer(this.selectedObject.userData.containerId);
            this.selectedObject = null;
        }
    }

    focusOnObject(object) {
        const box = new THREE.Box3().setFromObject(object);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        
        const maxDim = Math.max(size.x, size.y, size.z);
        const fov = this.camera.fov * (Math.PI / 180);
        let cameraDistance = maxDim / (2 * Math.tan(fov / 2));
        
        cameraDistance *= 1.5; // Add some padding
        
        const direction = new THREE.Vector3()
            .subVectors(this.camera.position, center)
            .normalize();
        
        this.camera.position.copy(center).add(direction.multiplyScalar(cameraDistance));
        this.camera.lookAt(center);
    }

    resetCamera() {
        this.camera.position.set(15, 10, 15);
        this.camera.lookAt(0, 0, 0);
    }

    toggleAnimation() {
        this.containerManager.toggleAnimation();
    }

    toggleHelpers() {
        const helpers = this.scene.children.filter(child => 
            child instanceof THREE.AxesHelper || child instanceof THREE.GridHelper
        );
        helpers.forEach(helper => {
            helper.visible = !helper.visible;
        });
    }

    loadOptimizationResult(optimizationResult) {
        // Clear existing containers
        this.containerManager.clearAllContainers();
        
        // Load ship based on vehicles
        const vehicles = optimizationResult.vehicles || [];
        this.ship.loadVehicles(vehicles);
        
        // Load container assignments
        const assignments = optimizationResult.assignments || {};
        this.containerManager.loadAssignments(assignments, optimizationResult.containers || []);
        
        // Update camera to show entire scene
        this.fitSceneToView();
    }

    fitSceneToView() {
        const bbox = new THREE.Box3().setFromObject(this.scene);
        const center = bbox.getCenter(new THREE.Vector3());
        const size = bbox.getSize(new THREE.Vector3());
        
        const maxDim = Math.max(size.x, size.y, size.z);
        const fov = this.camera.fov * (Math.PI / 180);
        let cameraDistance = Math.abs(maxDim / Math.sin(fov / 2));
        
        cameraDistance *= 1.2; // Add padding
        
        this.camera.position.copy(center);
        this.camera.position.x += cameraDistance;
        this.camera.position.y += cameraDistance * 0.5;
        this.camera.position.z += cameraDistance;
        this.camera.lookAt(center);
    }

    highlightVehicle(vehicleId) {
        this.ship.highlightVehicle(vehicleId);
    }

    highlightContainer(containerId) {
        this.containerManager.highlightContainer(containerId);
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Update container animations
        this.containerManager.update();
        
        // Update ship animations
        this.ship.update();
        
        // Render scene
        this.renderer.render(this.scene, this.camera);
    }

    dispose() {
        this.renderer.dispose();
        this.containerManager.dispose();
        this.ship.dispose();
        
        // Remove event listeners
        window.removeEventListener('resize', this.onWindowResize);
        // ... remove other event listeners
    }
}