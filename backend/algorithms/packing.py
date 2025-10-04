import logging
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Item:
    id: int
    length: float
    width: float
    height: float
    weight: float
    quantity: int = 1
    fragile: bool = False
    stackable: bool = True
    rotation_allowed: bool = True

@dataclass
class Container:
    length: float
    width: float
    height: float
    max_weight: float

@dataclass
class Placement:
    item_id: int
    x: float
    y: float
    z: float
    length: float
    width: float
    height: float
    rotated: bool = False

class PackingAlgorithm:
    def __init__(self):
        self.name = "Basic Packing Algorithm"
        self.logger = logging.getLogger(__name__)
    
    def optimize(self, container_data: Dict, items_data: List[Dict]) -> Dict:
        """
        Optimize packing using a basic first-fit decreasing algorithm
        """
        try:
            # Parse container data
            container = Container(
                length=container_data['length'],
                width=container_data['width'],
                height=container_data['height'],
                max_weight=container_data['max_weight']
            )
            
            # Parse items data
            items = []
            for item_data in items_data:
                for _ in range(item_data.get('quantity', 1)):
                    items.append(Item(
                        id=item_data['id'],
                        length=item_data['length'],
                        width=item_data['width'],
                        height=item_data['height'],
                        weight=item_data['weight'],
                        fragile=item_data.get('fragile', False),
                        stackable=item_data.get('stackable', True),
                        rotation_allowed=item_data.get('rotation_allowed', True)
                    ))
            
            # Sort items by volume (decreasing)
            items.sort(key=lambda x: x.length * x.width * x.height, reverse=True)
            
            placements = []
            used_volume = 0
            used_weight = 0
            packed_items = 0
            
            # Simple first-fit packing
            current_x, current_y, current_z = 0, 0, 0
            max_row_height = 0
            
            for item in items:
                # Check weight constraint
                if used_weight + item.weight > container.max_weight:
                    continue
                
                # Try different orientations
                orientations = self._get_orientations(item)
                placed = False
                
                for orientation in orientations:
                    l, w, h = orientation
                    
                    # Check if item fits in current position
                    if (current_x + l <= container.length and
                        current_y + w <= container.width and
                        current_z + h <= container.height):
                        
                        placement = Placement(
                            item_id=item.id,
                            x=current_x,
                            y=current_y,
                            z=current_z,
                            length=l,
                            width=w,
                            height=h,
                            rotated=(orientation != (item.length, item.width, item.height))
                        )
                        placements.append(placement)
                        
                        used_volume += l * w * h
                        used_weight += item.weight
                        packed_items += 1
                        
                        # Update current position
                        current_x += l
                        max_row_height = max(max_row_height, h)
                        placed = True
                        break
                
                if not placed:
                    # Move to next row
                    current_x = 0
                    current_y += max_row_height
                    max_row_height = 0
                    
                    # Check if we're out of container bounds
                    if current_y >= container.width:
                        break
            
            # Calculate utilization
            total_volume = container.length * container.width * container.height
            utilization_rate = used_volume / total_volume if total_volume > 0 else 0
            
            return {
                'placements': [
                    {
                        'item_id': p.item_id,
                        'position': [p.x, p.y, p.z],
                        'dimensions': [p.length, p.width, p.height],
                        'rotated': p.rotated
                    }
                    for p in placements
                ],
                'metrics': {
                    'utilization_rate': round(utilization_rate, 4),
                    'total_items_packed': packed_items,
                    'total_volume_used': round(used_volume, 2),
                    'total_weight_used': round(used_weight, 2),
                    'container_volume': round(total_volume, 2),
                    'container_max_weight': container.max_weight
                },
                'algorithm': self.name
            }
            
        except Exception as e:
            self.logger.error(f"Packing optimization failed: {str(e)}")
            raise
    
    def _get_orientations(self, item: Item) -> List[Tuple[float, float, float]]:
        """Get all possible orientations for an item"""
        orientations = []
        l, w, h = item.length, item.width, item.height
        
        if item.rotation_allowed:
            orientations.extend([
                (l, w, h),
                (l, h, w),
                (w, l, h),
                (w, h, l),
                (h, l, w),
                (h, w, l)
            ])
        else:
            orientations.append((l, w, h))
        
        # Remove duplicates and ensure dimensions are positive
        unique_orientations = []
        for orient in orientations:
            if all(dim > 0 for dim in orient) and orient not in unique_orientations:
                unique_orientations.append(orient)
        
        return unique_orientations
    
    def validate_placement(self, container: Dict, placements: List[Dict]) -> bool:
        """Validate that placements don't overlap and fit within container"""
        for i, placement1 in enumerate(placements):
            # Check container bounds
            pos1, dims1 = placement1['position'], placement1['dimensions']
            if (pos1[0] + dims1[0] > container['length'] or
                pos1[1] + dims1[1] > container['width'] or
                pos1[2] + dims1[2] > container['height']):
                return False
            
            # Check overlaps with other items
            for j, placement2 in enumerate(placements):
                if i != j:
                    if self._check_overlap(placement1, placement2):
                        return False
        
        return True
    
    def _check_overlap(self, item1: Dict, item2: Dict) -> bool:
        """Check if two items overlap"""
        pos1, dims1 = item1['position'], item1['dimensions']
        pos2, dims2 = item2['position'], item2['dimensions']
        
        # Check overlap in all dimensions
        overlap_x = (pos1[0] < pos2[0] + dims2[0]) and (pos1[0] + dims1[0] > pos2[0])
        overlap_y = (pos1[1] < pos2[1] + dims2[1]) and (pos1[1] + dims1[1] > pos2[1])
        overlap_z = (pos1[2] < pos2[2] + dims2[2]) and (pos1[2] + dims1[2] > pos2[2])
        
        return overlap_x and overlap_y and overlap_z