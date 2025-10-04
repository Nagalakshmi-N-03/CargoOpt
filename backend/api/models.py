from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class AlgorithmType(str, Enum):
    PACKING = "packing"
    GENETIC = "genetic"
    STOWAGE = "stowage"
    AUTO = "auto"

class ContainerType(str, Enum):
    STANDARD_20FT = "standard_20ft"
    STANDARD_40FT = "standard_40ft"
    HIGH_CUBE_40FT = "high_cube_40ft"
    REEFER_20FT = "reefer_20ft"
    CUSTOM = "custom"

class OptimizationStrategy(str, Enum):
    BALANCED = "balanced"
    SPACE_FIRST = "space_first"
    WEIGHT_FIRST = "weight_first"
    STABILITY_FIRST = "stability_first"

class ContainerData(BaseModel):
    length: float = Field(..., gt=0, description="Container length in cm")
    width: float = Field(..., gt=0, description="Container width in cm")
    height: float = Field(..., gt=0, description="Container height in cm")
    max_weight: float = Field(..., gt=0, description="Maximum weight capacity in kg")
    name: str = Field("Container", description="Container name")
    type: ContainerType = Field(ContainerType.CUSTOM, description="Container type")
    id: Optional[str] = Field(None, description="Container identifier")

    @validator('length', 'width', 'height', 'max_weight')
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError('Must be positive')
        return v

class CargoItemData(BaseModel):
    id: int = Field(..., description="Unique item identifier")
    length: float = Field(..., gt=0, description="Item length in cm")
    width: float = Field(..., gt=0, description="Item width in cm")
    height: float = Field(..., gt=0, description="Item height in cm")
    weight: float = Field(..., gt=0, description="Item weight in kg")
    quantity: int = Field(1, gt=0, description="Number of identical items")
    fragile: bool = Field(False, description="Whether item is fragile")
    stackable: bool = Field(True, description="Whether item can be stacked")
    rotation_allowed: bool = Field(True, description="Whether item can be rotated")
    name: str = Field("Item", description="Item name")
    priority: int = Field(1, ge=1, le=10, description="Packing priority (1-10)")

    @validator('length', 'width', 'height', 'weight')
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError('Must be positive')
        return v

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v

class PlacementData(BaseModel):
    item_id: int = Field(..., description="ID of the placed item")
    position: List[float] = Field(..., min_items=3, max_items=3, description="[x, y, z] coordinates")
    dimensions: List[float] = Field(..., min_items=3, max_items=3, description="[length, width, height] dimensions")
    rotated: bool = Field(False, description="Whether item is rotated")
    layer: int = Field(0, description="Packing layer number")

class OptimizationMetrics(BaseModel):
    utilization_rate: float = Field(..., ge=0, le=1, description="Volume utilization rate")
    total_items_packed: int = Field(..., ge=0, description="Number of items packed")
    total_volume_used: float = Field(..., ge=0, description="Total volume used")
    total_weight_used: float = Field(..., ge=0, description="Total weight used")
    execution_time: float = Field(..., ge=0, description="Execution time in seconds")
    efficiency_score: float = Field(..., ge=0, le=1, description="Overall efficiency score")
    stability_score: Optional[float] = Field(None, ge=0, le=1, description="Stability score")
    space_efficiency: Optional[float] = Field(None, ge=0, le=1, description="Space efficiency metric")

class OptimizationRequest(BaseModel):
    container: ContainerData = Field(..., description="Container specifications")
    items: List[CargoItemData] = Field(..., min_items=1, description="Items to pack")
    algorithm: AlgorithmType = Field(AlgorithmType.AUTO, description="Optimization algorithm to use")
    strategy: OptimizationStrategy = Field(OptimizationStrategy.BALANCED, description="Optimization strategy")
    max_execution_time: int = Field(30, ge=1, le=300, description="Maximum execution time in seconds")

class GeneticOptimizationRequest(BaseModel):
    container: ContainerData = Field(..., description="Container specifications")
    items: List[CargoItemData] = Field(..., min_items=1, description="Items to pack")
    generations: int = Field(100, ge=10, le=1000, description="Number of generations")
    population_size: int = Field(50, ge=10, le=200, description="Population size")
    mutation_rate: float = Field(0.1, ge=0.01, le=0.5, description="Mutation rate")
    crossover_rate: float = Field(0.8, ge=0.5, le=1.0, description="Crossover rate")
    elitism_count: int = Field(2, ge=1, le=10, description="Number of elite individuals")

