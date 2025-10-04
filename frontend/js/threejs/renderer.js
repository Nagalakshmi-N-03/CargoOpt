import * as THREE from 'three';

export class Renderer {
    constructor(container) {
        this.container = container;
        this.renderer = this.createRenderer();
        this.container.appendChild(this.renderer.domElement);
    }

    createRenderer() {
        const renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true
        });
        
        renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.outputEncoding = THREE.sRGBEncoding;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1;
        
        // Enable physics-based rendering
        renderer.physicallyCorrectLights = true;
        
        return renderer;
    }

    setSize(width, height) {
        this.renderer.setSize(width, height);
    }

    render(scene, camera) {
        this.renderer.render(scene, camera);
    }

    setClearColor(color, alpha = 1) {
        this.renderer.setClearColor(color, alpha);
    }

    enableShadows(enable = true) {
        this.renderer.shadowMap.enabled = enable;
    }

    setShadowMapType(type) {
        const shadowTypes = {
            'basic': THREE.BasicShadowMap,
            'pcf': THREE.PCFShadowMap,
            'pcfsoft': THREE.PCFSoftShadowMap
        };
        this.renderer.shadowMap.type = shadowTypes[type] || THREE.PCFSoftShadowMap;
    }

    setToneMapping(mapping) {
        const toneMappings = {
            'none': THREE.NoToneMapping,
            'linear': THREE.LinearToneMapping,
            'reinhard': THREE.ReinhardToneMapping,
            'cineon': THREE.CineonToneMapping,
            'aces': THREE.ACESFilmicToneMapping
        };
        this.renderer.toneMapping = toneMappings[mapping] || THREE.ACESFilmicToneMapping;
    }

    setToneMappingExposure(exposure) {
        this.renderer.toneMappingExposure = exposure;
    }

    takeScreenshot(filename = 'cargoopt-screenshot.png') {
        this.renderer.render(); // Ensure scene is rendered
        const link = document.createElement('a');
        link.download = filename;
        link.href = this.renderer.domElement.toDataURL();
        link.click();
    }

    enableVR() {
        // VR capabilities can be added here
        console.log('VR support can be implemented with WebXR');
    }

    enableAR() {
        // AR capabilities can be added here
        console.log('AR support can be implemented with WebXR');
    }

    setBackground(colorOrTexture) {
        if (colorOrTexture instanceof THREE.Texture) {
            this.scene.background = colorOrTexture;
        } else {
            this.scene.background = new THREE.Color(colorOrTexture);
        }
    }

    addPostProcessing() {
        // Post-processing effects can be added here
        console.log('Post-processing effects can be implemented');
    }

    dispose() {
        this.renderer.dispose();
        if (this.container.contains(this.renderer.domElement)) {
            this.container.removeChild(this.renderer.domElement);
        }
    }
}