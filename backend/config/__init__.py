"""
CargoOpt Configuration Package
Provides configuration management and database connectivity.
"""

from backend.config.settings import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from backend.config.database import DatabaseManager, db_manager


def get_database_url():
    """
    Get the database URL from configuration.
    
    Returns:
        Database URL string
    """
    config = Config()
    return config.DATABASE_URL


__all__ = [
    'Config',
    'DevelopmentConfig', 
    'ProductionConfig',
    'TestingConfig',
    'DatabaseManager',
    'db_manager',
    'get_database_url'
]