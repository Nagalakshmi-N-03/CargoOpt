import logging
import math
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class Vector3D:
    x: float
    y: float
    z: float
    
    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def dot(self, other) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

@dataclass
class BoundingBox:
    min_point: Vector3D
    max_point: Vector3D
    
    @property
    def center(self) -> Vector3D:
        return Vector3D(
            (self.min_point.x + self.max_point.x) / 2,
            (self.min_point.y + self.max_point.y) / 2,
            (self.min_point.z + self.max_point.z) / 2
        )
    
    @property
    def dimensions(self) -> Vector3D:
        return Vector3D(
            self.max_point.x - self.min_point.x,
            self.max_point.y - self.min_point.y,
            self.max_point.z - self.min_point.z
        )
    
    @property
    def volume(self) -> float:
        dims = self.dimensions
        return dims.x * dims.y * dims.z

class MathUtils:
    @staticmethod
    def calculate_volume(length: float, width: float, height: float) -> float:
        """Calculate volume from dimensions"""
        return length * width * height
    
    @staticmethod
    def calculate_surface_area(length: float, width: float, height: float) -> float:
        """Calculate surface area from dimensions"""
        return 2 * (length * width + length * height + width * height)
    
    @staticmethod
    def calculate_utilization(used_volume: float, total_volume: float) -> float:
        """Calculate volume utilization percentage (0-1)"""
        if total_volume <= 0:
            return 0.0
        return max(0.0, min(1.0, used_volume / total_volume))
    
    @staticmethod
    def check_overlap(box1: BoundingBox, box2: BoundingBox) -> bool:
        """Check if two bounding boxes overlap"""
        return (
            box1.min_point.x < box2.max_point.x and
            box1.max_point.x > box2.min_point.x and
            box1.min_point.y < box2.max_point.y and
            box1.max_point.y > box2.min_point.y and
            box1.min_point.z < box2.max_point.z and
            box1.max_point.z > box2.min_point.z
        )
    
    @staticmethod
    def calculate_overlap_volume(box1: BoundingBox, box2: BoundingBox) -> float:
        """Calculate overlap volume between two bounding boxes"""
        if not MathUtils.check_overlap(box1, box2):
            return 0.0
        
        overlap_x = max(0, min(box1.max_point.x, box2.max_point.x) - max(box1.min_point.x, box2.min_point.x))
        overlap_y = max(0, min(box1.max_point.y, box2.max_point.y) - max(box1.min_point.y, box2.min_point.y))
        overlap_z = max(0, min(box1.max_point.z, box2.max_point.z) - max(box1.min_point.z, box2.min_point.z))
        
        return overlap_x * overlap_y * overlap_z
    
    @staticmethod
    def is_inside_container(item_box: BoundingBox, container_box: BoundingBox) -> bool:
        """Check if item is completely inside container"""
        return (
            item_box.min_point.x >= container_box.min_point.x and
            item_box.max_point.x <= container_box.max_point.x and
            item_box.min_point.y >= container_box.min_point.y and
            item_box.max_point.y <= container_box.max_point.y and
            item_box.min_point.z >= container_box.min_point.z and
            item_box.max_point.z <= container_box.max_point.z
        )
    
    @staticmethod
    def calculate_centroid(points: List[Vector3D]) -> Vector3D:
        """Calculate centroid of multiple points"""
        if not points:
            return Vector3D(0, 0, 0)
        
        sum_x = sum(p.x for p in points)
        sum_y = sum(p.y for p in points)
        sum_z = sum(p.z for p in points)
        count = len(points)
        
        return Vector3D(sum_x / count, sum_y / count, sum_z / count)
    
    @staticmethod
    def calculate_distance(point1: Vector3D, point2: Vector3D) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt(
            (point1.x - point2.x)**2 +
            (point1.y - point2.y)**2 +
            (point1.z - point2.z)**2
        )
    
    @staticmethod
    def rotate_point(point: Vector3D, rotation_angles: Vector3D, center: Vector3D = None) -> Vector3D:
        """Rotate a point around given center using Euler angles"""
        if center is None:
            center = Vector3D(0, 0, 0)
        
        # Translate point to origin
        translated = point - center
        
        # Convert to radians
        rx, ry, rz = math.radians(rotation_angles.x), math.radians(rotation_angles.y), math.radians(rotation_angles.z)
        
        # Rotation matrices
        # X-axis rotation
        x_rotated = Vector3D(
            translated.x,
            translated.y * math.cos(rx) - translated.z * math.sin(rx),
            translated.y * math.sin(rx) + translated.z * math.cos(rx)
        )
        
        # Y-axis rotation
        y_rotated = Vector3D(
            x_rotated.x * math.cos(ry) + x_rotated.z * math.sin(ry),
            x_rotated.y,
            -x_rotated.x * math.sin(ry) + x_rotated.z * math.cos(ry)
        )
        
        # Z-axis rotation
        z_rotated = Vector3D(
            y_rotated.x * math.cos(rz) - y_rotated.y * math.sin(rz),
            y_rotated.x * math.sin(rz) + y_rotated.y * math.cos(rz),
            y_rotated.z
        )
        
        # Translate back
        return z_rotated + center
    
    @staticmethod
    def get_bounding_box_from_placement(position: List[float], dimensions: List[float]) -> BoundingBox:
        """Create bounding box from placement data"""
        min_point = Vector3D(position[0], position[1], position[2])
        max_point = Vector3D(
            position[0] + dimensions[0],
            position[1] + dimensions[1],
            position[2] + dimensions[2]
        )
        return BoundingBox(min_point, max_point)
    
    @staticmethod
    def calculate_packing_efficiency(placements: List[Dict], container_volume: float) -> Dict[str, float]:
        """Calculate various packing efficiency metrics"""
        if not placements or container_volume <= 0:
            return {
                'volume_utilization': 0.0,
                'space_efficiency': 0.0,
                'density_score': 0.0
            }
        
        total_used_volume = 0
        bounding_boxes = []
        
        for placement in placements:
            position = placement['position']
            dimensions = placement['dimensions']
            volume = dimensions[0] * dimensions[1] * dimensions[2]
            total_used_volume += volume
            
            bbox = MathUtils.get_bounding_box_from_placement(position, dimensions)
            bounding_boxes.append(bbox)
        
        volume_utilization = total_used_volume / container_volume
        
        # Calculate space efficiency (considering gaps)
        if len(bounding_boxes) > 1:
            total_overlap_volume = 0
            for i in range(len(bounding_boxes)):
                for j in range(i + 1, len(bounding_boxes)):
                    total_overlap_volume += MathUtils.calculate_overlap_volume(
                        bounding_boxes[i], bounding_boxes[j]
                    )
            
            # Penalize overlaps
            space_efficiency = volume_utilization * (1 - total_overlap_volume / total_used_volume)
        else:
            space_efficiency = volume_utilization
        
        # Density score (combination of metrics)
        density_score = (volume_utilization + space_efficiency) / 2
        
        return {
            'volume_utilization': round(volume_utilization, 4),
            'space_efficiency': round(space_efficiency, 4),
            'density_score': round(density_score, 4)
        }
    
    @staticmethod
    def calculate_center_of_mass(placements: List[Dict], weights: List[float]) -> Vector3D:
        """Calculate center of mass for placed items"""
        if not placements or not weights or len(placements) != len(weights):
            return Vector3D(0, 0, 0)
        
        total_mass = sum(weights)
        if total_mass == 0:
            return Vector3D(0, 0, 0)
        
        weighted_x = 0
        weighted_y = 0
        weighted_z = 0
        
        for placement, weight in zip(placements, weights):
            position = placement['position']
            dimensions = placement['dimensions']
            
            # Use center of each item
            center_x = position[0] + dimensions[0] / 2
            center_y = position[1] + dimensions[1] / 2
            center_z = position[2] + dimensions[2] / 2
            
            weighted_x += center_x * weight
            weighted_y += center_y * weight
            weighted_z += center_z * weight
        
        return Vector3D(
            weighted_x / total_mass,
            weighted_y / total_mass,
            weighted_z / total_mass
        )
    
    @staticmethod
    def calculate_stability_score(placements: List[Dict], container_dimensions: List[float]) -> float:
        """Calculate stability score based on center of mass and base support"""
        if not placements:
            return 1.0  # Perfect stability for empty container
        
        # Calculate center of mass (assuming uniform density for simplicity)
        weights = [1.0] * len(placements)  # Uniform weight for stability calculation
        com = MathUtils.calculate_center_of_mass(placements, weights)
        
        # Ideal center is at the geometric center of container base
        ideal_com = Vector3D(
            container_dimensions[0] / 2,
            container_dimensions[1] / 2,
            0  # At base level for stability
        )
        
        # Distance from ideal center (normalized)
        max_distance = math.sqrt(
            (container_dimensions[0] / 2)**2 +
            (container_dimensions[1] / 2)**2
        )
        actual_distance = MathUtils.calculate_distance(com, ideal_com)
        
        if max_distance == 0:
            return 1.0
        
        # Stability decreases as center of mass moves away from center
        distance_penalty = min(1.0, actual_distance / max_distance)
        stability_score = 1.0 - distance_penalty
        
        # Additional penalty for high center of mass
        height_penalty = min(1.0, com.z / container_dimensions[2])
        stability_score *= (1.0 - height_penalty * 0.5)  # Reduce by up to 50% for high COM
        
        return max(0.0, min(1.0, stability_score))
    
    @staticmethod
    def optimize_rotation(dimensions: List[float], container_dimensions: List[float]) -> List[float]:
        """Find optimal rotation to fit in container"""
        length, width, height = dimensions
        cont_length, cont_width, cont_height = container_dimensions
        
        # Try all rotations that fit
        valid_rotations = []
        
        rotations = [
            (length, width, height),
            (length, height, width),
            (width, length, height),
            (width, height, length),
            (height, length, width),
            (height, width, length)
        ]
        
        for rot in rotations:
            l, w, h = rot
            if (l <= cont_length and w <= cont_width and h <= cont_height):
                # Prefer rotations that minimize empty space
                space_utilization = (l * w * h) / (cont_length * cont_width * cont_height)
                valid_rotations.append((rot, space_utilization))
        
        if not valid_rotations:
            return dimensions  # Return original if no rotation fits
        
        # Return rotation with best space utilization
        best_rotation = max(valid_rotations, key=lambda x: x[1])[0]
        return list(best_rotation)
    
    @staticmethod
    def calculate_container_fill_pattern(container_dimensions: List[float], item_dimensions: List[float]) -> Dict:
        """Calculate optimal grid-based fill pattern for items in container"""
        cont_l, cont_w, cont_h = container_dimensions
        item_l, item_w, item_h = item_dimensions
        
        # Calculate how many items fit in each dimension
        items_x = math.floor(cont_l / item_l) if item_l > 0 else 0
        items_y = math.floor(cont_w / item_w) if item_w > 0 else 0
        items_z = math.floor(cont_h / item_h) if item_h > 0 else 0
        
        total_items = items_x * items_y * items_z
        
        # Calculate utilization
        used_volume = total_items * item_l * item_w * item_h
        total_volume = cont_l * cont_w * cont_h
        utilization = used_volume / total_volume if total_volume > 0 else 0
        
        return {
            'items_per_layer': items_x * items_y,
            'layers': items_z,
            'total_items': total_items,
            'utilization': round(utilization, 4),
            'pattern': f"{items_x}x{items_y}x{items_z}",
            'wasted_space': round(total_volume - used_volume, 2)
        }