"""
API Routes and Models for Cargo Space Optimization
"""

from .routes import router
from .models import (
    ContainerData,
    CargoItemData,
    OptimizationRequest,
    GeneticOptimizationRequest,
    MultiContainerRequest,
    BatchOptimizationRequest,
    PlacementValidationRequest,
    AlgorithmComparisonRequest,
    OptimizationResponse,
    BatchOptimizationResponse,
    ValidationResponse,
    ComparisonResponse
)

__all__ = [
    'router',
    'ContainerData',
    'CargoItemData', 
    'OptimizationRequest',
    'GeneticOptimizationRequest',
    'MultiContainerRequest',
    'BatchOptimizationRequest',
    'PlacementValidationRequest',
    'AlgorithmComparisonRequest',
    'OptimizationResponse',
    'BatchOptimizationResponse',
    'ValidationResponse',
    'ComparisonResponse'
]