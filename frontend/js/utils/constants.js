/**
 * Application Constants
 * Global constants used throughout the application
 */

// ============================================================================
// API Configuration
// ============================================================================

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

export const API_ENDPOINTS = {
  // Core
  HEALTH: '/health',
  INFO: '/info',
  STATS: '/stats',
  CONFIG: '/config',
  VALIDATE: '/validate',
  
  // Optimization
  OPTIMIZE: '/optimize',
  HISTORY: '/history',
  EXPORTS: '/exports',
  
  // Resources
  CONTAINERS: '/containers',
  ITEMS: '/items',
  
  // Stowage
  STOWAGE: '/stowage',
};

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
};

// ============================================================================
// Container Standards
// ============================================================================

export const CONTAINER_TYPES = {
  STANDARD_20: {
    name: '20ft Standard',
    code: '20GP',
    length: 5898,
    width: 2352,
    height: 2393,
    maxWeight: 28180,
    tareWeight: 2300,
    volume: 33.2,
  },
  STANDARD_40: {
    name: '40ft Standard',
    code: '40GP',
    length: 12032,
    width: 2352,
    height: 2393,
    maxWeight: 26680,
    tareWeight: 3800,
    volume: 67.7,
  },
  HIGH_CUBE_40: {
    name: '40ft High Cube',
    code: '40HC',
    length: 12032,
    width: 2352,
    height: 2698,
    maxWeight: 26560,
    tareWeight: 3920,
    volume: 76.3,
  },
  HIGH_CUBE_45: {
    name: '45ft High Cube',
    code: '45HC',
    length: 13556,
    width: 2352,
    height: 2698,
    maxWeight: 27700,
    tareWeight: 4800,
    volume: 86.0,
  },
  REFRIGERATED_20: {
    name: '20ft Refrigerated',
    code: '20RF',
    length: 5444,
    width: 2294,
    height: 2276,
    maxWeight: 27400,
    tareWeight: 3080,
    volume: 28.4,
  },
  REFRIGERATED_40: {
    name: '40ft Refrigerated',
    code: '40RF',
    length: 11583,
    width: 2294,
    height: 2544,
    maxWeight: 26960,
    tareWeight: 4800,
    volume: 67.5,
  },
};

// ============================================================================
// Item Types
// ============================================================================

export const ITEM_TYPES = {
  GLASS: { name: 'Glass', color: '#87CEEB', fragile: true },
  WOOD: { name: 'Wood', color: '#8B4513', fragile: false },
  METAL: { name: 'Metal', color: '#708090', fragile: false },
  PLASTIC: { name: 'Plastic', color: '#FFB6C1', fragile: false },
  ELECTRONICS: { name: 'Electronics', color: '#4169E1', fragile: true },
  TEXTILES: { name: 'Textiles', color: '#DDA0DD', fragile: false },
  FOOD: { name: 'Food', color: '#FFA500', fragile: false },
  CHEMICALS: { name: 'Chemicals', color: '#FF4500', fragile: false },
  OTHER: { name: 'Other', color: '#A9A9A9', fragile: false },
};

export const STORAGE_CONDITIONS = {
  STANDARD: { name: 'Standard', icon: 'box', temp: null },
  REFRIGERATED: { name: 'Refrigerated', icon: 'snowflake', temp: { min: 2, max: 8 } },
  FROZEN: { name: 'Frozen', icon: 'ice-crystal', temp: { min: -25, max: -18 } },
  HAZARDOUS: { name: 'Hazardous', icon: 'exclamation-triangle', temp: null },
};

// ============================================================================
// IMDG Hazard Classes
// ============================================================================

