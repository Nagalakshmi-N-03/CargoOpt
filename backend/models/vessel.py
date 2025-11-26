"""
SQLAlchemy Database Models for CargoOpt
These are the actual database table definitions.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.models.base import Base


# Enums
class ContainerTypeEnum(enum.Enum):
    STANDARD_20 = "20ft Standard"
    STANDARD_40 = "40ft Standard"
    HIGH_CUBE_40 = "40ft High Cube"
    HIGH_CUBE_45 = "45ft High Cube"
    REFRIGERATED_20 = "20ft Refrigerated"
    REFRIGERATED_40 = "40ft Refrigerated"
    OPEN_TOP_20 = "20ft Open Top"
    OPEN_TOP_40 = "40ft Open Top"
    FLAT_RACK_20 = "20ft Flat Rack"
    FLAT_RACK_40 = "40ft Flat Rack"
    TANK_20 = "20ft Tank"
    CUSTOM = "Custom"


class ItemTypeEnum(enum.Enum):
    STANDARD = "Standard"
    FRAGILE = "Fragile"
    HAZARDOUS = "Hazardous"
    PERISHABLE = "Perishable"
    VALUABLE = "Valuable"


class VesselTypeEnum(enum.Enum):
    FEEDER = "Feeder (< 3000 TEU)"
    PANAMAX = "Panamax (3000-5000 TEU)"
    POST_PANAMAX = "Post-Panamax (5000-10000 TEU)"
    NEW_PANAMAX = "New Panamax (10000-14500 TEU)"
    ULTRA_LARGE = "Ultra Large (> 14500 TEU)"


# Database Models
class ContainerDB(Base):
    """Container database model."""
    __tablename__ = 'containers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    container_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200))
    container_type = Column(SQLEnum(ContainerTypeEnum), nullable=False)
    
    # Dimensions (mm)
    length = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    
    # Capacity
    max_weight = Column(Float, nullable=False)
    tare_weight = Column(Float, nullable=False)
    
    # Properties
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Temperature control
    temperature_controlled = Column(Boolean, default=False)
    min_temperature = Column(Float)
    max_temperature = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = relationship("ItemDB", back_populates="container")
    stowage_positions = relationship("StowagePositionDB", back_populates="container")


class ItemDB(Base):
    """Item database model."""
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    item_type = Column(SQLEnum(ItemTypeEnum), default=ItemTypeEnum.STANDARD)
    
    # Dimensions (mm)
    length = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    
    # Weight
    weight = Column(Float, nullable=False)
    
    # Properties
    description = Column(Text)
    is_fragile = Column(Boolean, default=False)
    is_stackable = Column(Boolean, default=True)
    max_stack_weight = Column(Float)
    
    # Container assignment
    container_id = Column(Integer, ForeignKey('containers.id'))
    container = relationship("ContainerDB", back_populates="items")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class VesselDB(Base):
    """Vessel database model."""
    __tablename__ = 'vessels'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vessel_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    vessel_type = Column(SQLEnum(VesselTypeEnum), nullable=False)
    
    # Capacity
    teu_capacity = Column(Integer, nullable=False)
    max_weight_tons = Column(Float, nullable=False)
    
    # Dimensions
    length_m = Column(Float, nullable=False)
    width_m = Column(Float, nullable=False)
    draft_m = Column(Float, nullable=False)
    
    # Stowage configuration
    bays = Column(Integer, nullable=False)
    rows = Column(Integer, nullable=False)
    tiers_above_deck = Column(Integer, nullable=False)
    tiers_below_deck = Column(Integer, nullable=False)
    
    # Properties
    reefer_plugs = Column(Integer, default=0)
    max_speed_knots = Column(Float, default=20.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stowage_plans = relationship("StowagePlanDB", back_populates="vessel")


class StowagePlanDB(Base):
    """Stowage plan database model."""
    __tablename__ = 'stowage_plans'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(String(100), unique=True, nullable=False, index=True)
    voyage_number = Column(String(50), nullable=False)
    
    # Foreign keys
    vessel_id = Column(Integer, ForeignKey('vessels.id'), nullable=False)
    vessel = relationship("VesselDB", back_populates="stowage_plans")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))
    
    # Relationships
    positions = relationship("StowagePositionDB", back_populates="stowage_plan", cascade="all, delete-orphan")


class StowagePositionDB(Base):
    """Stowage position database model."""
    __tablename__ = 'stowage_positions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    stowage_plan_id = Column(Integer, ForeignKey('stowage_plans.id'), nullable=False)
    stowage_plan = relationship("StowagePlanDB", back_populates="positions")
    
    container_id = Column(Integer, ForeignKey('containers.id'), nullable=False)
    container = relationship("ContainerDB", back_populates="stowage_positions")
    
    # Position
    bay = Column(Integer, nullable=False)
    row = Column(Integer, nullable=False)
    tier = Column(Integer, nullable=False)
    is_above_deck = Column(Boolean, nullable=False)
    
    # Properties
    weight_kg = Column(Float, nullable=False)
    is_reefer = Column(Boolean, default=False)
    hazard_class = Column(String(20))


class UserDB(Base):
    """User database model for authentication."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    
    # Profile
    full_name = Column(String(200))
    company = Column(String(200))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)


class OptimizationRunDB(Base):
    """Optimization run tracking."""
    __tablename__ = 'optimization_runs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Parameters
    algorithm = Column(String(50), nullable=False)
    objective = Column(String(50))
    
    # Results
    status = Column(String(20), default='pending')  # pending, running, completed, failed
    utilization_percent = Column(Float)
    total_items = Column(Integer)
    packed_items = Column(Integer)
    execution_time_seconds = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    created_by = Column(String(100))
    
    # Error tracking
    error_message = Column(Text)