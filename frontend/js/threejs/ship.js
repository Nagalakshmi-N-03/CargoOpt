import * as THREE from 'three';

export class Ship {
    constructor(scene) {
        this.scene = scene;
        this.vehicles = new Map(); // vehicleId -> THREE.Group
        this.vehicleMeshes = new Map(); // vehicleId -> THREE.Mesh
        this.animations = new Map();
        this.isAnimating = false;

        this.materials = this.createMaterials();
        this.createDockArea();
    }

    createMaterials() {
        return {
            standard: new THREE.MeshStandardMaterial({
                color: 0x2F4F4F,
                metalness: 0.4,
                roughness: 0.6
            }),
            selected: new THREE.MeshStandardMaterial({
                color: 0xFFA500,
                metalness: 0.5,
                roughness: 0.3,
                emissive: 0x332200
            }),
            highlighted: new THREE.MeshStandardMaterial({
                color: 0x98FB98,
                metalness: 0.3,
                roughness: 0.5,
                emissive: 0x003300
            }),
            truck: new THREE.MeshStandardMaterial({
                color: 0x8B4513,
                metalness: 0.2,
                roughness: 0.8
            }),
            van: new THREE.MeshStandardMaterial({
                color: 0x4169E1,
                metalness: 0.3,
                roughness: 0.6
            })
        };
    }

    createDockArea() {
        // Create dock platform
        const dockGeometry = new THREE.PlaneGeometry(30, 30);
        const dockMaterial = new THREE.MeshStandardMaterial({ 
            color: 0x696969,
            roughness: 0.8,
            metalness: 0.2
        });
        const dock = new THREE.Mesh(dockGeometry, dockMaterial);
        dock.rotation.x = -Math.PI / 2;
        dock.position.y = -0.05;
        dock.receiveShadow = true;
        this.scene.add(dock);

        // Add dock markings
        this.addDockMarkings();
    }

    addDockMarkings() {
        // Add parking lines
        const lineGeometry = new THREE.PlaneGeometry(0.2, 4);
        const lineMaterial = new THREE.MeshBasicMaterial({ color: 0xFFFFFF });
        
        for (let i = -3; i <= 3; i++) {
            const line = new THREE.Mesh(lineGeometry, lineMaterial);
            line.rotation.x = -Math.PI / 2;
            line.position.set(i * 4, -0.04, 0);
            this.scene.add(line);
        }

        // Add safety boundaries
        const boundaryGeometry = new THREE.BoxGeometry(32, 0.1, 0.5);
        const boundaryMaterial = new THREE.MeshBasicMaterial({ color: 0xFF0000 });
        
        const leftBoundary = new THREE.Mesh(boundaryGeometry, boundaryMaterial);
        leftBoundary.position.set(0, 0, -15);
        this.scene.add(leftBoundary);
        
        const rightBoundary = new THREE.Mesh(boundaryGeometry, boundaryMaterial);
        rightBoundary.position.set(0, 0, 15);
        this.scene.add(rightBoundary);
    }

    createVehicle(vehicleData) {
        const { id, type, max_weight, length, width, height } = vehicleData;
        
        const vehicleGroup = new THREE.Group();
        vehicleGroup.userData = {
            isVehicle: true,
            vehicleId: id,
            type: type,
            maxWeight: max_weight,
            dimensions: { length, width, height },
            currentLoad: 0
        };

        // Choose material based on vehicle type
        let material = this.materials.standard;
        if (type.includes('truck')) {
            material = this.materials.truck;
        } else if (type.includes('van')) {
            material = this.materials.van;
        }

        // Create vehicle body
        const bodyGeometry = new THREE.BoxGeometry(length, height * 0.3, width);
        const body = new THREE.Mesh(bodyGeometry, material);
        body.position.y = height * 0.15;
        body.castShadow = true;
        body.receiveShadow = true;

        // Create cargo area
        const cargoGeometry = new THREE.BoxGeometry(length * 0.9, height * 0.6, width * 0.9);
        const cargoMaterial = new THREE.MeshStandardMaterial({
            color: 0xD3D3D3,
            transparent: true,
            opacity: 0.7,
            wireframe: false
        });
        const cargoArea = new THREE.Mesh(cargoGeometry, cargoMaterial);
        cargoArea.position.y = height * 0.6;
        cargoArea.castShadow = true;

        // Add wheels
        this.addWheels(vehicleGroup, length, width, height);

        // Add cabin for trucks
        if (type.includes('truck')) {
            this.addCabin(vehicleGroup, length, width, height);
        }

        vehicleGroup.add(body);
        vehicleGroup.add(cargoArea);

        this.vehicles.set(id, vehicleGroup);
        this.vehicleMeshes.set(id, body);
        this.scene.add(vehicleGroup);

        return vehicleGroup;
    }

