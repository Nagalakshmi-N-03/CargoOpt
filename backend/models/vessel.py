"""
Vessel Data Models
Vessel-related data structures and database models.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, validator
from datetime import datetime

Base = declarative_base()

class VesselType(enum.Enum):
    """Vessel types enumeration"""
    CONTAINER_SHIP = "container_ship"
    BULK_CARRIER = "bulk_carrier"
    TANKER = "tanker"
    RORO = "roro"
    GENERAL_CARGO = "general_cargo"
    LNG_CARRIER = "lng_carrier"

class Vessel(Base):
    """Vessel database model"""
    __tablename__ = "vessels"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Vessel identification
    imo_number = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    call_sign = Column(String(10))
    flag = Column(String(50))
    
    # Vessel type and category
    vessel_type = Column(Enum(VesselType), nullable=False)
    classification_society = Column(String(100))
    
    # Physical dimensions
    length_overall = Column(Float, nullable=False)  # in meters
    breadth = Column(Float, nullable=False)         # in meters
    depth = Column(Float, nullable=False)           # in meters
    draft_design = Column(Float, nullable=False)    # in meters
    draft_max = Column(Float, nullable=False)       # in meters
    
    # Capacity information
    deadweight_tonnage = Column(Float, nullable=False)  # in tons
    gross_tonnage = Column(Float, nullable=False)       # in tons
    net_tonnage = Column(Float, nullable=False)         # in tons
    teu_capacity = Column(Integer, nullable=False)      # TEU capacity
    reefer_plugs = Column(Integer)                      # Number of reefer plugs
    
    # Compartments and structure
    number_of_holds = Column(Integer)
    number_of_hatches = Column(Integer)
    
    # Operational data
    service_speed = Column(Float)  # in knots
    max_speed = Column(Float)      # in knots
    fuel_consumption = Column(JSON)  # Fuel consumption at different speeds
    
    # Stability and safety
    gm_min = Column(Float)  # Minimum metacentric height
    gm_max = Column(Float)  # Maximum metacentric height
    trim_max = Column(Float)  # Maximum trim in meters
    
    # Metadata
    built_year = Column(Integer)
    builder = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    additional_properties = Column(JSON)  # Flexible field for extra data
    
    # Relationships
    compartments = relationship("VesselCompartment", back_populates="vessel")

class VesselCompartment(Base):
    """Vessel compartment/bay database model"""
    __tablename__ = "vessel_compartments"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    vessel_id = Column(Integer, ForeignKey("vessels.id"), nullable=False)
    
    # Compartment identification
    bay_number = Column(Integer, nullable=False)      # Longitudinal position
    row_number = Column(Integer, nullable=False)      # Transverse position
    tier_number = Column(Integer, nullable=False)     # Vertical position
    
    # Physical properties
    length = Column(Float, nullable=False)  # in meters
    width = Column(Float, nullable=False)   # in meters
    height = Column(Float, nullable=False)  # in meters
    max_weight = Column(Float, nullable=False)  # in kg
    
    # Special capabilities
    can_accommodate_reefer = Column(Boolean, default=False)
    can_accommodate_hazardous = Column(Boolean, default=False)
    can_accommodate_oversized = Column(Boolean, default=False)
    has_power_supply = Column(Boolean, default=False)
    
    # Operational constraints
    is_occupied = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)  # For maintenance, etc.
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    vessel = relationship("Vessel", back_populates="compartments")

    def get_position_code(self) -> str:
        """Generate position code (e.g., '010203' for bay1, row2, tier3)"""
        return f"{self.bay_number:02d}{self.row_number:02d}{self.tier_number:02d}"

# Pydantic models for API
class VesselCompartmentBase(BaseModel):
    """Base Pydantic model for vessel compartment"""
    bay_number: int
    row_number: int
    tier_number: int
    length: float
    width: float
    height: float
    max_weight: float
    can_accommodate_reefer: bool = False
    can_accommodate_hazardous: bool = False
    can_accommodate_oversized: bool = False
    has_power_supply: bool = False
    is_occupied: bool = False
    is_blocked: bool = False

class VesselCompartmentCreate(VesselCompartmentBase):
    """Pydantic model for creating a vessel compartment"""
    pass

class VesselCompartmentResponse(VesselCompartmentBase):
    """Pydantic model for vessel compartment API response"""
    id: int
    vessel_id: int
    position_code: str
    created_at: datetime

    class Config:
        from_attributes = True

    @validator('position_code', always=True)
    def generate_position_code(cls, v, values):
        """Generate position code from bay, row, tier numbers"""
        bay = values.get('bay_number', 0)
        row = values.get('row_number', 0)
        tier = values.get('tier_number', 0)
        return f"{bay:02d}{row:02d}{tier:02d}"

class VesselBase(BaseModel):
    """Base Pydantic model for Vessel"""
    imo_number: str
    name: str
    vessel_type: VesselType
    length_overall: float
    breadth: float
    depth: float
    draft_design: float
    draft_max: float
    deadweight_tonnage: float
    gross_tonnage: float
    net_tonnage: float
    teu_capacity: int
    call_sign: Optional[str] = None
    flag: Optional[str] = None
    classification_society: Optional[str] = None
    reefer_plugs: Optional[int] = None
    number_of_holds: Optional[int] = None
    number_of_hatches: Optional[int] = None
    service_speed: Optional[float] = None
    max_speed: Optional[float] = None
    gm_min: Optional[float] = None
    gm_max: Optional[float] = None
    trim_max: Optional[float] = None
    built_year: Optional[int] = None
    builder: Optional[str] = None

class VesselCreate(VesselBase):
    """Pydantic model for creating a vessel"""
    pass

class VesselUpdate(BaseModel):
    """Pydantic model for updating a vessel"""
    name: Optional[str] = None
    service_speed: Optional[float] = None
    max_speed: Optional[float] = None
    fuel_consumption: Optional[Dict[str, Any]] = None

class VesselResponse(VesselBase):
    """Pydantic model for vessel API response"""
    id: int
    compartments: List[VesselCompartmentResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        use_enum_values = True