export const HAZARD_CLASSES = {
  '1': { name: 'Explosives', color: '#FF0000', icon: 'bomb' },
  '2.1': { name: 'Flammable Gas', color: '#FF6B6B', icon: 'fire' },
  '2.2': { name: 'Non-Flammable Gas', color: '#90EE90', icon: 'wind' },
  '2.3': { name: 'Toxic Gas', color: '#8B008B', icon: 'skull' },
  '3': { name: 'Flammable Liquid', color: '#FFA500', icon: 'fire-alt' },
  '4.1': { name: 'Flammable Solid', color: '#FFD700', icon: 'fire' },
  '4.2': { name: 'Spontaneous Combustion', color: '#FF4500', icon: 'fire' },
  '4.3': { name: 'Dangerous When Wet', color: '#4169E1', icon: 'tint' },
  '5.1': { name: 'Oxidizer', color: '#FFFF00', icon: 'atom' },
  '5.2': { name: 'Organic Peroxide', color: '#FF8C00', icon: 'flask' },
  '6.1': { name: 'Toxic', color: '#800080', icon: 'skull-crossbones' },
  '6.2': { name: 'Infectious', color: '#DC143C', icon: 'biohazard' },
  '7': { name: 'Radioactive', color: '#FFFF00', icon: 'radiation' },
  '8': { name: 'Corrosive', color: '#000000', icon: 'vial' },
  '9': { name: 'Miscellaneous', color: '#808080', icon: 'question' },
};

// ============================================================================
// Optimization Algorithms
// ============================================================================

export const ALGORITHMS = {
  GENETIC: {
    name: 'Genetic Algorithm',
    code: 'genetic',
    description: 'Population-based evolutionary optimization',
    icon: 'dna',
    recommended: true,
  },
  CONSTRAINT: {
    name: 'Constraint Programming',
    code: 'constraint',
    description: 'Rule-based constraint satisfaction',
    icon: 'puzzle-piece',
    recommended: false,
  },
  HYBRID: {
    name: 'Hybrid Approach',
    code: 'hybrid',
    description: 'Combination of genetic and constraint methods',
    icon: 'random',
    recommended: false,
  },
  AUTO: {
    name: 'Auto-Select',
    code: 'auto',
    description: 'Automatically select best algorithm',
    icon: 'magic',
    recommended: true,
  },
};

// ============================================================================
// Optimization Objectives
// ============================================================================

export const OPTIMIZATION_OBJECTIVES = {
  BALANCED: {
    name: 'Balanced',
    description: 'Balance between all factors',
    weights: { utilization: 0.4, stability: 0.25, constraints: 0.25, accessibility: 0.1 },
  },
  UTILIZATION: {
    name: 'Maximum Space Utilization',
    description: 'Prioritize space efficiency',
    weights: { utilization: 0.7, stability: 0.1, constraints: 0.15, accessibility: 0.05 },
  },
  STABILITY: {
    name: 'Maximum Stability',
    description: 'Prioritize load stability',
    weights: { utilization: 0.2, stability: 0.6, constraints: 0.15, accessibility: 0.05 },
  },
  ACCESSIBILITY: {
    name: 'Maximum Accessibility',
    description: 'Prioritize easy unloading',
    weights: { utilization: 0.2, stability: 0.2, constraints: 0.15, accessibility: 0.45 },
  },
};

// ============================================================================
// Validation Rules
// ============================================================================

export const VALIDATION_RULES = {
  CONTAINER: {
    LENGTH: { min: 100, max: 50000, unit: 'mm' },
    WIDTH: { min: 100, max: 10000, unit: 'mm' },
    HEIGHT: { min: 100, max: 10000, unit: 'mm' },
    MAX_WEIGHT: { min: 1, max: 100000, unit: 'kg' },
  },
  ITEM: {
    LENGTH: { min: 1, max: 20000, unit: 'mm' },
    WIDTH: { min: 1, max: 10000, unit: 'mm' },
    HEIGHT: { min: 1, max: 10000, unit: 'mm' },
    WEIGHT: { min: 0.001, max: 50000, unit: 'kg' },
    QUANTITY: { min: 1, max: 10000 },
    PRIORITY: { min: 1, max: 10 },
  },
  OPTIMIZATION: {
    POPULATION_SIZE: { min: 10, max: 500 },
    GENERATIONS: { min: 5, max: 500 },
    TIME_LIMIT: { min: 10, max: 600, unit: 'seconds' },
    MUTATION_RATE: { min: 0, max: 1 },
    CROSSOVER_RATE: { min: 0, max: 1 },
  },
};

