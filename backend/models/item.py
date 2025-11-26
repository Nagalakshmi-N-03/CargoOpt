"""
Item Model
Represents cargo items to be loaded into containers.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime


class ItemType(Enum):
    """Types of cargo items."""
    STANDARD = "Standard"
    FRAGILE = "Fragile"
    HAZARDOUS = "Hazardous"
    PERISHABLE = "Perishable"
    VALUABLE = "Valuable"
    OVERSIZED = "Oversized"


@dataclass
class Item:
    """
    Represents a cargo item to be packed.
    """
    
    # Identity
    item_id: str
    name: str
    item_type: ItemType = ItemType.STANDARD
    
    # Dimensions (in mm)
    length: int = 1000
    width: int = 1000
    height: int = 1000
    
    # Weight (in kg)
    weight: float = 100.0
    
    # Properties
    description: Optional[str] = None
    is_fragile: bool = False
    is_stackable: bool = True
    max_stack_weight: Optional[float] = None  # Max weight that can be placed on top
    
    # Hazmat information
    hazard_class: Optional[str] = None
    un_number: Optional[str] = None
    
    # Temperature requirements (for perishables)
    requires_temperature_control: bool = False
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    
    # Value (for insurance/priority)
    declared_value: Optional[float] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.item_type, str):
            self.item_type = ItemType(self.item_type)
        
        # Set fragile if item type is fragile
        if self.item_type == ItemType.FRAGILE:
            self.is_fragile = True
        
        # Set temperature control for perishables
        if self.item_type == ItemType.PERISHABLE:
            self.requires_temperature_control = True
            if self.min_temperature is None:
                self.min_temperature = 2.0
            if self.max_temperature is None:
                self.max_temperature = 8.0
    
    @property
    def volume_m3(self) -> float:
        """Calculate volume in cubic meters."""
        return (self.length * self.width * self.height) / 1_000_000_000
    
    @property
    def volume_ft3(self) -> float:
        """Calculate volume in cubic feet."""
        return self.volume_m3 * 35.3147
    
    @property
    def density(self) -> float:
        """Calculate density in kg/m³."""
        volume = self.volume_m3
        return self.weight / volume if volume > 0 else 0
    
    @property
    def is_hazmat(self) -> bool:
        """Check if item is hazardous material."""
        return self.item_type == ItemType.HAZARDOUS or self.hazard_class is not None
    
    def can_stack_on(self, other: 'Item') -> bool:
        """
        Check if this item can be stacked on top of another item.
        
        Args:
            other: The item below
            
        Returns:
            True if this item can be stacked on the other item
        """
        if not other.is_stackable:
            return False
        
        if self.is_fragile:
            return False
        
        if other.max_stack_weight is not None:
            return self.weight <= other.max_stack_weight
        
        return True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """Create item from dictionary."""
        return cls(
            item_id=data.get('item_id', ''),
            name=data.get('name', ''),
            item_type=ItemType(data.get('item_type', 'Standard')),
            length=data.get('length', 1000),
            width=data.get('width', 1000),
            height=data.get('height', 1000),
            weight=data.get('weight', 100.0),
            description=data.get('description'),
            is_fragile=data.get('is_fragile', False),
            is_stackable=data.get('is_stackable', True),
            max_stack_weight=data.get('max_stack_weight'),
            hazard_class=data.get('hazard_class'),
            un_number=data.get('un_number'),
            requires_temperature_control=data.get('requires_temperature_control', False),
            min_temperature=data.get('min_temperature'),
            max_temperature=data.get('max_temperature'),
            declared_value=data.get('declared_value')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary."""
        return {
            'item_id': self.item_id,
            'name': self.name,
            'item_type': self.item_type.value,
            'dimensions': {
                'length': self.length,
                'width': self.width,
                'height': self.height
            },
            'weight': self.weight,
            'volume_m3': self.volume_m3,
            'volume_ft3': self.volume_ft3,
            'density': self.density,
            'description': self.description,
            'is_fragile': self.is_fragile,
            'is_stackable': self.is_stackable,
            'max_stack_weight': self.max_stack_weight,
            'is_hazmat': self.is_hazmat,
            'hazard_class': self.hazard_class,
            'un_number': self.un_number,
            'requires_temperature_control': self.requires_temperature_control,
            'min_temperature': self.min_temperature,
            'max_temperature': self.max_temperature,
            'declared_value': self.declared_value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create_standard(cls, item_id: str, name: str, 
                       length: int, width: int, height: int, 
                       weight: float) -> 'Item':
        """Create a standard item with basic dimensions."""
        return cls(
            item_id=item_id,
            name=name,
            item_type=ItemType.STANDARD,
            length=length,
            width=width,
            height=height,
            weight=weight
        )
    
    @classmethod
    def create_fragile(cls, item_id: str, name: str,
                      length: int, width: int, height: int,
                      weight: float) -> 'Item':
        """Create a fragile item that cannot be stacked."""
        return cls(
            item_id=item_id,
            name=name,
            item_type=ItemType.FRAGILE,
            length=length,
            width=width,
            height=height,
            weight=weight,
            is_fragile=True,
            is_stackable=False
        )
    
    @classmethod
    def create_hazmat(cls, item_id: str, name: str,
                     length: int, width: int, height: int,
                     weight: float, hazard_class: str, un_number: str) -> 'Item':
        """Create a hazardous material item."""
        return cls(
            item_id=item_id,
            name=name,
            item_type=ItemType.HAZARDOUS,
            length=length,
            width=width,
            height=height,
            weight=weight,
            hazard_class=hazard_class,
            un_number=un_number
        )
    
    def __repr__(self) -> str:
        return f"Item({self.item_id}, {self.name}, {self.length}x{self.width}x{self.height}mm, {self.weight}kg)"