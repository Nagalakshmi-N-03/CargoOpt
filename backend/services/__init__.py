"""
CargoOpt Services Package
Business logic layer providing core services for the optimization system.

This package contains services that coordinate between the API layer and
algorithm implementations, providing data processing, validation, and
optimization orchestration.

Services:
    - DataProcessor: Handles data transformation and preprocessing
    - OptimizationService: Orchestrates optimization workflows
    - ValidationService: Validates input data and results
    - EmissionCalculator: Calculates environmental impact metrics

Usage:
    from backend.services import OptimizationService, ValidationService
    
    validator = ValidationService()
    optimizer = OptimizationService()
    
    # Validate input
    is_valid, errors = validator.validate_optimization_request(data)
    
    # Run optimization
    if is_valid:
        result = optimizer.optimize(data)
"""

from backend.services.data_processor import DataProcessor, DataTransformer
from backend.services.optimization import OptimizationService, OptimizationOrchestrator
from backend.services.validation import (
    ValidationService, 
    ContainerValidator,
    ItemValidator,
    ConstraintValidator
)
from backend.services.emission_calculator import (
    EmissionCalculator,
    CarbonFootprintAnalyzer,
    FuelEfficiencyCalculator
)

__all__ = [
    # Data Processing
    'DataProcessor',
    'DataTransformer',
    
    # Optimization
    'OptimizationService',
    'OptimizationOrchestrator',
    
    # Validation
    'ValidationService',
    'ContainerValidator',
    'ItemValidator',
    'ConstraintValidator',
    
    # Emissions
    'EmissionCalculator',
    'CarbonFootprintAnalyzer',
    'FuelEfficiencyCalculator'
]

__version__ = '1.0.0'
__author__ = 'CargoOpt Development Team'

# Service initialization logging
from backend.utils.logger import get_logger
logger = get_logger(__name__)
logger.info("CargoOpt Services Package initialized")