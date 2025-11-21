"""
Container Stowage Planning
Implements maritime container stowage rules and optimization.
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum

from backend.utils.logger import get_logger
from backend.algorithms.packing import Placement

logger = get_logger(__name__)


class HazardCompatibility(Enum):
    """Hazard class compatibility levels."""
    COMPATIBLE = "compatible"
    SEPARATED = "separated"  # Must be separated by one container
    SEGREGATED = "segregated"  # Must be in different bays
    PROHIBITED = "prohibited"  # Cannot be on same vessel


@dataclass
class StowageRule:
    """
    Represents a stowage rule or constraint.
    """
    name: str
    rule_type: str  # 'imdg', 'weight', 'refrigeration', 'accessibility'
    severity: str  # 'critical', 'warning', 'info'
    description: str
    check_function: callable
    
    def check(self, *args, **kwargs) -> Tuple[bool, Optional[str]]:
        """
        Check if rule is satisfied.
        
        Returns:
            (is_satisfied, violation_message)
        """
        return self.check_function(*args, **kwargs)


class StowageRules:
    """
    Container stowage rules based on IMDG Code and maritime standards.
    """
    
    # IMDG hazard class segregation table (simplified)
    SEGREGATION_TABLE = {
        # Class: {incompatible_classes: segregation_level}
        '1': {'1': 'separated', '2.1': 'segregated', '3': 'separated', '4.1': 'separated'},
        '2.1': {'1': 'segregated', '3': 'separated', '4.1': 'separated', '4.2': 'segregated'},
        '2.2': {},  # Generally compatible
        '2.3': {'3': 'separated', '4.1': 'separated', '6.1': 'separated', '8': 'separated'},
        '3': {'1': 'separated', '2.1': 'separated', '4.1': 'compatible', '5.1': 'separated'},
        '4.1': {'1': 'separated', '2.1': 'separated', '5.1': 'separated'},
        '4.2': {'2.1': 'segregated', '5.1': 'segregated', '8': 'separated'},
        '4.3': {'3': 'separated', '5.1': 'segregated', '8': 'separated'},
        '5.1': {'3': 'separated', '4.1': 'separated', '4.2': 'segregated', '4.3': 'segregated'},
        '5.2': {'1': 'segregated', '2.1': 'segregated', '4.1': 'segregated'},
        '6.1': {'2.3': 'separated', '3': 'compatible', '8': 'compatible'},
        '6.2': {},  # Special handling
        '7': {},  # Special handling
        '8': {'2.3': 'separated', '4.2': 'separated', '4.3': 'separated'},
        '9': {}  # Miscellaneous
    }
    
    @staticmethod
    def get_segregation_requirement(class1: str, class2: str) -> str:
        """
        Get segregation requirement between two hazard classes.
        
        Args:
            class1: First hazard class
            class2: Second hazard class
            
        Returns:
            Segregation level: 'compatible', 'separated', 'segregated', 'prohibited'
        """
        if class1 == class2:
            # Same class compatibility depends on specific substances
            return 'compatible'
        
        # Check segregation table
        if class1 in StowageRules.SEGREGATION_TABLE:
            incompatible = StowageRules.SEGREGATION_TABLE[class1]
            if class2 in incompatible:
                return incompatible[class2]
        
        if class2 in StowageRules.SEGREGATION_TABLE:
            incompatible = StowageRules.SEGREGATION_TABLE[class2]
            if class1 in incompatible:
                return incompatible[class1]
        
        return 'compatible'
    
    @staticmethod
    def calculate_segregation_distance(segregation: str, container_length: int) -> int:
        """
        Calculate required horizontal segregation distance.
        
        Args:
            segregation: Segregation level
            container_length: Container length in mm
            
        Returns:
            Required distance in mm
        """
        if segregation == 'separated':
            return container_length  # One container length
        elif segregation == 'segregated':
            return container_length * 2  # Two container lengths
        elif segregation == 'prohibited':
            return float('inf')
        else:
            return 0  # Compatible


class StowagePlanner:
    """
    Maritime container stowage planner with IMDG compliance.
    """
    
    def __init__(self, container: Dict, items: List[Dict]):
        """
        Initialize stowage planner.
        
        Args:
            container: Container specifications
            items: List of items/cargo to stow
        """
        self.container = container
        self.items = items
        self.rules = self._initialize_rules()
        
        # Categorize items
        self.hazardous_items = []
        self.refrigerated_items = []
        self.heavy_items = []
        self.fragile_items = []
        
        self._categorize_items()
        
        logger.info(f"Stowage planner initialized: "
                   f"{len(self.hazardous_items)} hazardous, "
                   f"{len(self.refrigerated_items)} refrigerated")
    
    def _initialize_rules(self) -> List[StowageRule]:
        """
        Initialize stowage rules.
        
        Returns:
            List of stowage rules
        """
        return [
            StowageRule(
                name='hazard_segregation',
                rule_type='imdg',
                severity='critical',
                description='Hazardous materials must be properly segregated',
                check_function=self._check_hazard_segregation
            ),
            StowageRule(
                name='weight_distribution',
                rule_type='weight',
                severity='critical',
                description='Weight must be properly distributed',
                check_function=self._check_weight_distribution
            ),
            StowageRule(
                name='refrigeration_grouping',
                rule_type='refrigeration',
                severity='warning',
                description='Refrigerated items should be grouped',
                check_function=self._check_refrigeration_grouping
            ),
            StowageRule(
                name='heavy_on_bottom',
                rule_type='weight',
                severity='critical',
                description='Heavy items must be on bottom',
                check_function=self._check_heavy_on_bottom
            ),
            StowageRule(
                name='fragile_protection',
                rule_type='accessibility',
                severity='warning',
                description='Fragile items must be protected',
                check_function=self._check_fragile_protection
            ),
            StowageRule(
                name='stack_limits',
                rule_type='weight',
                severity='critical',
                description='Stacking limits must be respected',
                check_function=self._check_stack_limits
            ),
            StowageRule(
                name='accessibility',
                rule_type='accessibility',
                severity='info',
                description='Items should be accessible for inspection',
                check_function=self._check_accessibility
            )
        ]
    
    def _categorize_items(self):
        """Categorize items by special requirements."""
        for i, item in enumerate(self.items):
            # Hazardous
            if item.get('hazard_class'):
                self.hazardous_items.append(i)
            
            # Refrigerated
            if item.get('storage_condition') in ['refrigerated', 'frozen']:
                self.refrigerated_items.append(i)
            
            # Heavy (>1000 kg)
            if item.get('weight', 0) > 1000:
                self.heavy_items.append(i)
            
            # Fragile
            if item.get('fragile', False):
                self.fragile_items.append(i)
    
    def validate_stowage(self, placements: List[Placement]) -> Tuple[bool, List[Dict]]:
        """
        Validate stowage plan against all rules.
        
        Args:
            placements: List of item placements
            
        Returns:
            (is_valid, list of violations)
        """
        violations = []
        
        for rule in self.rules:
            is_satisfied, message = rule.check(placements, self.items, self.container)
            
            if not is_satisfied:
                violations.append({
                    'rule': rule.name,
                    'type': rule.rule_type,
                    'severity': rule.severity,
                    'message': message
                })
        
        is_valid = not any(v['severity'] == 'critical' for v in violations)
        
        return is_valid, violations
    
    def optimize_stowage(self, placements: List[Placement]) -> List[Placement]:
        """
        Optimize stowage plan to improve compliance and efficiency.
        
        Args:
            placements: Initial placements
            
        Returns:
            Optimized placements
        """
        # Sort placements by priority
        sorted_placements = self._prioritize_placements(placements)
        
        # Apply stowage optimizations
        optimized = self._apply_weight_distribution(sorted_placements)
        optimized = self._apply_hazard_separation(optimized)
        optimized = self._apply_refrigeration_grouping(optimized)
        
        return optimized
    
    def _prioritize_placements(self, placements: List[Placement]) -> List[Placement]:
        """
        Prioritize placements based on stowage requirements.
        
        Args:
            placements: Original placements
            
        Returns:
            Prioritized placements
        """
        # Priority order:
        # 1. Hazardous items (need special positioning)
        # 2. Heavy items (need bottom placement)
        # 3. Refrigerated items (need grouping)
        # 4. Fragile items (need top placement)
        # 5. Regular items
        
        def get_priority(placement: Placement) -> Tuple:
            item = self.items[placement.item_index]
            
            return (
                1 if item.get('hazard_class') else 5,
                -item.get('weight', 0),  # Heavier first
                1 if item.get('storage_condition') in ['refrigerated', 'frozen'] else 3,
                5 if item.get('fragile') else 1
            )
        
        return sorted(placements, key=get_priority)
    
    # Rule checking methods
    
    def _check_hazard_segregation(
        self,
        placements: List[Placement],
        items: List[Dict],
        container: Dict
    ) -> Tuple[bool, Optional[str]]:
        """Check hazardous material segregation."""
        hazmat_placements = [
            p for p in placements
            if items[p.item_index].get('hazard_class')
        ]
        
        for i, p1 in enumerate(hazmat_placements):
            item1 = items[p1.item_index]
            class1 = item1.get('hazard_class')
            
            for p2 in hazmat_placements[i+1:]:
                item2 = items[p2.item_index]
                class2 = item2.get('hazard_class')
                
                # Get required segregation
                segregation = StowageRules.get_segregation_requirement(class1, class2)
                
                if segregation == 'prohibited':
                    return False, f"Classes {class1} and {class2} cannot be together"
                
                # Calculate actual distance
                distance = self._calculate_horizontal_distance(p1, p2)
                required = StowageRules.calculate_segregation_distance(
                    segregation, container['length']
                )
                
                if distance < required:
                    return False, (f"Insufficient segregation between {class1} and {class2}: "
                                 f"{distance}mm < {required}mm required")
        
        return True, None
    
    def _check_weight_distribution(
        self,
        placements: List[Placement],
        items: List[Dict],
        container: Dict
    ) -> Tuple[bool, Optional[str]]:
        """Check weight distribution and center of gravity."""
        if not placements:
            return True, None
        
        # Calculate center of gravity
        total_weight = sum(p.weight for p in placements)
        
        if total_weight == 0:
            return True, None
        
        cog_x = sum(p.weight * (p.x + p.length/2) for p in placements) / total_weight
        cog_y = sum(p.weight * (p.y + p.width/2) for p in placements) / total_weight
        cog_z = sum(p.weight * (p.z + p.height/2) for p in placements) / total_weight
        
        # Check if COG is within acceptable range
        container_center_x = container['length'] / 2
        container_center_y = container['width'] / 2
        
        # COG should be within 20% of center horizontally
        tolerance_x = container['length'] * 0.2
        tolerance_y = container['width'] * 0.2
        
        if abs(cog_x - container_center_x) > tolerance_x:
            return False, f"COG X-axis offset too large: {abs(cog_x - container_center_x):.0f}mm"
        
        if abs(cog_y - container_center_y) > tolerance_y:
            return False, f"COG Y-axis offset too large: {abs(cog_y - container_center_y):.0f}mm"
        
        # COG should be in lower half
        if cog_z > container['height'] * 0.6:
            return False, f"COG too high: {cog_z:.0f}mm (max {container['height'] * 0.6:.0f}mm)"
        
        return True, None
    
    def _check_refrigeration_grouping(
        self,
        placements: List[Placement],
        items: List[Dict],
        container: Dict
    ) -> Tuple[bool, Optional[str]]:
        """Check if refrigerated items are grouped together."""
        reefer_placements = [
            p for p in placements
            if items[p.item_index].get('storage_condition') in ['refrigerated', 'frozen']
        ]
        
        if len(reefer_placements) <= 1:
            return True, None
        
        # Calculate average position
        avg_x = sum(p.x for p in reefer_placements) / len(reefer_placements)
        avg_y = sum(p.y for p in reefer_placements) / len(reefer_placements)
        
        # Check if all are within reasonable distance
        max_distance = container['length'] * 0.3  # 30% of container length
        
        for p in reefer_placements:
            distance = ((p.x - avg_x)**2 + (p.y - avg_y)**2)**0.5
            if distance > max_distance:
                return False, "Refrigerated items should be grouped closer together"
        
        return True, None
    
    def _check_heavy_on_bottom(
        self,
        placements: List[Placement],
        items: List[Dict],
        container: Dict
    ) -> Tuple[bool, Optional[str]]:
        """Check if heavy items are at the bottom."""
        # Items over 1000kg should be in lower 40% of container
        threshold_weight = 1000  # kg
        threshold_height = container['height'] * 0.4
        
        for p in placements:
            if p.weight > threshold_weight:
                if p.z > threshold_height:
                    return False, f"Heavy item ({p.weight}kg) placed too high at z={p.z}mm"
        
        return True, None
    
    def _check_fragile_protection(
        self,
        placements: List[Placement],
        items: List[Dict],
        container: Dict
    ) -> Tuple[bool, Optional[str]]:
        """Check if fragile items are protected."""
        for p in placements:
            item = items[p.item_index]
            if item.get('fragile', False):
                # Check if anything heavy is on top
                for other in placements:
                    if other.item_index != p.item_index:
                        # Check if other is on top
                        if (abs(other.z - (p.z + p.height)) < 10 and
                            self._placements_overlap_horizontally(p, other)):
                            
                            if other.weight > item['weight'] * 2:
                                return False, f"Heavy item on top of fragile item {p.item_index}"
        
        return True, None
    
    def _check_stack_limits(
        self,
        placements: List[Placement],
        items: List[Dict],
        container: Dict
    ) -> Tuple[bool, Optional[str]]:
        """Check if stacking weight limits are respected."""
        for p in placements:
            item = items[p.item_index]
            max_stack = item.get('max_stack_weight', float('inf'))
            
            # Calculate weight on top
            weight_on_top = 0
            for other in placements:
                if (other.z > p.z and
                    self._placements_overlap_horizontally(p, other)):
                    weight_on_top += other.weight
            
            if weight_on_top > max_stack:
                return False, (f"Stack weight limit exceeded for item {p.item_index}: "
                             f"{weight_on_top:.1f}kg > {max_stack:.1f}kg")
        
        return True, None
    
    def _check_accessibility(
        self,
        placements: List[Placement],
        items: List[Dict],
        container: Dict
    ) -> Tuple[bool, Optional[str]]:
        """Check if items are reasonably accessible."""
        # At least 30% of items should have clear access from top
        accessible = 0
        
        for p in placements:
            # Check if anything is on top
            blocked = False
            for other in placements:
                if (other.z > p.z + p.height and
                    self._placements_overlap_horizontally(p, other)):
                    blocked = True
                    break
            
            if not blocked:
                accessible += 1
        
        accessibility_ratio = accessible / len(placements) if placements else 0
        
        if accessibility_ratio < 0.3:
            return False, f"Only {accessibility_ratio*100:.0f}% of items are accessible (should be >30%)"
        
        return True, None
    
    # Optimization methods
    
    def _apply_weight_distribution(self, placements: List[Placement]) -> List[Placement]:
        """Optimize weight distribution."""
        # Sort by weight and adjust z-positions
        heavy_items = sorted(
            [p for p in placements if p.weight > 500],
            key=lambda p: -p.weight
        )
        
        # Try to place heavy items lower
        for p in heavy_items:
            if p.z > self.container['height'] * 0.3:
                # Try to find lower position
                # (Simplified - would need full repositioning logic)
                pass
        
        return placements
    
    def _apply_hazard_separation(self, placements: List[Placement]) -> List[Placement]:
        """Optimize hazardous material separation."""
        # Group compatible hazmat together, separate incompatible
        # (Simplified implementation)
        return placements
    
    def _apply_refrigeration_grouping(self, placements: List[Placement]) -> List[Placement]:
        """Optimize refrigerated item grouping."""
        # Move refrigerated items closer together
        # (Simplified implementation)
        return placements
    
    # Helper methods
    
    def _calculate_horizontal_distance(self, p1: Placement, p2: Placement) -> float:
        """Calculate horizontal distance between two placements."""
        center1_x = p1.x + p1.length / 2
        center1_y = p1.y + p1.width / 2
        center2_x = p2.x + p2.length / 2
        center2_y = p2.y + p2.width / 2
        
        return ((center1_x - center2_x)**2 + (center1_y - center2_y)**2)**0.5
    
    def _placements_overlap_horizontally(self, p1: Placement, p2: Placement) -> bool:
        """Check if two placements overlap in the horizontal plane."""
        x_overlap = not (p1.x + p1.length <= p2.x or p2.x + p2.length <= p1.x)
        y_overlap = not (p1.y + p1.width <= p2.y or p2.y + p2.width <= p1.y)
        return x_overlap and y_overlap