"""
CargoOpt Backend Package
AI-Powered Container Optimization System

This package provides the core backend functionality including:
- REST API endpoints for optimization operations
- Genetic algorithm and constraint programming optimization engines
- Database models and data access layers
- Utility functions and helpers
"""

__version__ = '1.0.0'
__author__ = 'CargoOpt Development Team'
__email__ = 'support@cargoopt.com'

from backend.main import create_app

__all__ = ['create_app', '__version__']