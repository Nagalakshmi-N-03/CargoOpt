"""
Stowage Plan Models
Database models and classes for stowage planning
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, field_validator
from datetime import datetime
import enum

Base = declarative_base()


class StowagePlanStatus(enum.Enum):
    """Stowage plan status enumeration"""
    DRAFT = "draft"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class StowagePlan(Base):
    """Stowage plan database model"""
    __tablename__ = "stowage_plans"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Plan identification
    plan_number = Column(String(50), unique=True, index=True, nullable=False)
    vessel_id = Column(Integer, ForeignKey("vessels.id"), nullable=False)
    voyage_number = Column(String(50))
    
    # Status and timestamps
    status = Column(String(20), default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(String(100), nullable=True)
    
    # Port information
    loading_port = Column(String(100))
    discharge_port = Column(String(100))
    estimated_departure = Column(DateTime(timezone=True))
    estimated_arrival = Column(DateTime(timezone=True))
    
    # Optimization results
    total_containers = Column(Integer, default=0)
    total_weight = Column(Float, default=0.0)
    total_volume = Column(Float, default=0.0)
    utilization_rate = Column(Float, default=0.0)
    
    # Stability calculations
    calculated_gm = Column(Float, nullable=True)
    calculated_trim = Column(Float, nullable=True)
    is_stable = Column(Boolean, default=True)
    
    # Optimization metadata
    algorithm_used = Column(String(50))
    optimization_time = Column(Float, nullable=True)  # in seconds
    iterations_count = Column(Integer, nullable=True)
    
    # Additional data
    notes = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)  # CHANGED: renamed from 'metadata' to 'extra_data'
    
    # Relationships
    positions = relationship("StowagePosition", back_populates="stowage_plan", cascade="all, delete-orphan")


class StowagePosition(Base):
    """Stowage position database model - represents a container placement"""
    __tablename__ = "stowage_positions"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    stowage_plan_id = Column(Integer, ForeignKey("stowage_plans.id"), nullable=False)
    container_id = Column(Integer, nullable=False)
    compartment_id = Column(Integer, ForeignKey("vessel_compartments.id"), nullable=False)
    
    # Position details
    bay = Column(Integer, nullable=False)
    row = Column(Integer, nullable=False)
    tier = Column(Integer, nullable=False)
    
    # 3D coordinates
    position_x = Column(Float, nullable=False)
    position_y = Column(Float, nullable=False)
    position_z = Column(Float, nullable=False)
    
    # Container orientation
    rotation = Column(Integer, default=0)  # 0, 90, 180, 270 degrees
    
    # Loading sequence
    load_sequence = Column(Integer, nullable=True)
    discharge_sequence = Column(Integer, nullable=True)
    
    # Status
    is_loaded = Column(Boolean, default=False)
    is_discharged = Column(Boolean, default=False)
    
    # Timestamps
    loaded_at = Column(DateTime(timezone=True), nullable=True)
    discharged_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional info
    notes = Column(Text, nullable=True)
    
    # Relationships
    stowage_plan = relationship("StowagePlan", back_populates="positions")

    def get_position_code(self) -> str:
        """Generate position code (e.g., '010203' for bay1, row2, tier3)"""
        return f"{self.bay:02d}{self.row:02d}{self.tier:02d}"


class OptimizationResult(Base):
    """Optimization result database model - stores results of optimization runs"""
    __tablename__ = "optimization_results"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Algorithm information
    algorithm = Column(String(50), nullable=False, index=True)
    
    # Container/vessel reference
    container_id = Column(Integer, nullable=True)
    
    # Results
    utilization_rate = Column(Float, nullable=False)
    total_items_packed = Column(Integer, nullable=False)
    total_volume_used = Column(Float, nullable=False)
    total_weight_used = Column(Float, default=0.0)
    
    # Performance metrics
    execution_time = Column(Float, nullable=True)  # in seconds
    iterations_count = Column(Integer, nullable=True)
    
    # Detailed placement data (JSON)
    placement_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Additional metadata
    extra_data = Column(JSON, nullable=True)  # CHANGED: renamed from 'metadata' to 'extra_data'


# Pydantic models for API
class StowagePositionBase(BaseModel):
    """Base Pydantic model for stowage position"""
    container_id: int
    compartment_id: int
    bay: int
    row: int
    tier: int
    position_x: float
    position_y: float
    position_z: float
    rotation: int = 0
    load_sequence: Optional[int] = None
    discharge_sequence: Optional[int] = None
    notes: Optional[str] = None


class StowagePositionCreate(StowagePositionBase):
    """Pydantic model for creating a stowage position"""
    pass


class StowagePositionResponse(StowagePositionBase):
    """Pydantic model for stowage position API response"""
    id: int
    stowage_plan_id: int
    position_code: str
    is_loaded: bool
    is_discharged: bool
    loaded_at: Optional[datetime] = None
    discharged_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @field_validator('position_code', mode='before')
    @classmethod
    def generate_position_code(cls, v, info):
        """Generate position code from bay, row, tier numbers"""
        if v is not None:
            return v
        data = info.data
        bay = data.get('bay', 0)
        row = data.get('row', 0)
        tier = data.get('tier', 0)
        return f"{bay:02d}{row:02d}{tier:02d}"


class StowagePlanBase(BaseModel):
    """Base Pydantic model for stowage plan"""
    plan_number: str
    vessel_id: int
    voyage_number: Optional[str] = None
    loading_port: Optional[str] = None
    discharge_port: Optional[str] = None
    estimated_departure: Optional[datetime] = None
    estimated_arrival: Optional[datetime] = None
    algorithm_used: Optional[str] = None
    notes: Optional[str] = None


class StowagePlanCreate(StowagePlanBase):
    """Pydantic model for creating a stowage plan"""
    positions: List[StowagePositionCreate] = []


class StowagePlanUpdate(BaseModel):
    """Pydantic model for updating a stowage plan"""
    status: Optional[str] = None
    notes: Optional[str] = None
    approved_by: Optional[str] = None


class StowagePlanResponse(StowagePlanBase):
    """Pydantic model for stowage plan API response"""
    id: int
    status: str
    total_containers: int
    total_weight: float
    total_volume: float
    utilization_rate: float
    calculated_gm: Optional[float] = None
    calculated_trim: Optional[float] = None
    is_stable: bool
    optimization_time: Optional[float] = None
    iterations_count: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    positions: List[StowagePositionResponse] = []

    model_config = {"from_attributes": True}


class OptimizationResultResponse(BaseModel):
    """Pydantic model for optimization result API response"""
    id: int
    algorithm: str
    container_id: Optional[int] = None
    utilization_rate: float
    total_items_packed: int
    total_volume_used: float
    total_weight_used: float
    execution_time: Optional[float] = None
    iterations_count: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}