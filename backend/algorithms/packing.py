"""
Core Packing Algorithms
Implements fundamental 3D bin packing algorithms and heuristics.
"""

from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import math

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class PackingHeuristic(Enum):
    """Packing heuristic strategies."""
    BEST_FIT = "best_fit"
    FIRST_FIT = "first_fit"
    BOTTOM_LEFT = "bottom_left"
    MAXIMUM_TOUCHING = "maximum_touching"
    GUILLOTINE = "guillotine"


@dataclass
class Placement:
    """
    Represents the placement of an item in the container.
    """
    item_index: int
    x: int  # Position in mm
    y: int
    z: int
    length: int  # Dimensions in mm after rotation
    width: int
    height: int
    rotation: int = 0  # Rotation angle (0, 90, 180, 270)
    weight: float = 0.0
    volume: float = field(init=False)
    
    def __post_init__(self):
        """Calculate volume after initialization."""
        self.volume = self.length * self.width * self.height
    
    def get_bounds(self) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """
        Get bounding box coordinates.
        
        Returns:
            ((min_x, min_y, min_z), (max_x, max_y, max_z))
        """
        return (
            (self.x, self.y, self.z),
            (self.x + self.length, self.y + self.width, self.z + self.height)
        )
    
    def overlaps(self, other: 'Placement') -> bool:
        """
        Check if this placement overlaps with another.
        
        Args:
            other: Another placement
            
        Returns:
            True if placements overlap
        """
        return not (
            self.x + self.length <= other.x or
            other.x + other.length <= self.x or
            self.y + self.width <= other.y or
            other.y + other.width <= self.y or
            self.z + self.height <= other.z or
            other.z + other.height <= self.z
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'item_index': self.item_index,
            'position': {'x': self.x, 'y': self.y, 'z': self.z},
            'dimensions': {'length': self.length, 'width': self.width, 'height': self.height},
            'rotation': self.rotation,
            'weight': self.weight,
            'volume': self.volume
        }


@dataclass
class Space:
    """
    Represents available space in the container.
    """
    x: int
    y: int
    z: int
    length: int
    width: int
    height: int
    
    def volume(self) -> int:
        """Calculate volume of this space."""
        return self.length * self.width * self.height
    
    def can_fit(self, item_length: int, item_width: int, item_height: int) -> bool:
        """Check if an item can fit in this space."""
        return (
            item_length <= self.length and
            item_width <= self.width and
            item_height <= self.height
        )
    
    def contains_point(self, x: int, y: int, z: int) -> bool:
        """Check if a point is within this space."""
        return (
            self.x <= x < self.x + self.length and
            self.y <= y < self.y + self.width and
            self.z <= z < self.z + self.height
        )


