"""
CargoOpt API Package
Provides REST API endpoints for the container optimization system.

Modules:
    - routes: Main API routes and version info
    - optimization: Container optimization endpoints
    - containers: Container management endpoints
    - items: Item management endpoints
    - history: Optimization history endpoints
    - exports: Export and report generation endpoints
    - models: Data models and validation schemas
"""

from backend.api.routes import api_bp
from backend.api.models import (
    ContainerSchema,
    ItemSchema,
    OptimizationRequestSchema,
    OptimizationResponseSchema,
    PlacementSchema
)

__all__ = [
    'api_bp',
    'ContainerSchema',
    'ItemSchema',
    'OptimizationRequestSchema',
    'OptimizationResponseSchema',
    'PlacementSchema'
]