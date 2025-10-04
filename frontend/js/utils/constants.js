// Application constants and configuration
const Constants = {
    // API Configuration
    API: {
        BASE_URL: 'http://localhost:5000/api/v1',
        TIMEOUT: 30000,
        RETRY_ATTEMPTS: 3,
        RETRY_DELAY: 1000
    },

    // Algorithm Types
    ALGORITHMS: {
        AUTO: 'auto',
        PACKING: 'packing',
        GENETIC: 'genetic',
        STOWAGE: 'stowage'
    },

    // Algorithm Display Names
    ALGORITHM_NAMES: {
        auto: 'Auto Select',
        packing: 'Basic Packing',
        genetic: 'Genetic Algorithm',
        stowage: 'Multi-Container Stowage'
    },

    // Algorithm Descriptions
    ALGORITHM_DESCRIPTIONS: {
        auto: 'Automatically selects the best algorithm based on problem characteristics',
        packing: 'Fast first-fit decreasing algorithm for simple packing scenarios',
        genetic: 'Evolutionary algorithm for complex optimization problems',
        stowage: 'Optimizes cargo distribution across multiple containers'
    },

    // Optimization Strategies
    STRATEGIES: {
        BALANCED: 'balanced',
        SPACE_FIRST: 'space_first',
        WEIGHT_FIRST: 'weight_first',
        STABILITY_FIRST: 'stability_first'
    },

    STRATEGY_NAMES: {
        balanced: 'Balanced',
        space_first: 'Space First',
        weight_first: 'Weight First',
        stability_first: 'Stability First'
    },

    // Container Types
    CONTAINER_TYPES: {
        STANDARD_20FT: 'standard_20ft',
        STANDARD_40FT: 'standard_40ft',
        HIGH_CUBE_40FT: 'high_cube_40ft',
        REEFER_20FT: 'reefer_20ft',
        CUSTOM: 'custom'
    },

    CONTAINER_TYPE_NAMES: {
        standard_20ft: 'Standard 20ft',
        standard_40ft: 'Standard 40ft',
        high_cube_40ft: 'High Cube 40ft',
        reefer_20ft: 'Refrigerated 20ft',
        custom: 'Custom Container'
    },

    // Default Container Specifications (in cm and kg)
    DEFAULT_CONTAINERS: {
        standard_20ft: {
            name: 'Standard 20ft Container',
            length: 605,
            width: 244,
            height: 259,
            max_weight: 28200,
            volume: 38.3,
            description: 'Standard 20-foot dry container'
        },
        standard_40ft: {
            name: 'Standard 40ft Container',
            length: 1219,
            width: 244,
            height: 259,
            max_weight: 26700,
            volume: 76.3,
            description: 'Standard 40-foot dry container'
        },
        high_cube_40ft: {
            name: 'High Cube 40ft Container',
            length: 1219,
            width: 244,
            height: 289,
            max_weight: 26700,
            volume: 85.7,
            description: 'High cube 40-foot container with extra height'
        },
        reefer_20ft: {
            name: 'Refrigerated 20ft Container',
            length: 543,
            width: 229,
            height: 226,
            max_weight: 30480,
            volume: 28.0,
            description: '20-foot refrigerated container'
        }
    },

    // Item Properties
    ITEM_PROPERTIES: {
        FRAGILE: 'fragile',
        STACKABLE: 'stackable',
        ROTATION_ALLOWED: 'rotation_allowed'
    },

    PROPERTY_NAMES: {
        fragile: 'Fragile',
        stackable: 'Stackable',
        rotation_allowed: 'Rotation Allowed'
    },

    // Validation Constants
    VALIDATION: {
        MAX_CONTAINER_DIMENSION: 10000, // 100 meters in cm
        MAX_CONTAINER_WEIGHT: 1000000, // 1000 tons in kg
        MAX_ITEM_DIMENSION: 1000, // 10 meters in cm
        MAX_ITEM_WEIGHT: 10000, // 10 tons in kg
        MAX_ITEM_QUANTITY: 1000,
        MIN_ITEM_VOLUME: 1 // 1 cm³
    },

    // Optimization Constants
    OPTIMIZATION: {
        MAX_EXECUTION_TIME: 300, // 5 minutes in seconds
        MIN_GENERATIONS: 10,
        MAX_GENERATIONS: 1000,
        MIN_POPULATION_SIZE: 10,
        MAX_POPULATION_SIZE: 200,
        MIN_MUTATION_RATE: 0.01,
        MAX_MUTATION_RATE: 0.5,
        DEFAULT_GENERATIONS: 100,
        DEFAULT_POPULATION_SIZE: 50,
        DEFAULT_MUTATION_RATE: 0.1
    },

    // UI Constants
    UI: {
        DEBOUNCE_DELAY: 300,
        NOTIFICATION_DURATION: 5000,
        AUTO_SAVE_DELAY: 2000,
        MAX_HISTORY_ITEMS: 50,
        CHART_ANIMATION_DURATION: 1000
    },

    // Color Scheme
    COLORS: {
        PRIMARY: '#2563eb',
        PRIMARY_DARK: '#1d4ed8',
        SECONDARY: '#64748b',
        SUCCESS: '#10b981',
        WARNING: '#f59e0b',
        ERROR: '#ef4444',
        INFO: '#3b82f6',
        
        // Algorithm-specific colors
        ALGORITHM: {
            packing: '#3b82f6',
            genetic: '#10b981',
            stowage: '#f59e0b',
            auto: '#8b5cf6'
        },

        // Utilization colors
        UTILIZATION: {
            low: '#ef4444',
            medium: '#f59e0b',
            high: '#10b981',
            excellent: '#059669'
        }
    },

    // Local Storage Keys
    STORAGE_KEYS: {
        CONTAINERS: 'cargoopt_containers',
        ITEMS: 'cargoopt_items',
        SETTINGS: 'cargoopt_settings',
        HISTORY: 'cargoopt_history',
        FAVORITES: 'cargoopt_favorites'
    },

    // Export Formats
    EXPORT_FORMATS: {
        JSON: 'json',
        CSV: 'csv',
        EXCEL: 'excel',
        PDF: 'pdf'
    },

    // File Size Limits
    FILE_LIMITS: {
        MAX_UPLOAD_SIZE: 10 * 1024 * 1024, // 10MB
        MAX_IMPORT_ITEMS: 1000,
        MAX_EXPORT_ITEMS: 10000
    },

    // Performance Metrics
    PERFORMANCE: {
        GOOD_UTILIZATION: 0.7,
        EXCELLENT_UTILIZATION: 0.85,
        FAST_EXECUTION: 5, // seconds
        SLOW_EXECUTION: 30 // seconds
    },

    // Sample Data
    SAMPLE_DATA: {
        CONTAINERS: [
            {
                name: "Sample 20ft Container",
                length: 605,
                width: 244,
                height: 259,
                max_weight: 28200,
                type: "standard_20ft"
            }
        ],
        ITEMS: [
            {
                id: 1,
                name: "Small Box",
                length: 50,
                width: 40,
                height: 30,
                weight: 10,
                quantity: 10,
                fragile: false,
                stackable: true,
                rotation_allowed: true
            },
            {
                id: 2,
                name: "Medium Crate",
                length: 120,
                width: 80,
                height: 60,
                weight: 50,
                quantity: 5,
                fragile: false,
                stackable: true,
                rotation_allowed: true
            },
            {
                id: 3,
                name: "Large Pallet",
                length: 200,
                width: 120,
                height: 100,
                weight: 200,
                quantity: 3,
                fragile: false,
                stackable: true,
                rotation_allowed: false
            }
        ]
    },

    // Error Messages
    ERROR_MESSAGES: {
        NETWORK_ERROR: 'Network error. Please check your connection.',
        SERVER_ERROR: 'Server error. Please try again later.',
        VALIDATION_ERROR: 'Please check your input data.',
        TIMEOUT_ERROR: 'Request timed out. Please try again.',
        UNAUTHORIZED: 'Authentication required.',
        FORBIDDEN: 'Access denied.',
        NOT_FOUND: 'Resource not found.'
    },

    // Success Messages
    SUCCESS_MESSAGES: {
        OPTIMIZATION_COMPLETE: 'Optimization completed successfully!',
        DATA_SAVED: 'Data saved successfully.',
        EXPORT_COMPLETE: 'Export completed successfully.',
        IMPORT_COMPLETE: 'Import completed successfully.'
    }
};

// Configuration that can be overridden by environment
const Config = {
    ...Constants,
    
    // Environment-specific overrides
    isDevelopment: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1',
    isProduction: !window.location.hostname.includes('localhost'),
    
    // Dynamic configuration based on environment
    get API_BASE_URL() {
        return this.isDevelopment ? 
            'http://localhost:5000/api/v1' : 
            '/api/v1';
    },
    
    get LOG_LEVEL() {
        return this.isDevelopment ? 'debug' : 'error';
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Constants, Config };
} else {
    window.Constants = Constants;
    window.Config = Config;
}