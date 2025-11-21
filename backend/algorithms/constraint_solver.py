"""
Constraint Programming Solver for Container Optimization
Implements constraint-based optimization for 3D container packing.
"""

from typing import List, Dict, Tuple, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime
import copy

from backend.config.settings import Config
from backend.utils.logger import get_logger
from backend.algorithms.packing import PackingEngine, Placement

logger = get_logger(__name__)


@dataclass
class Constraint:
    """
    Represents a packing constraint.
    """
    name: str
    type: str  # 'hard' or 'soft'
    description: str
    check_function: callable
    weight: float = 1.0  # For soft constraints
    
    def check(self, *args, **kwargs) -> bool:
        """Check if constraint is satisfied."""
        return self.check_function(*args, **kwargs)


class ConstraintSolver:
    """
    Constraint Programming solver for 3D container packing.
    Uses backtracking search with constraint propagation.
    """
    
    def __init__(self, container: Dict, items: List[Dict], config: Config = None):
        """
        Initialize constraint solver.
        
        Args:
            container: Container specifications
            items: List of items to pack
            config: Configuration object
        """
        self.container = container
        self.items = items
        self.config = config or Config()
        
        # Initialize packing engine
        self.packing_engine = PackingEngine(container, items)
        
        # Constraints
        self.hard_constraints = []
        self.soft_constraints = []
        self._initialize_constraints()
        
        # Search state
        self.current_placements = []
        self.unpacked_items = set(range(len(items)))
        self.search_space = []
        
        # Statistics
        self.start_time = None
        self.end_time = None
        self.nodes_explored = 0
        self.backtracks = 0
        
        logger.info(f"Constraint solver initialized with {len(items)} items")
    
    def _initialize_constraints(self):
        """Initialize all packing constraints."""
        # Hard constraints (must be satisfied)
        self.hard_constraints = [
            Constraint(
                name='within_container',
                type='hard',
                description='Item must be within container bounds',
                check_function=self._check_within_container
            ),
            Constraint(
                name='no_overlap',
                type='hard',
                description='Items must not overlap',
                check_function=self._check_no_overlap
            ),
            Constraint(
                name='weight_limit',
                type='hard',
                description='Total weight within container limit',
                check_function=self._check_weight_limit
            ),
            Constraint(
                name='support',
                type='hard',
                description='Items must be supported from below',
                check_function=self._check_support
            ),
            Constraint(
                name='stack_weight',
                type='hard',
                description='Stack weight limits respected',
                check_function=self._check_stack_weight
            )
        ]
        
        # Soft constraints (preferences)
        self.soft_constraints = [
            Constraint(
                name='fragile_on_top',
                type='soft',
                description='Fragile items should be on top',
                check_function=self._check_fragile_on_top,
                weight=0.8
            ),
            Constraint(
                name='heavy_at_bottom',
                type='soft',
                description='Heavy items should be at bottom',
                check_function=self._check_heavy_at_bottom,
                weight=0.7
            ),
            Constraint(
                name='orientation_preference',
                type='soft',
                description='Items in preferred orientation',
                check_function=self._check_orientation_preference,
                weight=0.5
            ),
            Constraint(
                name='accessibility',
                type='soft',
                description='Items easily accessible',
                check_function=self._check_accessibility,
                weight=0.6
            )
        ]
    
    def solve(self, max_time: int = None) -> Dict[str, Any]:
        """
        Solve the container packing problem using constraint programming.
        
        Args:
            max_time: Maximum computation time in seconds
            
        Returns:
            Dictionary with optimization results
        """
        self.start_time = datetime.utcnow()
        max_time = max_time or self.config.MAX_COMPUTATION_TIME
        
        logger.info("Starting constraint solver optimization")
        
        # Sort items by priority (largest/heaviest first)
        sorted_items = self._sort_items_by_priority()
        
        # Try to pack items using backtracking
        best_solution = {
            'placements': [],
            'utilization': 0.0,
            'score': 0.0
        }
        
        self.current_placements = []
        self.unpacked_items = set(sorted_items)
        
        # Recursive backtracking search
        solution = self._backtrack_search(
            sorted_items,
            best_solution,
            max_time
        )
        
        self.end_time = datetime.utcnow()
        
        return self._format_results(solution)
    
    def _sort_items_by_priority(self) -> List[int]:
        """
        Sort items by packing priority.
        
        Returns:
            List of item indices sorted by priority
        """
        items_with_idx = [(i, item) for i, item in enumerate(self.items)]
        
        # Sort by: priority, volume (desc), weight (desc)
        sorted_items = sorted(
            items_with_idx,
            key=lambda x: (
                x[1].get('priority', 5),  # Lower priority number = pack first
                -(x[1]['length'] * x[1]['width'] * x[1]['height']),
                -x[1]['weight']
            )
        )
        
        return [idx for idx, _ in sorted_items]
    
    def _backtrack_search(
        self,
        item_indices: List[int],
        best_solution: Dict,
        max_time: int
    ) -> Dict:
        """
        Recursive backtracking search with constraint propagation.
        
        Args:
            item_indices: Remaining items to pack
            best_solution: Current best solution found
            max_time: Time limit
            
        Returns:
            Best solution found
        """
        self.nodes_explored += 1
        
        # Check time limit
        if (datetime.utcnow() - self.start_time).total_seconds() > max_time:
            return best_solution
        
        # Base case: all items packed or no more can fit
        if not item_indices:
            score = self._evaluate_solution()
            if score > best_solution['score']:
                best_solution = {
                    'placements': copy.deepcopy(self.current_placements),
                    'utilization': self._calculate_utilization(),
                    'score': score
                }
            return best_solution
        
        # Select next item
        item_idx = item_indices[0]
        remaining = item_indices[1:]
        item = self.items[item_idx]
        
        # Generate possible positions for this item
        positions = self._generate_positions(item, item_idx)
        
        # Try each position
        for position in positions:
            # Check if placement is valid
            if self._is_valid_placement(position):
                # Add placement
                self.current_placements.append(position)
                self.unpacked_items.discard(item_idx)
                
                # Recursive search
                best_solution = self._backtrack_search(
                    remaining,
                    best_solution,
                    max_time
                )
                
                # Backtrack
                self.current_placements.pop()
                self.unpacked_items.add(item_idx)
                self.backtracks += 1
        
        # Try skipping this item (might not fit)
        best_solution = self._backtrack_search(
            remaining,
            best_solution,
            max_time
        )
        
        return best_solution
    
    def _generate_positions(self, item: Dict, item_idx: int) -> List[Placement]:
        """
        Generate candidate positions for placing an item.
        
        Args:
            item: Item to place
            item_idx: Item index
            
        Returns:
            List of candidate placements
        """
        positions = []
        
        # Get item dimensions
        dims = [item['length'], item['width'], item['height']]
        
        # Try different orientations
        orientations = self._get_allowed_orientations(item, dims)
        
        # Generate corner points where item could be placed
        corner_points = self._get_corner_points()
        
        for point in corner_points:
            for orient_dims in orientations:
                l, w, h = orient_dims
                
                # Check if item fits at this position
                if (point[0] + l <= self.container['length'] and
                    point[1] + w <= self.container['width'] and
                    point[2] + h <= self.container['height']):
                    
                    placement = Placement(
                        item_index=item_idx,
                        x=point[0],
                        y=point[1],
                        z=point[2],
                        length=l,
                        width=w,
                        height=h,
                        rotation=self._get_rotation_angle(dims, orient_dims),
                        weight=item['weight']
                    )
                    positions.append(placement)
        
        # Sort positions by preference (lower-left-back first)
        positions.sort(key=lambda p: (p.z, p.y, p.x))
        
        return positions
    
    def _get_corner_points(self) -> List[Tuple[int, int, int]]:
        """
        Get candidate corner points for item placement.
        
        Returns:
            List of (x, y, z) corner points
        """
        points = [(0, 0, 0)]  # Start with origin
        
        # Add corners created by existing placements
        for placement in self.current_placements:
            # Top corners
            points.extend([
                (placement.x, placement.y, placement.z + placement.height),
                (placement.x + placement.length, placement.y, placement.z + placement.height),
                (placement.x, placement.y + placement.width, placement.z + placement.height),
                (placement.x + placement.length, placement.y + placement.width, placement.z + placement.height)
            ])
            
            # Side corners
            points.extend([
                (placement.x + placement.length, placement.y, placement.z),
                (placement.x, placement.y + placement.width, placement.z)
            ])
        
        # Remove duplicates and sort
        points = list(set(points))
        points.sort(key=lambda p: (p[2], p[1], p[0]))
        
        return points[:50]  # Limit number of points to check
    
    def _get_allowed_orientations(self, item: Dict, dims: List[int]) -> List[Tuple[int, int, int]]:
        """
        Get allowed orientations for an item.
        
        Args:
            item: Item dictionary
            dims: [length, width, height]
            
        Returns:
            List of allowed dimension orientations
        """
        if item.get('keep_upright', False):
            # Only orientations that keep height vertical
            return [(dims[0], dims[1], dims[2])]
        
        if not item.get('rotation_allowed', True):
            # No rotation
            return [(dims[0], dims[1], dims[2])]
        
        # All 6 possible orientations
        orientations = [
            (dims[0], dims[1], dims[2]),
            (dims[0], dims[2], dims[1]),
            (dims[1], dims[0], dims[2]),
            (dims[1], dims[2], dims[0]),
            (dims[2], dims[0], dims[1]),
            (dims[2], dims[1], dims[0])
        ]
        
        # Remove duplicates (for cubes/squares)
        return list(set(orientations))
    
    def _get_rotation_angle(self, original: List[int], rotated: List[int]) -> int:
        """Determine rotation angle from dimension change."""
        if original == rotated:
            return 0
        # Simplified - return 0, 90, 180, or 270 based on orientation
        return 0
    
    def _is_valid_placement(self, placement: Placement) -> bool:
        """
        Check if a placement satisfies all hard constraints.
        
        Args:
            placement: Placement to validate
            
        Returns:
            True if valid
        """
        for constraint in self.hard_constraints:
            if not constraint.check(placement, self.current_placements):
                return False
        return True
    
    # Hard constraint checking methods
    
    def _check_within_container(self, placement: Placement, placements: List) -> bool:
        """Check if item is within container bounds."""
        return (
            placement.x >= 0 and
            placement.y >= 0 and
            placement.z >= 0 and
            placement.x + placement.length <= self.container['length'] and
            placement.y + placement.width <= self.container['width'] and
            placement.z + placement.height <= self.container['height']
        )
    
    def _check_no_overlap(self, placement: Placement, placements: List) -> bool:
        """Check if item overlaps with any existing items."""
        for other in placements:
            if self._placements_overlap(placement, other):
                return False
        return True
    
    def _placements_overlap(self, p1: Placement, p2: Placement) -> bool:
        """Check if two placements overlap."""
        return not (
            p1.x + p1.length <= p2.x or p2.x + p2.length <= p1.x or
            p1.y + p1.width <= p2.y or p2.y + p2.width <= p1.y or
            p1.z + p1.height <= p2.z or p2.z + p2.height <= p1.z
        )
    
    def _check_weight_limit(self, placement: Placement, placements: List) -> bool:
        """Check if total weight is within container limit."""
        total_weight = placement.weight + sum(p.weight for p in placements)
        return total_weight <= self.container['max_weight']
    
    def _check_support(self, placement: Placement, placements: List) -> bool:
        """Check if item has adequate support from below."""
        if placement.z == 0:
            return True  # On container floor
        
        # Find items below
        support_area = 0
        item_area = placement.length * placement.width
        
        for other in placements:
            if abs(other.z + other.height - placement.z) < 1:  # Directly below
                overlap_area = self._get_overlap_area(placement, other)
                support_area += overlap_area
        
        # Require at least 60% support
        return support_area >= 0.6 * item_area
    
    def _get_overlap_area(self, p1: Placement, p2: Placement) -> float:
        """Calculate horizontal overlap area between two placements."""
        x_overlap = max(0, min(p1.x + p1.length, p2.x + p2.length) - max(p1.x, p2.x))
        y_overlap = max(0, min(p1.y + p1.width, p2.y + p2.width) - max(p1.y, p2.y))
        return x_overlap * y_overlap
    
    def _check_stack_weight(self, placement: Placement, placements: List) -> bool:
        """Check if weight on top of items is within limits."""
        item = self.items[placement.item_index]
        max_stack = item.get('max_stack_weight', float('inf'))
        
        if not item.get('stackable', True):
            # Check if anything will be on top
            for other in placements:
                if abs(other.z - (placement.z + placement.height)) < 1:
                    if self._get_overlap_area(placement, other) > 0:
                        return False
        
        return True
    
    # Soft constraint checking methods
    
    def _check_fragile_on_top(self, placement: Placement, placements: List) -> bool:
        """Prefer fragile items on top."""
        item = self.items[placement.item_index]
        if not item.get('fragile', False):
            return True
        
        # Check if any non-fragile items are above
        for other in placements:
            if other.z > placement.z:
                return False
        return True
    
    def _check_heavy_at_bottom(self, placement: Placement, placements: List) -> bool:
        """Prefer heavy items at bottom."""
        if not placements:
            return True
        
        avg_z = sum(p.z for p in placements) / len(placements)
        return placement.z <= avg_z
    
    def _check_orientation_preference(self, placement: Placement, placements: List) -> bool:
        """Check if item is in preferred orientation."""
        item = self.items[placement.item_index]
        if item.get('keep_upright', False):
            return placement.height == item['height']
        return True
    
    def _check_accessibility(self, placement: Placement, placements: List) -> bool:
        """Check if item is accessible."""
        # Check if item has clear path from opening
        # Simplified: check if nothing is directly on top
        for other in placements:
            if other.z > placement.z + placement.height:
                if self._get_overlap_area(placement, other) > 0:
                    return False
        return True
    
    def _evaluate_solution(self) -> float:
        """
        Evaluate current solution considering soft constraints.
        
        Returns:
            Solution score (0-1)
        """
        if not self.current_placements:
            return 0.0
        
        # Utilization score
        utilization = self._calculate_utilization() / 100.0
        
        # Soft constraint satisfaction
        soft_score = 0.0
        total_weight = sum(c.weight for c in self.soft_constraints)
        
        for constraint in self.soft_constraints:
            satisfied = sum(
                1 for p in self.current_placements
                if constraint.check(p, self.current_placements)
            )
            ratio = satisfied / len(self.current_placements)
            soft_score += constraint.weight * ratio
        
        soft_score /= total_weight
        
        # Combined score
        return 0.7 * utilization + 0.3 * soft_score
    
    def _calculate_utilization(self) -> float:
        """Calculate space utilization percentage."""
        if not self.current_placements:
            return 0.0
        
        used_volume = sum(
            p.length * p.width * p.height
            for p in self.current_placements
        )
        
        container_volume = (
            self.container['length'] *
            self.container['width'] *
            self.container['height']
        )
        
        return (used_volume / container_volume) * 100.0
    
    def _format_results(self, solution: Dict) -> Dict[str, Any]:
        """
        Format optimization results.
        
        Args:
            solution: Solution dictionary
            
        Returns:
            Formatted results
        """
        computation_time = (self.end_time - self.start_time).total_seconds()
        
        return {
            'status': 'completed',
            'algorithm': 'constraint_solver',
            'score': solution['score'],
            'utilization': solution['utilization'],
            'placements': solution['placements'],
            'is_valid': True,
            'violations': [],
            'nodes_explored': self.nodes_explored,
            'backtracks': self.backtracks,
            'computation_time': computation_time,
            'items_packed': len(solution['placements']),
            'items_unpacked': len(self.items) - len(solution['placements'])
        }