    addWheels(vehicleGroup, length, width, height) {
        const wheelGeometry = new THREE.CylinderGeometry(0.3, 0.3, 0.2, 8);
        const wheelMaterial = new THREE.MeshStandardMaterial({ color: 0x000000 });
        
        const wheelPositions = [
            { x: length * 0.3, z: width * 0.4 },
            { x: length * 0.3, z: -width * 0.4 },
            { x: -length * 0.3, z: width * 0.4 },
            { x: -length * 0.3, z: -width * 0.4 }
        ];

        wheelPositions.forEach(pos => {
            const wheel = new THREE.Mesh(wheelGeometry, wheelMaterial);
            wheel.rotation.z = Math.PI / 2;
            wheel.position.set(pos.x, 0.1, pos.z);
            vehicleGroup.add(wheel);
        });
    }

    addCabin(vehicleGroup, length, width, height) {
        const cabinGeometry = new THREE.BoxGeometry(length * 0.4, height * 0.5, width);
        const cabinMaterial = new THREE.MeshStandardMaterial({ color: 0x1E90FF });
        const cabin = new THREE.Mesh(cabinGeometry, cabinMaterial);
        cabin.position.set(length * 0.3, height * 0.5, 0);
        cabin.castShadow = true;
        vehicleGroup.add(cabin);
    }

    loadVehicles(vehiclesData) {
        vehiclesData.forEach((vehicleData, index) => {
            const vehicle = this.createVehicle(vehicleData);
            
            // Position vehicles in a row
            const x = index * 8 - (vehiclesData.length - 1) * 4;
            vehicle.position.set(x, 0, 0);
            vehicle.userData.originalPosition = vehicle.position.clone();
        });
    }

    highlightVehicle(vehicleId) {
        this.removeAllHighlights();
        
        const mesh = this.vehicleMeshes.get(vehicleId);
        if (mesh) {
            mesh.material = this.materials.highlighted;
        }
    }

    removeAllHighlights() {
        this.vehicleMeshes.forEach((mesh, vehicleId) => {
            if (mesh.material !== this.materials.selected) {
                this.resetVehicleMaterial(vehicleId);
            }
        });
    }

    selectVehicle(vehicleId) {
        const vehicle = this.vehicles.get(vehicleId);
        if (vehicle) {
            const mesh = this.vehicleMeshes.get(vehicleId);
            if (mesh) {
                mesh.material = this.materials.selected;
            }
            
            this.startSelectionAnimation(vehicleId);
            return vehicle;
        }
        return null;
    }

    deselectVehicle(vehicleId) {
        const mesh = this.vehicleMeshes.get(vehicleId);
        if (mesh) {
            this.resetVehicleMaterial(vehicleId);
        }
        
        this.stopSelectionAnimation(vehicleId);
    }