// ============================================================================
// UI Constants
// ============================================================================

export const COLORS = {
  PRIMARY: '#3b82f6',
  SECONDARY: '#8b5cf6',
  SUCCESS: '#22c55e',
  WARNING: '#f59e0b',
  ERROR: '#ef4444',
  INFO: '#06b6d4',
  LIGHT: '#f9fafb',
  DARK: '#1f2937',
};

export const STATUS_COLORS = {
  pending: '#f59e0b',
  running: '#3b82f6',
  completed: '#22c55e',
  failed: '#ef4444',
  cancelled: '#6b7280',
};

export const STATUS_ICONS = {
  pending: 'clock',
  running: 'spinner',
  completed: 'check-circle',
  failed: 'times-circle',
  cancelled: 'ban',
};

export const VIEW_PRESETS = {
  FRONT: { name: 'Front', code: 'front', icon: 'arrow-right' },
  BACK: { name: 'Back', code: 'back', icon: 'arrow-left' },
  LEFT: { name: 'Left', code: 'left', icon: 'arrow-left' },
  RIGHT: { name: 'Right', code: 'right', icon: 'arrow-right' },
  TOP: { name: 'Top', code: 'top', icon: 'arrow-up' },
  ISOMETRIC: { name: 'Isometric', code: 'isometric', icon: 'cube' },
};

// ============================================================================
// File Formats
// ============================================================================

export const EXPORT_FORMATS = {
  PDF: { name: 'PDF Document', ext: 'pdf', mime: 'application/pdf', icon: 'file-pdf' },
  JSON: { name: 'JSON Data', ext: 'json', mime: 'application/json', icon: 'file-code' },
  CSV: { name: 'CSV Spreadsheet', ext: 'csv', mime: 'text/csv', icon: 'file-csv' },
  XLSX: { name: 'Excel Spreadsheet', ext: 'xlsx', mime: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', icon: 'file-excel' },
  PNG: { name: 'PNG Image', ext: 'png', mime: 'image/png', icon: 'file-image' },
  JPG: { name: 'JPEG Image', ext: 'jpg', mime: 'image/jpeg', icon: 'file-image' },
};

export const IMPORT_FORMATS = {
  JSON: { name: 'JSON', ext: '.json', mime: 'application/json' },
  CSV: { name: 'CSV', ext: '.csv', mime: 'text/csv' },
  XLSX: { name: 'Excel', ext: '.xlsx,.xls', mime: 'application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' },
};

// ============================================================================
// Keyboard Shortcuts
// ============================================================================

export const KEYBOARD_SHORTCUTS = {
  NEW_OPTIMIZATION: { key: 'n', ctrl: true, description: 'New optimization' },
  SAVE: { key: 's', ctrl: true, description: 'Save' },
  EXPORT: { key: 'e', ctrl: true, description: 'Export' },
  HELP: { key: '?', ctrl: false, description: 'Show help' },
  ESCAPE: { key: 'Escape', ctrl: false, description: 'Cancel / Go back' },
  SEARCH: { key: 'k', ctrl: true, description: 'Search' },
};

// ============================================================================
// Messages
// ============================================================================

export const MESSAGES = {
  SUCCESS: {
    OPTIMIZATION_COMPLETE: 'Optimization completed successfully!',
    SAVE_SUCCESS: 'Saved successfully',
    DELETE_SUCCESS: 'Deleted successfully',
    EXPORT_SUCCESS: 'Export completed',
    IMPORT_SUCCESS: 'Import completed',
  },
  ERROR: {
    GENERIC: 'An error occurred. Please try again.',
    NETWORK: 'Network error. Please check your connection.',
    VALIDATION: 'Please check your input and try again.',
    NOT_FOUND: 'Resource not found',
    UNAUTHORIZED: 'You are not authorized to perform this action.',
    SERVER_ERROR: 'Server error. Please try again later.',
  },
  WARNING: {
    UNSAVED_CHANGES: 'You have unsaved changes. Are you sure you want to leave?',
    DELETE_CONFIRM: 'Are you sure you want to delete this item?',
    CANCEL_CONFIRM: 'Are you sure you want to cancel this optimization?',
  },
  INFO: {
    LOADING: 'Loading...',
    PROCESSING: 'Processing...',
    SAVING: 'Saving...',
    DELETING: 'Deleting...',
    EXPORTING: 'Exporting...',
    IMPORTING: 'Importing...',
  },
};

// ============================================================================
// Pagination
// ============================================================================

export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_PER_PAGE: 20,
  MAX_PER_PAGE: 100,
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
};

