"""
CargoOpt Configuration Settings
Centralized configuration management for all application settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Config:
    """Base configuration class with default settings."""
    
    # Flask settings
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 'yes')
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Server settings
    HOST = os.getenv('API_HOST', '0.0.0.0')
    PORT = int(os.getenv('API_PORT', 5000))
    
    # Database settings
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'cargoopt')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 5))
    DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', 10))
    
    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # File upload settings
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))  # 10MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(BASE_DIR / 'data' / 'uploads'))
    EXPORT_FOLDER = os.getenv('EXPORT_FOLDER', str(BASE_DIR / 'data' / 'exports'))
    ALLOWED_EXTENSIONS = {'json', 'csv', 'xlsx', 'xls'}
    
    # Genetic Algorithm settings
    GA_POPULATION_SIZE = int(os.getenv('GA_POPULATION_SIZE', 100))
    GA_GENERATIONS = int(os.getenv('GA_GENERATIONS', 50))
    GA_MUTATION_RATE = float(os.getenv('GA_MUTATION_RATE', 0.15))
    GA_CROSSOVER_RATE = float(os.getenv('GA_CROSSOVER_RATE', 0.85))
    GA_TOURNAMENT_SIZE = int(os.getenv('GA_TOURNAMENT_SIZE', 3))
    GA_ELITE_SIZE = int(os.getenv('GA_ELITE_SIZE', 5))
    
    # Optimization settings
    MAX_COMPUTATION_TIME = int(os.getenv('MAX_COMPUTATION_TIME', 300))  # seconds
    ENABLE_PARALLEL = os.getenv('ENABLE_PARALLEL', 'True').lower() in ('true', '1', 'yes')
    NUM_WORKERS = int(os.getenv('NUM_WORKERS', 4))
    
    # Constraint weights for fitness function
    WEIGHT_UTILIZATION = float(os.getenv('WEIGHT_UTILIZATION', 0.4))
    WEIGHT_STABILITY = float(os.getenv('WEIGHT_STABILITY', 0.25))
    WEIGHT_CONSTRAINTS = float(os.getenv('WEIGHT_CONSTRAINTS', 0.25))
    WEIGHT_ACCESSIBILITY = float(os.getenv('WEIGHT_ACCESSIBILITY', 0.1))
    
    # Report settings
    REPORT_DPI = int(os.getenv('REPORT_DPI', 300))
    REPORT_PAGE_SIZE = os.getenv('REPORT_PAGE_SIZE', 'A4')
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_FILE = os.getenv('LOG_FILE', str(BASE_DIR / 'logs' / 'cargoopt.log'))
    
    # Cache settings
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    
    # Rate limiting
    RATE_LIMIT_DEFAULT = os.getenv('RATE_LIMIT_DEFAULT', '100/hour')
    RATE_LIMIT_OPTIMIZATION = os.getenv('RATE_LIMIT_OPTIMIZATION', '10/minute')
    
    # Item types configuration
    ITEM_TYPES = [
        'glass', 'wood', 'metal', 'plastic', 
        'electronics', 'textiles', 'food', 'chemicals', 'other'
    ]
    
    # Storage conditions
    STORAGE_CONDITIONS = ['standard', 'refrigerated', 'frozen', 'hazardous']
    
    # Container types
    CONTAINER_TYPES = [
        'standard', 'high_cube', 'refrigerated', 
        'open_top', 'flat_rack', 'tank'
    ]
    
    # IMDG hazard classes
    HAZARD_CLASSES = [
        '1', '2.1', '2.2', '2.3', '3', '4.1', '4.2', '4.3',
        '5.1', '5.2', '6.1', '6.2', '7', '8', '9'
    ]


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'
    LOG_LEVEL = 'DEBUG'
    
    # Reduced GA parameters for faster iteration
    GA_POPULATION_SIZE = 50
    GA_GENERATIONS = 25


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'
    LOG_LEVEL = 'WARNING'
    
    # Stricter security settings
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set in production
    
    # Production GA parameters
    GA_POPULATION_SIZE = 150
    GA_GENERATIONS = 100
    
    # Production database pool
    DB_POOL_SIZE = 10
    DB_MAX_OVERFLOW = 20


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    FLASK_ENV = 'testing'
    
    # Use separate test database
    DB_NAME = os.getenv('TEST_DB_NAME', 'cargoopt_test')
    
    # Minimal GA for fast tests
    GA_POPULATION_SIZE = 10
    GA_GENERATIONS = 5
    MAX_COMPUTATION_TIME = 30


# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment."""
    env = os.getenv('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)