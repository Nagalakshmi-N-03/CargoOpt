import * as THREE from 'three';

export class ContainerManager {
    constructor(scene) {
        this.scene = scene;
        this.containers = new Map(); // containerId -> THREE.Group
        this.containerMeshes = new Map(); // containerId -> THREE.Mesh
        this.animations = new Map(); // containerId -> animation data
        this.isAnimating = false;
        this.animationSpeed = 2.0;
        
        this.materials = this.createMaterials();
    }

    createMaterials() {
        return {
            standard: new THREE.MeshStandardMaterial({ 
                color: 0x4682B4,
                metalness: 0.3,
                roughness: 0.7
            }),
            selected: new THREE.MeshStandardMaterial({
                color: 0xFFD700,
                metalness: 0.5,
                roughness: 0.3,
                emissive: 0x333300
            }),
            highlighted: new THREE.MeshStandardMaterial({
                color: 0x90EE90,
                metalness: 0.3,
                roughness: 0.6,
                emissive: 0x003300
            }),
            hazardous: new THREE.MeshStandardMaterial({
                color: 0xFF4500,
                metalness: 0.2,
                roughness: 0.8,
                emissive: 0x330000
            }),
            refrigerated: new THREE.MeshStandardMaterial({
                color: 0x87CEEB,
                metalness: 0.4,
                roughness: 0.5
            })
        };
    }

    createContainer(containerData) {
        const { id, name, length, width, height, weight, type, hazardClass } = containerData;
        
        const containerGroup = new THREE.Group();
        containerGroup.userData = {
            isContainer: true,
            containerId: id,
            name: name,
            dimensions: { length, width, height },
            weight: weight,
            type: type,
            hazardClass: hazardClass,
            originalPosition: new THREE.Vector3()
        };

        // Choose material based on container properties
        let material = this.materials.standard;
        if (hazardClass) {
            material = this.materials.hazardous;
        } else if (type === 'refrigerated') {
            material = this.materials.refrigerated;
        }

        // Create container geometry
        const geometry = new THREE.BoxGeometry(length, height, width);
        const mesh = new THREE.Mesh(geometry, material);
        mesh.castShadow = true;
        mesh.receiveShadow = true;

        // Add wireframe for better visibility
        const wireframe = new THREE.WireframeGeometry(geometry);
        const line = new THREE.LineSegments(wireframe);
        line.material.color.set(0x000000);
        line.material.transparent = true;
        line.material.opacity = 0.3;

        containerGroup.add(mesh);
        containerGroup.add(line);

        // Add label
        this.addLabel(containerGroup, name, weight, height);

        this.containers.set(id, containerGroup);
        this.containerMeshes.set(id, mesh);
        this.scene.add(containerGroup);

        return containerGroup;
    }

    addLabel(containerGroup, name, weight, height) {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 256;
        canvas.height = 128;

        // Draw label background
        context.fillStyle = 'rgba(255, 255, 255, 0.9)';
        context.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw border
        context.strokeStyle = '#333';
        context.lineWidth = 2;
        context.strokeRect(0, 0, canvas.width, canvas.height);

        // Draw text
        context.fillStyle = '#333';
        context.font = 'bold 20px Arial';
        context.textAlign = 'center';
        context.fillText(name, canvas.width / 2, 30);
        
        context.font = '16px Arial';
        context.fillText(`${weight}kg`, canvas.width / 2, 60);
        
        context.font = '14px Arial';
        context.fillText('CargoOpt', canvas.width / 2, 90);

        const texture = new THREE.CanvasTexture(canvas);
        const labelMaterial = new THREE.SpriteMaterial({ 
            map: texture,
            transparent: true 
        });
        
        const sprite = new THREE.Sprite(labelMaterial);
        sprite.scale.set(3, 1.5, 1);
        sprite.position.y = height / 2 + 1; // Position above container
        containerGroup.add(sprite);
    }

    loadAssignments(assignments, containersData) {
        // First create all containers
        containersData.forEach(containerData => {
            this.createContainer(containerData);
        });

        // Position containers based on assignments
        let vehicleIndex = 0;
        Object.entries(assignments).forEach(([vehicleId, containerIds]) => {
            const vehicleContainers = containerIds.map(id => this.containers.get(id));
            
            // Simple grid layout for demonstration
            // In a real implementation, this would use actual 3D bin packing
            vehicleContainers.forEach((container, index) => {
                if (container) {
                    const row = Math.floor(index / 4);
                    const col = index % 4;
                    
                    const x = vehicleIndex * 8 + col * 2.5;
                    const z = row * 2.5;
                    const y = container.userData.dimensions.height / 2;
                    
                    container.position.set(x, y, z);
                    container.userData.originalPosition.copy(container.position);
                    
                    // Store vehicle assignment
                    container.userData.assignedVehicle = vehicleId;
                }
            });
            
            vehicleIndex++;
        });
    }

