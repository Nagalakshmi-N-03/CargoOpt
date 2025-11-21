"""
Mathematical Utility Functions
Common mathematical operations for container optimization.
"""

import math
from typing import Tuple, List, Dict
import numpy as np


def calculate_distance(
    p1: Tuple[float, float, float],
    p2: Tuple[float, float, float]
) -> float:
    """
    Calculate Euclidean distance between two 3D points.
    
    Args:
        p1: First point (x, y, z)
        p2: Second point (x, y, z)
        
    Returns:
        Distance between points
    """
    return math.sqrt(
        (p2[0] - p1[0])**2 +
        (p2[1] - p1[1])**2 +
        (p2[2] - p1[2])**2
    )


def calculate_volume(length: float, width: float, height: float) -> float:
    """
    Calculate volume from dimensions.
    
    Args:
        length, width, height: Dimensions
        
    Returns:
        Volume
    """
    return length * width * height


def calculate_center_of_gravity(
    positions: List[Tuple[float, float, float]],
    weights: List[float]
) -> Tuple[float, float, float]:
    """
    Calculate weighted center of gravity.
    
    Args:
        positions: List of (x, y, z) positions
        weights: List of weights corresponding to positions
        
    Returns:
        Center of gravity (x, y, z)
    """
    if not positions or not weights:
        return (0.0, 0.0, 0.0)
    
    total_weight = sum(weights)
    if total_weight == 0:
        return (0.0, 0.0, 0.0)
    
    cog_x = sum(p[0] * w for p, w in zip(positions, weights)) / total_weight
    cog_y = sum(p[1] * w for p, w in zip(positions, weights)) / total_weight
    cog_z = sum(p[2] * w for p, w in zip(positions, weights)) / total_weight
    
    return (cog_x, cog_y, cog_z)


def rotate_point(
    point: Tuple[float, float, float],
    angle_degrees: float,
    axis: str = 'z'
) -> Tuple[float, float, float]:
    """
    Rotate a 3D point around an axis.
    
    Args:
        point: Point to rotate (x, y, z)
        angle_degrees: Rotation angle in degrees
        axis: Axis to rotate around ('x', 'y', or 'z')
        
    Returns:
        Rotated point (x, y, z)
    """
    angle_rad = math.radians(angle_degrees)
    x, y, z = point
    
    if axis == 'x':
        return (
            x,
            y * math.cos(angle_rad) - z * math.sin(angle_rad),
            y * math.sin(angle_rad) + z * math.cos(angle_rad)
        )
    elif axis == 'y':
        return (
            x * math.cos(angle_rad) + z * math.sin(angle_rad),
            y,
            -x * math.sin(angle_rad) + z * math.cos(angle_rad)
        )
    else:  # z axis
        return (
            x * math.cos(angle_rad) - y * math.sin(angle_rad),
            x * math.sin(angle_rad) + y * math.cos(angle_rad),
            z
        )


def calculate_overlap_area(
    box1: Dict[str, float],
    box2: Dict[str, float]
) -> float:
    """
    Calculate horizontal overlap area between two boxes.
    
    Args:
        box1: {'x': x1, 'y': y1, 'length': l1, 'width': w1}
        box2: {'x': x2, 'y': y2, 'length': l2, 'width': w2}
        
    Returns:
        Overlap area
    """
    x_overlap = max(
        0,
        min(box1['x'] + box1['length'], box2['x'] + box2['length']) -
        max(box1['x'], box2['x'])
    )
    
    y_overlap = max(
        0,
        min(box1['y'] + box1['width'], box2['y'] + box2['width']) -
        max(box1['y'], box2['y'])
    )
    
    return x_overlap * y_overlap


def normalize_vector(vector: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    Normalize a 3D vector to unit length.
    
    Args:
        vector: Vector to normalize
        
    Returns:
        Normalized vector
    """
    magnitude = math.sqrt(sum(x**2 for x in vector))
    if magnitude == 0:
        return (0.0, 0.0, 0.0)
    return tuple(x / magnitude for x in vector)


def dot_product(v1: Tuple[float, ...], v2: Tuple[float, ...]) -> float:
    """Calculate dot product of two vectors."""
    return sum(a * b for a, b in zip(v1, v2))


def cross_product(
    v1: Tuple[float, float, float],
    v2: Tuple[float, float, float]
) -> Tuple[float, float, float]:
    """Calculate cross product of two 3D vectors."""
    return (
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    )


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b."""
    return a + (b - a) * clamp(t, 0.0, 1.0)