"""
CargoOpt Backend Package
Container Vessel Stowage Optimization System

This package contains the backend API, services, and algorithms
for the CargoOpt optimization system.
"""

__version__ = "1.0.0"
__author__ = "CargoOpt Team"
__description__ = "Container Vessel Stowage Optimization Backend"

# Import main components for easier access
from backend.main import app
from backend.config.settings import get_settings

# Package-level imports
__all__ = [
    "app",
    "get_settings",
]