    highlightContainer(containerId) {
        this.removeAllHighlights();
        
        const mesh = this.containerMeshes.get(containerId);
        if (mesh) {
            mesh.material = this.materials.highlighted;
        }
    }

    removeAllHighlights() {
        this.containerMeshes.forEach((mesh, containerId) => {
            if (mesh.material !== this.materials.selected) {
                this.resetContainerMaterial(containerId);
            }
        });
    }

    selectContainer(containerId) {
        const container = this.containers.get(containerId);
        if (container) {
            const mesh = this.containerMeshes.get(containerId);
            if (mesh) {
                mesh.material = this.materials.selected;
            }
            
            // Add selection animation
            this.startSelectionAnimation(containerId);
            
            return container;
        }
        return null;
    }

    deselectContainer(containerId) {
        const mesh = this.containerMeshes.get(containerId);
        if (mesh) {
            this.resetContainerMaterial(containerId);
        }
        
        // Stop selection animation
        this.stopSelectionAnimation(containerId);
    }

    resetContainerMaterial(containerId) {
        const mesh = this.containerMeshes.get(containerId);
        const container = this.containers.get(containerId);
        
        if (mesh && container) {
            if (container.userData.hazardClass) {
                mesh.material = this.materials.hazardous;
            } else if (container.userData.type === 'refrigerated') {
                mesh.material = this.materials.refrigerated;
            } else {
                mesh.material = this.materials.standard;
            }
        }
    }

    startSelectionAnimation(containerId) {
        const container = this.containers.get(containerId);
        if (container) {
            this.animations.set(containerId, {
                startTime: performance.now(),
                originalY: container.position.y
            });
        }
    }

    stopSelectionAnimation(containerId) {
        const container = this.containers.get(containerId);
        if (container) {
            container.position.y = container.userData.originalPosition.y;
            this.animations.delete(containerId);
        }
    }

    startLoadingAnimation(containerId, targetPosition, duration = 2000) {
        const container = this.containers.get(containerId);
        if (container) {
            this.animations.set(containerId, {
                type: 'loading',
                startTime: performance.now(),
                duration: duration,
                startPosition: container.position.clone(),
                targetPosition: targetPosition.clone()
            });
        }
    }

    update() {
        if (!this.isAnimating) return;

        const currentTime = performance.now();
        
        this.animations.forEach((animation, containerId) => {
            const container = this.containers.get(containerId);
            if (!container) return;

            if (animation.type === 'loading') {
                this.updateLoadingAnimation(container, animation, currentTime);
            } else {
                this.updateSelectionAnimation(container, animation, currentTime);
            }
        });
    }

    updateSelectionAnimation(container, animation, currentTime) {
        const elapsed = (currentTime - animation.startTime) / 1000;
        const bounceHeight = 0.3;
        const bounceSpeed = 5;
        
        const bounce = Math.sin(elapsed * bounceSpeed) * bounceHeight;
        container.position.y = animation.originalY + bounce;
    }

    updateLoadingAnimation(container, animation, currentTime) {
        const elapsed = currentTime - animation.startTime;
        const progress = Math.min(elapsed / animation.duration, 1);
        
        // Smooth step interpolation
        const smoothProgress = progress * progress * (3 - 2 * progress);
        
        container.position.lerpVectors(
            animation.startPosition,
            animation.targetPosition,
            smoothProgress
        );
        
        if (progress === 1) {
            this.animations.delete(container.userData.containerId);
        }
    }

    toggleAnimation() {
        this.isAnimating = !this.isAnimating;
    }

    clearAllContainers() {
        this.containers.forEach(container => {
            this.scene.remove(container);
        });
        this.containers.clear();
        this.containerMeshes.clear();
        this.animations.clear();
    }

    getContainerInfo(containerId) {
        const container = this.containers.get(containerId);
        return container ? container.userData : null;
    }

    getAllContainers() {
        return Array.from(this.containers.values());
    }

    getContainersByVehicle(vehicleId) {
        return Array.from(this.containers.values()).filter(
            container => container.userData.assignedVehicle === vehicleId
        );
    }

    dispose() {
        this.clearAllContainers();
        
        // Dispose materials
        Object.values(this.materials).forEach(material => material.dispose());
    }
}