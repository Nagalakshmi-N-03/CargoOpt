import logging
import math
from typing import List, Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StowagePlan:
    container_assignments: Dict
    utilization_rates: Dict
    total_utilization: float

class StowageOptimizer:
    def __init__(self):
        self.name = "Stowage Optimizer"
        self.logger = logging.getLogger(__name__)
    
    def optimize(self, containers_data: List[Dict], cargo_items: List[Dict]) -> Dict:
        """
        Optimize stowage across multiple containers
        """
        try:
            # Sort containers by volume (ascending)
            containers = sorted(containers_data, 
                              key=lambda c: c['length'] * c['width'] * c['height'])
            
            # Sort items by volume (descending)
            items = sorted(cargo_items, 
                          key=lambda i: i['length'] * i['width'] * i['height'], 
                          reverse=True)
            
            container_assignments = {}
            remaining_items = items.copy()
            
            for i, container in enumerate(containers):
                container_id = container.get('id', f"container_{i}")
                container_assignments[container_id] = {
                    'container': container,
                    'items': [],
                    'used_volume': 0,
                    'used_weight': 0
                }
                
                # Try to pack items into this container
                self._pack_container(container_assignments[container_id], remaining_items)
                
                # Remove packed items from remaining items
                packed_item_ids = [item['id'] for item in container_assignments[container_id]['items']]
                remaining_items = [item for item in remaining_items if item['id'] not in packed_item_ids]
                
                if not remaining_items:
                    break
            
            # Calculate utilization metrics
            utilization_rates = {}
            total_container_volume = 0
            total_used_volume = 0
            
            for container_id, assignment in container_assignments.items():
                container_vol = (assignment['container']['length'] * 
                               assignment['container']['width'] * 
                               assignment['container']['height'])
                utilization = assignment['used_volume'] / container_vol if container_vol > 0 else 0
                
                utilization_rates[container_id] = {
                    'utilization_rate': round(utilization, 4),
                    'used_volume': round(assignment['used_volume'], 2),
                    'total_volume': round(container_vol, 2),
                    'item_count': len(assignment['items'])
                }
                
                total_container_volume += container_vol
                total_used_volume += assignment['used_volume']
            
            total_utilization = total_used_volume / total_container_volume if total_container_volume > 0 else 0
            
            return {
                'container_assignments': {
                    container_id: {
                        'container': assignment['container'],
                        'items': assignment['items'],
                        'metrics': utilization_rates[container_id]
                    }
                    for container_id, assignment in container_assignments.items()
                },
                'overall_metrics': {
                    'total_utilization': round(total_utilization, 4),
                    'total_containers_used': len(container_assignments),
                    'total_items_packed': sum(len(assign['items']) for assign in container_assignments.values()),
                    'total_volume_used': round(total_used_volume, 2),
                    'remaining_items': len(remaining_items)
                },
                'algorithm': self.name
            }
            
        except Exception as e:
            self.logger.error(f"Stowage optimization failed: {str(e)}")
            raise
    
    def _pack_container(self, container_assignment: Dict, items: List[Dict]):
        """Pack items into a single container using first-fit decreasing"""
        container = container_assignment['container']
        max_weight = container['max_weight']
        
        # Filter items that can fit by weight
        available_items = [item for item in items 
                          if item['weight'] <= max_weight - container_assignment['used_weight']]
        
        # Simple first-fit packing
        current_levels = [{'z': 0, 'max_height': 0}]
        
        for item in available_items:
            if container_assignment['used_weight'] + item['weight'] > max_weight:
                continue
            
            # Try to place item in existing levels
            placed = False
            for level in current_levels:
                if self._try_place_in_level(container_assignment, item, level, container):
                    placed = True
                    break
            
            if not placed:
                # Create new level
                new_z = max(level['z'] + level['max_height'] for level in current_levels)
                if new_z + item['height'] <= container['height']:
                    new_level = {'z': new_z, 'max_height': item['height']}
                    if self._try_place_in_level(container_assignment, item, new_level, container):
                        current_levels.append(new_level)
                        placed = True
            
            if placed:
                container_assignment['used_volume'] += (item['length'] * item['width'] * item['height'])
                container_assignment['used_weight'] += item['weight']
    
    def _try_place_in_level(self, container_assignment: Dict, item: Dict, level: Dict, container: Dict) -> bool:
        """Try to place an item in a specific level"""
        # Simplified placement - in real implementation, you'd check for exact positioning
        # and avoid overlaps
        
        # Check if item fits in container dimensions
        if (item['length'] <= container['length'] and 
            item['width'] <= container['width'] and 
            level['z'] + item['height'] <= container['height']):
            
            # For now, just add the item without precise positioning
            container_assignment['items'].append(item)
            level['max_height'] = max(level['max_height'], item['height'])
            return True
        
        return False