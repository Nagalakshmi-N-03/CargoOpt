"""
CargoOpt Configuration Package
Provides configuration management and database connectivity.
"""

from backend.config.settings import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from backend.config.database import DatabaseManager, db_manager

__all__ = [
    'Config',
    'DevelopmentConfig', 
    'ProductionConfig',
    'TestingConfig',
    'DatabaseManager',
    'db_manager'
]