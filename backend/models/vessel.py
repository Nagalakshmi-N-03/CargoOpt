"""
Vessel Model
Represents cargo vessels with their specifications.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime


class VesselType(Enum):
    """Standard vessel types by capacity."""
    FEEDER = "Feeder (< 3000 TEU)"
    PANAMAX = "Panamax (3000-5000 TEU)"
    POST_PANAMAX = "Post-Panamax (5000-10000 TEU)"
    NEW_PANAMAX = "New Panamax (10000-14500 TEU)"
    ULTRA_LARGE = "Ultra Large (> 14500 TEU)"


@dataclass
class Vessel:
    """
    Represents a cargo vessel for container shipping.
    """
    
    # Identity
    vessel_id: str
    name: str
    vessel_type: VesselType = VesselType.FEEDER
    
    # Capacity
    teu_capacity: int = 1000  # Twenty-foot Equivalent Units
    max_weight_tons: float = 10000.0  # Maximum cargo weight in tons
    
    # Dimensions (in meters)
    length_m: float = 150.0
    width_m: float = 25.0
    draft_m: float = 10.0  # Maximum draft/depth
    
    # Stowage configuration
    bays: int = 10  # Number of bays (longitudinal)
    rows: int = 8   # Number of rows (transverse)
    tiers_above_deck: int = 4  # Tiers above deck
    tiers_below_deck: int = 6  # Tiers below deck
    
    # Special features
    reefer_plugs: int = 0  # Number of refrigerated container plugs
    max_speed_knots: float = 20.0  # Maximum speed in knots
    
    # Properties
    description: Optional[str] = None
    is_active: bool = True
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.vessel_type, str):
            self.vessel_type = VesselType(self.vessel_type)
    
    @property
    def total_tiers(self) -> int:
        """Calculate total number of tiers."""
        return self.tiers_above_deck + self.tiers_below_deck
    
    @property
    def total_slots(self) -> int:
        """Calculate theoretical maximum container slots."""
        return self.bays * self.rows * self.total_tiers
    
    @property
    def deadweight_tons(self) -> float:
        """Calculate approximate deadweight tonnage."""
        # Rough estimate: TEU capacity * 14 tons average per TEU
        return self.teu_capacity * 14.0
    
    @classmethod
    def feeder_vessel(cls, vessel_id: str, name: str) -> 'Vessel':
        """Create a small feeder vessel."""
        return cls(
            vessel_id=vessel_id,
            name=name,
            vessel_type=VesselType.FEEDER,
            teu_capacity=1000,
            max_weight_tons=12000,
            length_m=135.0,
            width_m=20.0,
            draft_m=8.0,
            bays=8,
            rows=6,
            tiers_above_deck=3,
            tiers_below_deck=5,
            reefer_plugs=50,
            max_speed_knots=18.0
        )
    
    @classmethod
    def panamax_vessel(cls, vessel_id: str, name: str) -> 'Vessel':
        """Create a Panamax vessel."""
        return cls(
            vessel_id=vessel_id,
            name=name,
            vessel_type=VesselType.PANAMAX,
            teu_capacity=4500,
            max_weight_tons=52000,
            length_m=294.0,
            width_m=32.2,
            draft_m=12.0,
            bays=17,
            rows=13,
            tiers_above_deck=5,
            tiers_below_deck=7,
            reefer_plugs=300,
            max_speed_knots=22.0
        )
    
    @classmethod
    def post_panamax_vessel(cls, vessel_id: str, name: str) -> 'Vessel':
        """Create a Post-Panamax vessel."""
        return cls(
            vessel_id=vessel_id,
            name=name,
            vessel_type=VesselType.POST_PANAMAX,
            teu_capacity=8000,
            max_weight_tons=100000,
            length_m=330.0,
            width_m=42.8,
            draft_m=14.5,
            bays=21,
            rows=17,
            tiers_above_deck=7,
            tiers_below_deck=9,
            reefer_plugs=500,
            max_speed_knots=24.0
        )
    
    @classmethod
    def ultra_large_vessel(cls, vessel_id: str, name: str) -> 'Vessel':
        """Create an Ultra Large Container Vessel (ULCV)."""
        return cls(
            vessel_id=vessel_id,
            name=name,
            vessel_type=VesselType.ULTRA_LARGE,
            teu_capacity=20000,
            max_weight_tons=200000,
            length_m=400.0,
            width_m=58.0,
            draft_m=16.0,
            bays=24,
            rows=23,
            tiers_above_deck=9,
            tiers_below_deck=11,
            reefer_plugs=1000,
            max_speed_knots=22.5
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vessel':
        """Create vessel from dictionary."""
        return cls(
            vessel_id=data.get('vessel_id', ''),
            name=data.get('name', ''),
            vessel_type=VesselType(data.get('vessel_type', VesselType.FEEDER.value)),
            teu_capacity=data.get('teu_capacity', 1000),
            max_weight_tons=data.get('max_weight_tons', 10000.0),
            length_m=data.get('length_m', 150.0),
            width_m=data.get('width_m', 25.0),
            draft_m=data.get('draft_m', 10.0),
            bays=data.get('bays', 10),
            rows=data.get('rows', 8),
            tiers_above_deck=data.get('tiers_above_deck', 4),
            tiers_below_deck=data.get('tiers_below_deck', 6),
            reefer_plugs=data.get('reefer_plugs', 0),
            max_speed_knots=data.get('max_speed_knots', 20.0),
            description=data.get('description'),
            is_active=data.get('is_active', True)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert vessel to dictionary."""
        return {
            'vessel_id': self.vessel_id,
            'name': self.name,
            'vessel_type': self.vessel_type.value,
            'capacity': {
                'teu_capacity': self.teu_capacity,
                'max_weight_tons': self.max_weight_tons,
                'deadweight_tons': self.deadweight_tons
            },
            'dimensions': {
                'length_m': self.length_m,
                'width_m': self.width_m,
                'draft_m': self.draft_m
            },
            'stowage_config': {
                'bays': self.bays,
                'rows': self.rows,
                'tiers_above_deck': self.tiers_above_deck,
                'tiers_below_deck': self.tiers_below_deck,
                'total_tiers': self.total_tiers,
                'total_slots': self.total_slots
            },
            'features': {
                'reefer_plugs': self.reefer_plugs,
                'max_speed_knots': self.max_speed_knots
            },
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def can_accommodate_reefers(self, count: int) -> bool:
        """Check if vessel can accommodate the number of refrigerated containers."""
        return count <= self.reefer_plugs
    
    def get_position_code(self, bay: int, row: int, tier: int, above_deck: bool) -> str:
        """
        Generate standard container position code (Bay-Row-Tier format).
        
        Args:
            bay: Bay number (1-based)
            row: Row number (1-based, odd numbers are centerline)
            tier: Tier number (1-based)
            above_deck: Whether position is above deck
            
        Returns:
            Position code in format BBRRTT
        """
        # Standard format: bay (2 digits), row (2 digits), tier (2 digits)
        # Below deck tiers typically use 02, 04, 06... 
        # Above deck tiers use 82, 84, 86...
        tier_code = tier * 2
        if above_deck:
            tier_code += 80
        
        return f"{bay:02d}{row:02d}{tier_code:02d}"
    
    def validate_position(self, bay: int, row: int, tier: int, above_deck: bool) -> tuple[bool, Optional[str]]:
        """
        Validate if a position is within vessel bounds.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if bay < 1 or bay > self.bays:
            return False, f"Bay {bay} out of range (1-{self.bays})"
        
        if row < 1 or row > self.rows:
            return False, f"Row {row} out of range (1-{self.rows})"
        
        max_tier = self.tiers_above_deck if above_deck else self.tiers_below_deck
        if tier < 1 or tier > max_tier:
            deck_type = "above deck" if above_deck else "below deck"
            return False, f"Tier {tier} out of range for {deck_type} (1-{max_tier})"
        
        return True, None
    
    def __repr__(self) -> str:
        return f"Vessel({self.vessel_id}, {self.name}, {self.vessel_type.value}, {self.teu_capacity} TEU)"