class PackingEngine:
    """
    Core packing engine implementing various 3D bin packing algorithms.
    """
    
    def __init__(self, container: Dict, items: List[Dict]):
        """
        Initialize packing engine.
        
        Args:
            container: Container specifications
            items: List of items to pack
        """
        self.container = container
        self.items = items
        self.placements = []
        self.available_spaces = [
            Space(
                x=0, y=0, z=0,
                length=container['length'],
                width=container['width'],
                height=container['height']
            )
        ]
    
    def pack(
        self,
        sequence: List[int],
        orientations: List[int],
        heuristic: PackingHeuristic = PackingHeuristic.BEST_FIT
    ) -> Dict[str, Any]:
        """
        Pack items according to sequence and orientations.
        
        Args:
            sequence: Order of items to pack (indices)
            orientations: Orientation for each item
            heuristic: Packing heuristic to use
            
        Returns:
            Dictionary with packing results
        """
        self.placements = []
        self.available_spaces = [
            Space(
                x=0, y=0, z=0,
                length=self.container['length'],
                width=self.container['width'],
                height=self.container['height']
            )
        ]
        
        packed_indices = []
        unpacked_indices = []
        violations = []
        
        for seq_idx, item_idx in enumerate(sequence):
            item = self.items[item_idx]
            orientation = orientations[seq_idx] if seq_idx < len(orientations) else 0
            
            # Get rotated dimensions
            dims = self._get_rotated_dimensions(item, orientation)
            
            # Try to place item
            placement = self._find_placement(
                item_idx, dims, item['weight'], heuristic
            )
            
            if placement:
                # Validate placement
                is_valid, item_violations = self._validate_placement(placement, item)
                
                if is_valid:
                    self.placements.append(placement)
                    packed_indices.append(item_idx)
                    self._update_spaces(placement)
                else:
                    violations.extend(item_violations)
                    unpacked_indices.append(item_idx)
            else:
                unpacked_indices.append(item_idx)
        
        # Calculate results
        utilization = self._calculate_utilization()
        
        return {
            'placements': self.placements,
            'packed_indices': packed_indices,
            'unpacked_indices': unpacked_indices,
            'utilization': utilization,
            'is_valid': len(violations) == 0,
            'violations': violations
        }
    
    def _get_rotated_dimensions(
        self,
        item: Dict,
        orientation: int
    ) -> Tuple[int, int, int]:
        """
        Get item dimensions after applying rotation.
        
        Args:
            item: Item dictionary
            orientation: Orientation index (0-5)
            
        Returns:
            (length, width, height) after rotation
        """
        l, w, h = item['length'], item['width'], item['height']
        
        # Check rotation constraints
        if item.get('keep_upright', False):
            return (l, w, h)  # No rotation
        
        if not item.get('rotation_allowed', True):
            return (l, w, h)  # No rotation
        
        # 6 possible orientations
        orientations = [
            (l, w, h),  # 0: original
            (l, h, w),  # 1: rotate around length axis
            (w, l, h),  # 2: rotate around height axis
            (w, h, l),  # 3: rotate 90° around two axes
            (h, l, w),  # 4: rotate differently
            (h, w, l),  # 5: rotate differently
        ]
        
        return orientations[orientation % 6]
    
    def _find_placement(
        self,
        item_idx: int,
        dimensions: Tuple[int, int, int],
        weight: float,
        heuristic: PackingHeuristic
    ) -> Optional[Placement]:
        """
        Find a suitable placement for an item.
        
        Args:
            item_idx: Item index
            dimensions: (length, width, height)
            weight: Item weight
            heuristic: Packing heuristic
            
        Returns:
            Placement object or None if no space found
        """
        length, width, height = dimensions
        
        if heuristic == PackingHeuristic.BEST_FIT:
            return self._best_fit_placement(item_idx, length, width, height, weight)
        elif heuristic == PackingHeuristic.BOTTOM_LEFT:
            return self._bottom_left_placement(item_idx, length, width, height, weight)
        else:
            return self._first_fit_placement(item_idx, length, width, height, weight)
    
    def _best_fit_placement(
        self,
        item_idx: int,
        length: int,
        width: int,
        height: int,
        weight: float
    ) -> Optional[Placement]:
        """
        Find best fitting space (minimum wasted volume).
        
        Args:
            item_idx: Item index
            length, width, height: Item dimensions
            weight: Item weight
            
        Returns:
            Placement or None
        """
        best_space = None
        best_waste = float('inf')
        
        for space in self.available_spaces:
            if space.can_fit(length, width, height):
                waste = space.volume() - (length * width * height)
                
                if waste < best_waste:
                    best_waste = waste
                    best_space = space
        
        if best_space:
            return Placement(
                item_index=item_idx,
                x=best_space.x,
                y=best_space.y,
                z=best_space.z,
                length=length,
                width=width,
                height=height,
                weight=weight
            )
        
        return None
    
    def _first_fit_placement(
        self,
        item_idx: int,
        length: int,
        width: int,
        height: int,
        weight: float
    ) -> Optional[Placement]:
        """
        Find first available space that fits.
        
        Args:
            item_idx: Item index
            length, width, height: Item dimensions
            weight: Item weight
            
        Returns:
            Placement or None
        """
        for space in self.available_spaces:
            if space.can_fit(length, width, height):
                return Placement(
                    item_index=item_idx,
                    x=space.x,
                    y=space.y,
                    z=space.z,
                    length=length,
                    width=width,
                    height=height,
                    weight=weight
                )
        
        return None
    
    def _bottom_left_placement(
        self,
        item_idx: int,
        length: int,
        width: int,
        height: int,
        weight: float
    ) -> Optional[Placement]:
        """
        Place item at lowest, leftmost, back-most position.
        
        Args:
            item_idx: Item index
            length, width, height: Item dimensions
            weight: Item weight
            
        Returns:
            Placement or None
        """
        # Sort spaces by z, then y, then x
        sorted_spaces = sorted(
            self.available_spaces,
            key=lambda s: (s.z, s.y, s.x)
        )
        
        for space in sorted_spaces:
            if space.can_fit(length, width, height):
                return Placement(
                    item_index=item_idx,
                    x=space.x,
                    y=space.y,
                    z=space.z,
                    length=length,
                    width=width,
                    height=height,
                    weight=weight
                )
        
        return None
    
    def _update_spaces(self, placement: Placement):
        """
        Update available spaces after placing an item.
        Uses guillotine cut approach.
        
        Args:
            placement: Newly placed item
        """
        new_spaces = []
        
        for space in self.available_spaces:
            # Check if placement intersects this space
            if self._placement_intersects_space(placement, space):
                # Split space around the placement
                splits = self._split_space(space, placement)
                new_spaces.extend(splits)
            else:
                # Keep space unchanged
                new_spaces.append(space)
        
        # Remove spaces that are completely inside other spaces
        self.available_spaces = self._remove_redundant_spaces(new_spaces)
        
        # Sort spaces (smaller first for better packing)
        self.available_spaces.sort(key=lambda s: (s.z, s.volume()))
    
    def _placement_intersects_space(self, placement: Placement, space: Space) -> bool:
        """Check if a placement intersects with a space."""
        return not (
            placement.x + placement.length <= space.x or
            space.x + space.length <= placement.x or
            placement.y + placement.width <= space.y or
            space.y + space.width <= placement.y or
            placement.z + placement.height <= space.z or
            space.z + space.height <= placement.z
        )
    
    def _split_space(self, space: Space, placement: Placement) -> List[Space]:
        """
        Split space around a placement using guillotine cuts.
        
        Args:
            space: Space to split
            placement: Placement dividing the space
            
        Returns:
            List of new spaces
        """
        splits = []
        
        # Right space
        if placement.x + placement.length < space.x + space.length:
            splits.append(Space(
                x=placement.x + placement.length,
                y=space.y,
                z=space.z,
                length=space.x + space.length - (placement.x + placement.length),
                width=space.width,
                height=space.height
            ))
        
        # Front space
        if placement.y + placement.width < space.y + space.width:
            splits.append(Space(
                x=space.x,
                y=placement.y + placement.width,
                z=space.z,
                length=space.length,
                width=space.y + space.width - (placement.y + placement.width),
                height=space.height
            ))
        
        # Top space
        if placement.z + placement.height < space.z + space.height:
            splits.append(Space(
                x=space.x,
                y=space.y,
                z=placement.z + placement.height,
                length=space.length,
                width=space.width,
                height=space.z + space.height - (placement.z + placement.height)
            ))
        
        return splits
    
    def _remove_redundant_spaces(self, spaces: List[Space]) -> List[Space]:
        """
        Remove spaces that are completely inside other spaces.
        
        Args:
            spaces: List of spaces
            
        Returns:
            Filtered list of spaces
        """
        filtered = []
        
        for i, space in enumerate(spaces):
            redundant = False
            
            for j, other in enumerate(spaces):
                if i != j and self._space_contains_space(other, space):
                    redundant = True
                    break
            
            if not redundant:
                filtered.append(space)
        
        return filtered
    
    def _space_contains_space(self, outer: Space, inner: Space) -> bool:
        """Check if outer space completely contains inner space."""
        return (
            outer.x <= inner.x and
            outer.y <= inner.y and
            outer.z <= inner.z and
            outer.x + outer.length >= inner.x + inner.length and
            outer.y + outer.width >= inner.y + inner.width and
            outer.z + outer.height >= inner.z + inner.height
        )
    
    def _validate_placement(
        self,
        placement: Placement,
        item: Dict
    ) -> Tuple[bool, List[str]]:
        """
        Validate a placement against constraints.
        
        Args:
            placement: Placement to validate
            item: Item dictionary
            
        Returns:
            (is_valid, list of violations)
        """
        violations = []
        
        # Check overlaps with existing placements
        for other in self.placements:
            if placement.overlaps(other):
                violations.append(f"Item overlaps with item {other.item_index}")
        
        # Check support (items must be supported from below)
        if placement.z > 0:
            if not self._has_adequate_support(placement):
                violations.append("Insufficient support from below")
        
        # Check stack weight limits
        if not item.get('stackable', True):
            # Check if anything would be on top
            pass  # Simplified for now
        
        # Check fragile items
        if item.get('fragile', False):
            # Should not have heavy items on top
            pass  # Simplified for now
        
        return len(violations) == 0, violations
    
    def _has_adequate_support(self, placement: Placement) -> bool:
        """
        Check if placement has adequate support from below.
        
        Args:
            placement: Placement to check
            
        Returns:
            True if adequately supported
        """
        if placement.z == 0:
            return True  # On container floor
        
        support_area = 0
        item_area = placement.length * placement.width
        
        for other in self.placements:
            # Check if other is directly below
            if abs(other.z + other.height - placement.z) < 1:
                # Calculate overlap area
                x_overlap = max(0, min(
                    placement.x + placement.length,
                    other.x + other.length
                ) - max(placement.x, other.x))
                
                y_overlap = max(0, min(
                    placement.y + placement.width,
                    other.y + other.width
                ) - max(placement.y, other.y))
                
                support_area += x_overlap * y_overlap
        
        # Require at least 60% support
        return support_area >= 0.6 * item_area
    
    def _calculate_utilization(self) -> float:
        """
        Calculate space utilization percentage.
        
        Returns:
            Utilization percentage
        """
        if not self.placements:
            return 0.0
        
        used_volume = sum(p.volume for p in self.placements)
        
        container_volume = (
            self.container['length'] *
            self.container['width'] *
            self.container['height']
        )
        
        return (used_volume / container_volume) * 100.0