    resetVehicleMaterial(vehicleId) {
        const mesh = this.vehicleMeshes.get(vehicleId);
        const vehicle = this.vehicles.get(vehicleId);
        
        if (mesh && vehicle) {
            if (vehicle.userData.type.includes('truck')) {
                mesh.material = this.materials.truck;
            } else if (vehicle.userData.type.includes('van')) {
                mesh.material = this.materials.van;
            } else {
                mesh.material = this.materials.standard;
            }
        }
    }

    startSelectionAnimation(vehicleId) {
        const vehicle = this.vehicles.get(vehicleId);
        if (vehicle) {
            this.animations.set(vehicleId, {
                startTime: performance.now(),
                originalY: vehicle.position.y
            });
        }
    }

    stopSelectionAnimation(vehicleId) {
        const vehicle = this.vehicles.get(vehicleId);
        if (vehicle) {
            vehicle.position.y = vehicle.userData.originalPosition.y;
            this.animations.delete(vehicleId);
        }
    }

    updateLoad(vehicleId, currentLoad) {
        const vehicle = this.vehicles.get(vehicleId);
        if (vehicle) {
            vehicle.userData.currentLoad = currentLoad;
            
            // Visual feedback for load level
            const loadPercentage = currentLoad / vehicle.userData.maxWeight;
            this.updateVehicleAppearance(vehicleId, loadPercentage);
        }
    }

    updateVehicleAppearance(vehicleId, loadPercentage) {
        const vehicle = this.vehicles.get(vehicleId);
        if (vehicle) {
            // Change color based on load (green -> yellow -> red)
            const body = this.vehicleMeshes.get(vehicleId);
            if (body) {
                if (loadPercentage < 0.7) {
                    body.material.color.setHex(0x00FF00); // Green
                } else if (loadPercentage < 0.9) {
                    body.material.color.setHex(0xFFFF00); // Yellow
                } else {
                    body.material.color.setHex(0xFF0000); // Red
                }
            }
            
            // Add suspension compression effect
            const compression = loadPercentage * 0.1;
            vehicle.position.y = vehicle.userData.originalPosition.y - compression;
        }
    }

    startLoadingAnimation(vehicleId, containers) {
        // Simulate loading process with animations
        const vehicle = this.vehicles.get(vehicleId);
        if (vehicle) {
            this.animations.set(vehicleId, {
                type: 'loading',
                startTime: performance.now(),
                containers: containers,
                currentContainerIndex: 0
            });
        }
    }

    update() {
        if (!this.isAnimating) return;

        const currentTime = performance.now();
        
        this.animations.forEach((animation, vehicleId) => {
            const vehicle = this.vehicles.get(vehicleId);
            if (!vehicle) return;

            if (animation.type === 'loading') {
                this.updateLoadingAnimation(vehicle, animation, currentTime);
            } else {
                this.updateSelectionAnimation(vehicle, animation, currentTime);
            }
        });
    }

    updateSelectionAnimation(vehicle, animation, currentTime) {
        const elapsed = (currentTime - animation.startTime) / 1000;
        const bounceHeight = 0.1;
        const bounceSpeed = 3;
        
        const bounce = Math.sin(elapsed * bounceSpeed) * bounceHeight;
        vehicle.position.y = animation.originalY + bounce;
    }

    updateLoadingAnimation(vehicle, animation, currentTime) {
        // Simulate sequential container loading
        // This would be coordinated with the ContainerManager
    }

    toggleAnimation() {
        this.isAnimating = !this.isAnimating;
    }

    clearAllVehicles() {
        this.vehicles.forEach(vehicle => {
            this.scene.remove(vehicle);
        });
        this.vehicles.clear();
        this.vehicleMeshes.clear();
        this.animations.clear();
    }

    getVehicleInfo(vehicleId) {
        const vehicle = this.vehicles.get(vehicleId);
        return vehicle ? vehicle.userData : null;
    }

    getAllVehicles() {
        return Array.from(this.vehicles.values());
    }

    dispose() {
        this.clearAllVehicles();
        
        // Dispose materials
        Object.values(this.materials).forEach(material => material.dispose());
    }
}