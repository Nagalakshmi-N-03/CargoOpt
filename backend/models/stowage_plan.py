"""
Stowage Plan Model
Represents container stowage plans for vessels.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class StowagePosition:
    """Represents a container's position in vessel stowage."""
    
    container_id: str
    bay: int
    row: int
    tier: int
    is_above_deck: bool
    weight_kg: float
    is_reefer: bool = False
    hazard_class: Optional[str] = None
    
    def to_bay_row_tier(self) -> str:
        """Get position in standard bay-row-tier format."""
        tier_str = f"{self.tier:02d}" if self.is_above_deck else f"{self.tier+80:02d}"
        return f"{self.bay:02d}{self.row:02d}{tier_str}"
    
    def to_dict(self) -> Dict:
        return {
            'container_id': self.container_id,
            'bay': self.bay,
            'row': self.row,
            'tier': self.tier,
            'position': self.to_bay_row_tier(),
            'is_above_deck': self.is_above_deck,
            'weight_kg': self.weight_kg,
            'is_reefer': self.is_reefer,
            'hazard_class': self.hazard_class
        }


@dataclass
class StowagePlan:
    """Represents a complete vessel stowage plan."""
    
    plan_id: str
    vessel_id: str
    voyage_number: str
    positions: List[StowagePosition] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    @property
    def total_containers(self) -> int:
        return len(self.positions)
    
    @property
    def total_weight(self) -> float:
        return sum(p.weight_kg for p in self.positions)
    
    @property
    def reefer_count(self) -> int:
        return sum(1 for p in self.positions if p.is_reefer)
    
    @property
    def hazmat_count(self) -> int:
        return sum(1 for p in self.positions if p.hazard_class)
    
    def get_bay_plan(self, bay: int) -> List[StowagePosition]:
        """Get all containers in a specific bay."""
        return [p for p in self.positions if p.bay == bay]
    
    def validate(self) -> tuple[bool, List[str]]:
        """Validate stowage plan."""
        errors = []
        
        # Check for duplicate positions
        positions_set = set()
        for pos in self.positions:
            pos_key = (pos.bay, pos.row, pos.tier, pos.is_above_deck)
            if pos_key in positions_set:
                errors.append(f"Duplicate position: {pos.to_bay_row_tier()}")
            positions_set.add(pos_key)
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict:
        return {
            'plan_id': self.plan_id,
            'vessel_id': self.vessel_id,
            'voyage_number': self.voyage_number,
            'statistics': {
                'total_containers': self.total_containers,
                'total_weight': self.total_weight,
                'reefer_count': self.reefer_count,
                'hazmat_count': self.hazmat_count
            },
            'positions': [p.to_dict() for p in self.positions],
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by
        }