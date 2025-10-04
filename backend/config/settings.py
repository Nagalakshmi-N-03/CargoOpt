"""
Application Settings Configuration
Environment-based configuration management for CargoOpt
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
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
    
    # Database
    database_url: str = "postgresql://username:password@localhost:5432/cargoopt"
    database_name: str = "cargoopt"
    database_user: str = "cargoopt_user"
    database_password: str = "your_secure_password"
    database_host: str = "localhost"
    database_port: int = 5432
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @validator("database_url", pre=True)
    def assemble_db_connection(cls, v, values):
        """Assemble database URL from components if not provided directly"""
        if isinstance(v, str) and v:
            return v
        
        return (
            f"postgresql://{values.get('database_user')}:"
            f"{values.get('database_password')}@"
            f"{values.get('database_host')}:"
            f"{values.get('database_port')}/"
            f"{values.get('database_name')}"
        )
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("allowed_hosts", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from string or list"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("allowed_extensions", pre=True)
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