"""
Application Settings Configuration
Environment-based configuration management for CargoOpt
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings configuration"""
    
    # Application
    app_name: str = "CargoOpt"
    app_env: str = "development"
    debug: bool = False
    secret_key: str = "your-secret-key-change-in-production"
    host: str = "0.0.0.0"
    port: int = 5000
    
    # API
    api_v1_prefix: str = "/api/v1"
    allowed_hosts: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5000",
    ]
    
    # Database - consolidated fields
    database_url: str = "postgresql://username:password@localhost:5432/cargoopt"
    
    # Security
    jwt_secret_key: str = "your-jwt-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # File Upload
    max_upload_size: int = 104857600  # 100MB in bytes
    allowed_extensions: List[str] = ["json", "csv", "xlsx"]
    
    # Optimization Parameters
    max_iterations: int = 1000
    population_size: int = 100
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/cargoopt.log"
    
    # External Services (if needed)
    weather_api_key: Optional[str] = None
    map_api_key: Optional[str] = None
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # This allows extra fields in .env without validation errors
    }
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from string or list"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @field_validator("allowed_extensions", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, v):
        """Parse allowed extensions from string or list"""
        if isinstance(v, str):
            return [ext.strip().lower() for ext in v.split(",")]
        return v


# Global settings instance
_settings = None

def get_settings() -> Settings:
    """
    Get application settings instance (singleton pattern)
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def reload_settings() -> Settings:
    """
    Reload settings from environment (useful for testing)
    """
    global _settings
    _settings = Settings()
    return _settings