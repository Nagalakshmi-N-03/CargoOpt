"""
Container Model
Represents shipping containers with their specifications.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime


class ContainerType(Enum):
    """Standard container types."""
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


@dataclass
class Container:
    """
    Represents a shipping container.
    """
    
    # Identity
    container_id: str
    name: Optional[str] = None
    container_type: ContainerType = ContainerType.STANDARD_20
    
    # Dimensions (in mm)
    length: int = 5898  # 20ft container internal length
    width: int = 2352   # 20ft container internal width
    height: int = 2393  # 20ft container internal height
    
    # Capacity
    max_weight: float = 28180  # kg (max payload for 20ft)
    tare_weight: float = 2300  # kg (empty container weight)
    
    # Properties
    description: Optional[str] = None
    is_active: bool = True
    
    # Temperature control (for reefer containers)
    temperature_controlled: bool = False
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.container_type, str):
            self.container_type = ContainerType(self.container_type)
    
    @property
    def volume_m3(self) -> float:
        """Calculate internal volume in cubic meters."""
        return (self.length * self.width * self.height) / 1_000_000_000
    
    @property
    def volume_ft3(self) -> float:
        """Calculate internal volume in cubic feet."""
        return self.volume_m3 * 35.3147
    
    @property
    def gross_weight(self) -> float:
        """Calculate maximum gross weight."""
        return self.max_weight + self.tare_weight
    
    @classmethod
    def standard_20ft(cls, container_id: str) -> 'Container':
        """Create a standard 20ft container."""
        return cls(
            container_id=container_id,
            name="20ft Standard Container",
            container_type=ContainerType.STANDARD_20,
            length=5898,
            width=2352,
            height=2393,
            max_weight=28180,
            tare_weight=2300
        )
    
    @classmethod
    def standard_40ft(cls, container_id: str) -> 'Container':
        """Create a standard 40ft container."""
        return cls(
            container_id=container_id,
            name="40ft Standard Container",
            container_type=ContainerType.STANDARD_40,
            length=12032,
            width=2352,
            height=2393,
            max_weight=26680,
            tare_weight=3800
        )
    
    @classmethod
    def high_cube_40ft(cls, container_id: str) -> 'Container':
        """Create a 40ft high cube container."""
        return cls(
            container_id=container_id,
            name="40ft High Cube Container",
            container_type=ContainerType.HIGH_CUBE_40,
            length=12032,
            width=2352,
            height=2698,
            max_weight=26560,
            tare_weight=3920
        )
    
    @classmethod
    def refrigerated_20ft(cls, container_id: str) -> 'Container':
        """Create a 20ft refrigerated container."""
        return cls(
            container_id=container_id,
            name="20ft Refrigerated Container",
            container_type=ContainerType.REFRIGERATED_20,
            length=5444,
            width=2294,
            height=2276,
            max_weight=27400,
            tare_weight=3080,
            temperature_controlled=True,
            min_temperature=-25.0,
            max_temperature=25.0
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Container':
        """Create container from dictionary."""
        return cls(
            container_id=data.get('container_id', ''),
            name=data.get('name'),
            container_type=ContainerType(data.get('container_type', 'Custom')),
            length=data.get('length', 0),
            width=data.get('width', 0),
            height=data.get('height', 0),
            max_weight=data.get('max_weight', 0),
            tare_weight=data.get('tare_weight', 0),
            description=data.get('description'),
            temperature_controlled=data.get('temperature_controlled', False),
            min_temperature=data.get('min_temperature'),
            max_temperature=data.get('max_temperature')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert container to dictionary."""
        return {
            'container_id': self.container_id,
            'name': self.name,
            'container_type': self.container_type.value,
            'length': self.length,
            'width': self.width,
            'height': self.height,
            'max_weight': self.max_weight,
            'tare_weight': self.tare_weight,
            'volume_m3': self.volume_m3,
            'volume_ft3': self.volume_ft3,
            'gross_weight': self.gross_weight,
            'description': self.description,
            'is_active': self.is_active,
            'temperature_controlled': self.temperature_controlled,
            'min_temperature': self.min_temperature,
            'max_temperature': self.max_temperature,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def can_fit(self, length: int, width: int, height: int) -> bool:
        """
        Check if dimensions can fit in container.
        
        Args:
            length, width, height: Dimensions in mm
            
        Returns:
            True if dimensions can fit (considering rotation)
        """
        dims = sorted([length, width, height])
        container_dims = sorted([self.length, self.width, self.height])
        
        return all(d <= c for d, c in zip(dims, container_dims))
    
    def __repr__(self) -> str:
        return f"Container({self.container_id}, {self.container_type.value}, {self.length}x{self.width}x{self.height}mm)"