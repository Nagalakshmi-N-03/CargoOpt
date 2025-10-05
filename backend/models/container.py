"""
Container Data Models
Container-related data structures and database models.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Text, JSON
from sqlalchemy.sql import func
import enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, field_validator
from datetime import datetime

# Import shared Base from database config
from backend.config.database import Base

class ContainerType(enum.Enum):
    """Container types enumeration"""
    DRY = "dry"
    REEFER = "reefer"
    TANK = "tank"
    FLATRACK = "flatrack"
    OPEN_TOP = "open_top"
    HIGH_CUBE = "high_cube"
    VENTILATED = "ventilated"
    HAZARDOUS = "hazardous"

class ContainerStatus(enum.Enum):
    """Container status enumeration"""
    EMPTY = "empty"
    LOADED = "loaded"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    DAMAGED = "damaged"

class Container(Base):
    """Container database model"""
    __tablename__ = "containers"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Container identification
    container_number = Column(String(20), unique=True, index=True, nullable=False)
    iso_code = Column(String(4), nullable=False)  # e.g., 22G1, 42G1, etc.
    
    # Physical properties
    length = Column(Float, nullable=False)  # in feet (20, 40, 45)
    width = Column(Float, nullable=False)   # in feet
    height = Column(Float, nullable=False)  # in feet
    tare_weight = Column(Float, nullable=False)  # in kg
    max_payload = Column(Float, nullable=False)  # in kg
    gross_weight = Column(Float)  # in kg (tare + payload)
    
    # Container type and category
    container_type = Column(Enum(ContainerType), nullable=False)
    status = Column(Enum(ContainerStatus), default=ContainerStatus.EMPTY)
    
    # Cargo information
    cargo_description = Column(Text)
    cargo_weight = Column(Float)  # in kg
    imdg_class = Column(String(10))  # IMDG classification for hazardous goods
    un_number = Column(String(4))   # UN number for hazardous goods
    
    # Special requirements
    is_reefer = Column(Boolean, default=False)
    reefer_temperature = Column(Float)  # in Celsius
    is_oversized = Column(Boolean, default=False)
    requires_power = Column(Boolean, default=False)
    
    # Location and tracking
    current_location = Column(String(100))
    destination_port = Column(String(100))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    additional_properties = Column(JSON)  # Flexible field for extra data

    def calculate_gross_weight(self) -> float:
        """Calculate gross weight (tare + cargo weight)"""
        return self.tare_weight + (self.cargo_weight or 0)

    def is_overweight(self) -> bool:
        """Check if container exceeds maximum payload"""
        return (self.cargo_weight or 0) > self.max_payload

    def is_hazardous(self) -> bool:
        """Check if container carries hazardous goods"""
        return self.imdg_class is not None

# Pydantic models for API
class ContainerBase(BaseModel):
    """Base Pydantic model for Container"""
    container_number: str
    iso_code: str
    length: float
    width: float
    height: float
    tare_weight: float
    max_payload: float
    container_type: ContainerType
    cargo_description: Optional[str] = None
    cargo_weight: Optional[float] = None
    imdg_class: Optional[str] = None
    un_number: Optional[str] = None
    is_reefer: bool = False
    reefer_temperature: Optional[float] = None
    is_oversized: bool = False
    requires_power: bool = False
    current_location: Optional[str] = None
    destination_port: Optional[str] = None

class ContainerCreate(ContainerBase):
    """Pydantic model for creating a container"""
    pass

class ContainerUpdate(BaseModel):
    """Pydantic model for updating a container"""
    cargo_description: Optional[str] = None
    cargo_weight: Optional[float] = None
    status: Optional[ContainerStatus] = None
    current_location: Optional[str] = None
    destination_port: Optional[str] = None

class ContainerResponse(ContainerBase):
    """Pydantic model for container API response"""
    id: int
    gross_weight: float
    status: ContainerStatus
    is_overweight: bool
    is_hazardous: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True, "use_enum_values": True}

    @field_validator('gross_weight', mode='before')
    @classmethod
    def calculate_gross_weight(cls, v, info):
        """Calculate gross weight for response"""
        if v is not None:
            return v
        data = info.data
        tare_weight = data.get('tare_weight', 0)
        cargo_weight = data.get('cargo_weight', 0) or 0
        return tare_weight + cargo_weight

    @field_validator('is_overweight', mode='before')
    @classmethod
    def check_overweight(cls, v, info):
        """Check if container is overweight"""
        if v is not None:
            return v
        data = info.data
        cargo_weight = data.get('cargo_weight', 0) or 0
        max_payload = data.get('max_payload', 0)
        return cargo_weight > max_payload

    @field_validator('is_hazardous', mode='before')
    @classmethod
    def check_hazardous(cls, v, info):
        """Check if container is hazardous"""
        if v is not None:
            return v
        data = info.data
        return data.get('imdg_class') is not None