// ============================================================================
// Chart Colors
// ============================================================================

export const CHART_COLORS = [
  '#3b82f6', '#8b5cf6', '#22c55e', '#f59e0b', 
  '#ef4444', '#06b6d4', '#ec4899', '#10b981',
  '#f97316', '#6366f1', '#14b8a6', '#a855f7',
];

// ============================================================================
// Animation Durations
// ============================================================================

export const ANIMATION = {
  FAST: 150,
  NORMAL: 300,
  SLOW: 500,
};

// ============================================================================
// Local Storage Keys
// ============================================================================

export const STORAGE_KEYS = {
  USER_PREFERENCES: 'cargoopt_user_preferences',
  RECENT_CONTAINERS: 'cargoopt_recent_containers',
  RECENT_ITEMS: 'cargoopt_recent_items',
  VIEW_SETTINGS: 'cargoopt_view_settings',
  AUTH_TOKEN: 'cargoopt_auth_token',
};

// ============================================================================
// Feature Flags
// ============================================================================

export const FEATURES = {
  ENABLE_3D_VISUALIZATION: true,
  ENABLE_SHIP_STOWAGE: true,
  ENABLE_EMISSIONS_CALCULATION: true,
  ENABLE_EXPORT_PDF: true,
  ENABLE_ADVANCED_PARAMETERS: true,
  ENABLE_MULTI_CONTAINER: false, // Coming soon
  ENABLE_REAL_TIME_COLLABORATION: false, // Coming soon
};

// ============================================================================
// Environment
// ============================================================================

export const ENV = {
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
  apiUrl: import.meta.env.VITE_API_BASE_URL,
  version: import.meta.env.VITE_APP_VERSION || '1.0.0',
};

// ============================================================================
// Regular Expressions
// ============================================================================

export const REGEX = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE: /^\+?[\d\s-()]+$/,
  URL: /^https?:\/\/.+/,
  HEX_COLOR: /^#[0-9A-Fa-f]{6}$/,
  CONTAINER_ID: /^[A-Z]{4}[0-9]{7}$/,
};

export default {
  API_BASE_URL,
  API_ENDPOINTS,
  HTTP_STATUS,
  CONTAINER_TYPES,
  ITEM_TYPES,
  STORAGE_CONDITIONS,
  HAZARD_CLASSES,
  ALGORITHMS,
  OPTIMIZATION_OBJECTIVES,
  VALIDATION_RULES,
  COLORS,
  STATUS_COLORS,
  STATUS_ICONS,
  VIEW_PRESETS,
  EXPORT_FORMATS,
  IMPORT_FORMATS,
  KEYBOARD_SHORTCUTS,
  MESSAGES,
  PAGINATION,
  CHART_COLORS,
  ANIMATION,
  STORAGE_KEYS,
  FEATURES,
  ENV,
  REGEX,
};