class MultiContainerRequest(BaseModel):
    containers: List[ContainerData] = Field(..., min_items=1, description="Available containers")
    items: List[CargoItemData] = Field(..., min_items=1, description="Items to distribute")
    strategy: OptimizationStrategy = Field(OptimizationStrategy.BALANCED, description="Distribution strategy")
    minimize_containers: bool = Field(True, description="Whether to minimize container count")

class BatchOptimizationRequest(BaseModel):
    tasks: List[OptimizationRequest] = Field(..., min_items=1, description="Optimization tasks")
    parallel_processing: bool = Field(False, description="Whether to process in parallel")
    batch_id: Optional[str] = Field(None, description="Batch identifier")

class PlacementValidationRequest(BaseModel):
    container: ContainerData = Field(..., description="Container specifications")
    items: List[CargoItemData] = Field(..., description="Items data")
    placements: List[PlacementData] = Field(..., description="Placements to validate")

class AlgorithmComparisonRequest(BaseModel):
    container: ContainerData = Field(..., description="Container specifications")
    items: List[CargoItemData] = Field(..., min_items=1, description="Items to pack")
    algorithms: List[AlgorithmType] = Field(..., min_items=1, description="Algorithms to compare")
    metric_weights: Dict[str, float] = Field(
        default_factory=lambda: {"utilization_rate": 0.4, "execution_time": 0.3, "stability_score": 0.3},
        description="Weights for different metrics"
    )

# Response Models
class OptimizationResponse(BaseModel):
    success: bool = Field(..., description="Whether optimization was successful")
    algorithm: str = Field(..., description="Algorithm used")
    result: Dict[str, Any] = Field(..., description="Optimization result")
    execution_time: float = Field(..., description="Total execution time")
    message: Optional[str] = Field(None, description="Additional message")
    warnings: List[str] = Field(default_factory=list, description="Any warnings")

class BatchOptimizationResponse(BaseModel):
    success: bool = Field(..., description="Whether batch processing was successful")
    batch_id: str = Field(..., description="Batch identifier")
    total_tasks: int = Field(..., description="Total number of tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    failed_tasks: int = Field(..., description="Number of failed tasks")
    results: List[OptimizationResponse] = Field(..., description="Individual task results")
    summary: Dict[str, Any] = Field(..., description="Batch summary")

class ValidationResponse(BaseModel):
    success: bool = Field(..., description="Whether validation was successful")
    valid: bool = Field(..., description="Whether placements are valid")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Validation metrics")
    issues: List[str] = Field(default_factory=list, description="Validation issues found")
    message: str = Field(..., description="Validation message")

class ComparisonResponse(BaseModel):
    success: bool = Field(..., description="Whether comparison was successful")
    comparison: Dict[str, Any] = Field(..., description="Algorithm comparison results")
    recommendations: List[str] = Field(..., description="Algorithm recommendations")
    best_algorithm: str = Field(..., description="Best performing algorithm")
    results: Dict[str, OptimizationResponse] = Field(..., description="Individual algorithm results")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    timestamp: float = Field(..., description="Response timestamp")
    features: List[str] = Field(..., description="Available features")

class AlgorithmInfo(BaseModel):
    name: str = Field(..., description="Algorithm name")
    id: str = Field(..., description="Algorithm identifier")
    endpoint: str = Field(..., description="API endpoint")
    description: str = Field(..., description="Algorithm description")
    best_for: str = Field(..., description="Best use cases")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Algorithm parameters")

class ContainerTypeInfo(BaseModel):
    name: str = Field(..., description="Container type name")
    length: float = Field(..., description="Length in cm")
    width: float = Field(..., description="Width in cm")
    height: float = Field(..., description="Height in cm")
    max_weight: float = Field(..., description="Maximum weight in kg")
    volume: float = Field(..., description="Volume in cubic meters")
    description: str = Field(..., description="Container description")