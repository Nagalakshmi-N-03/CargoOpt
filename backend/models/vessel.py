"""
Vessel Model
Represents cargo vessels/ships for container transport.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime


class VesselType(Enum):
    """Types of cargo vessels."""
    FEEDER = "Feeder (< 3000 TEU)"
    PANAMAX = "Panamax (3000-5000 TEU)"
    POST_PANAMAX = "Post-Panamax (5000-10000 TEU)"
    NEW_PANAMAX = "New Panamax (10000-14500 TEU)"
    ULTRA_LARGE = "Ultra Large (> 14500 TEU)"


@dataclass
class Vessel:
    """Represents a cargo vessel."""
    
    vessel_id: str
    name: str
    vessel_type: VesselType
    
    # Capacity
    teu_capacity: int  # Twenty-foot Equivalent Unit capacity
    max_weight_tons: float
    
    # Dimensions
    length_m: float
    width_m: float
    draft_m: float
    
    # Stowage
    bays: int
    rows: int
    tiers_above_deck: int
    tiers_below_deck: int
    
    # Properties
    reefer_plugs: int = 0
    max_speed_knots: float = 20.0
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def total_slots(self) -> int:
        """Calculate total container slots."""
        return self.bays * self.rows * (self.tiers_above_deck + self.tiers_below_deck)
    
    def to_dict(self) -> Dict:
        return {
            'vessel_id': self.vessel_id,
            'name': self.name,
            'vessel_type': self.vessel_type.value,
            'teu_capacity': self.teu_capacity,
            'max_weight_tons': self.max_weight_tons,
            'dimensions': {
                'length_m': self.length_m,
                'width_m': self.width_m,
                'draft_m': self.draft_m
            },
            'stowage': {
                'bays': self.bays,
                'rows': self.rows,
                'tiers_above': self.tiers_above_deck,
                'tiers_below': self.tiers_below_deck,
                'total_slots': self.total_slots
            },
            'reefer_plugs': self.reefer_plugs,
            'max_speed_knots': self.max_speed_knots
        }