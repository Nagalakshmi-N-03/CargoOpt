import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import math

from backend.utils.math_utils import MathUtils, Vector3D, BoundingBox

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    is_valid: bool
    issues: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'is_valid': self.is_valid,
            'issues': self.issues,
            'warnings': self.warnings,
            'metrics': self.metrics
        }

class ValidationService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_container_data(self, container_data: Dict[str, Any]) -> ValidationResult:
        """Validate container data"""
        issues = []
        warnings = []
        
        required_fields = ['length', 'width', 'height', 'max_weight']
        for field in required_fields:
            if field not in container_data:
                issues.append(f"Missing required field: {field}")
        
        if not issues:
            # Validate dimensions
            length = container_data.get('length', 0)
            width = container_data.get('width', 0)
            height = container_data.get('height', 0)
            max_weight = container_data.get('max_weight', 0)
            
            if length <= 0:
                issues.append("Container length must be positive")
            if width <= 0:
                issues.append("Container width must be positive")
            if height <= 0:
                issues.append("Container height must be positive")
            if max_weight <= 0:
                issues.append("Container max weight must be positive")
            
            # Check for reasonable dimensions
            if length > 10000:  # 100 meters
                warnings.append("Container length seems unusually large")
            if width > 10000:
                warnings.append("Container width seems unusually large")
            if height > 10000:
                warnings.append("Container height seems unusually large")
            if max_weight > 1000000:  # 1000 tons
                warnings.append("Container max weight seems unusually large")
        
        metrics = {
            'container_volume': length * width * height if not issues else 0,
            'has_required_fields': len(issues) == 0
        }
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            metrics=metrics
        )
    
    def validate_cargo_item(self, item_data: Dict[str, Any]) -> ValidationResult:
        """Validate individual cargo item"""
        issues = []
        warnings = []
        
        required_fields = ['id', 'length', 'width', 'height', 'weight']
        for field in required_fields:
            if field not in item_data:
                issues.append(f"Missing required field: {field}")
        
        if not issues:
            # Validate dimensions and weight
            length = item_data.get('length', 0)
            width = item_data.get('width', 0)
            height = item_data.get('height', 0)
            weight = item_data.get('weight', 0)
            quantity = item_data.get('quantity', 1)
            
            if length <= 0:
                issues.append("Item length must be positive")
            if width <= 0:
                issues.append("Item width must be positive")
            if height <= 0:
                issues.append("Item height must be positive")
            if weight <= 0:
                issues.append("Item weight must be positive")
            if quantity <= 0:
                issues.append("Item quantity must be positive")
            
            # Check for reasonable values
            if length > 1000:  # 10 meters
                warnings.append("Item length seems unusually large")
            if width > 1000:
                warnings.append("Item width seems unusually large")
            if height > 1000:
                warnings.append("Item height seems unusually large")
            if weight > 10000:  # 10 tons
                warnings.append("Item weight seems unusually large")
            if quantity > 1000:
                warnings.append("Item quantity seems unusually large")
            
            # Check if item is too small
            volume = length * width * height
            if volume < 1:  # 1 cm³
                warnings.append("Item volume is very small, may cause precision issues")
        
        metrics = {
            'item_volume': length * width * height if not issues else 0,
            'total_volume': (length * width * height * quantity) if not issues else 0,
            'total_weight': (weight * quantity) if not issues else 0,
            'has_required_fields': len(issues) == 0
        }
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            metrics=metrics
        )
    
    def validate_placement(self, container_data: Dict[str, Any], 
                          placements: List[Dict[str, Any]]) -> ValidationResult:
        """Validate item placements in container"""
        issues = []
        warnings = []
        
        if not placements:
            warnings.append("No placements to validate")
            return ValidationResult(
                is_valid=True,
                issues=issues,
                warnings=warnings,
                metrics={'total_placements': 0}
            )
        
        container_box = BoundingBox(
            Vector3D(0, 0, 0),
            Vector3D(container_data['length'], container_data['width'], container_data['height'])
        )
        
        total_volume_used = 0
        placement_boxes = []
        
        for i, placement in enumerate(placements):
            # Check required fields
            required_placement_fields = ['item_id', 'position', 'dimensions']
            for field in required_placement_fields:
                if field not in placement:
                    issues.append(f"Placement {i} missing required field: {field}")
            
            if 'position' in placement and 'dimensions' in placement:
                position = placement['position']
                dimensions = placement['dimensions']
                
                # Create bounding box for placement
                placement_box = MathUtils.get_bounding_box_from_placement(position, dimensions)
                placement_boxes.append(placement_box)
                
                # Check if placement is within container
                if not MathUtils.is_inside_container(placement_box, container_box):
                    issues.append(f"Item {placement.get('item_id', 'unknown')} is outside container bounds")
                
                # Check for valid dimensions
                if any(dim <= 0 for dim in dimensions):
                    issues.append(f"Item {placement.get('item_id', 'unknown')} has invalid dimensions")
                
                total_volume_used += dimensions[0] * dimensions[1] * dimensions[2]
        
        # Check for overlaps between items
        for i in range(len(placement_boxes)):
            for j in range(i + 1, len(placement_boxes)):
                if MathUtils.check_overlap(placement_boxes[i], placement_boxes[j]):
                    overlap_volume = MathUtils.calculate_overlap_volume(placement_boxes[i], placement_boxes[j])
                    issues.append(f"Items overlap: placement {i} and {j} overlap by {overlap_volume:.2f} volume units")
        
        # Check container utilization
        container_volume = container_data['length'] * container_data['width'] * container_data['height']
        utilization = total_volume_used / container_volume if container_volume > 0 else 0
        
        if utilization > 1.0:
            issues.append("Total placed volume exceeds container volume")
        elif utilization > 0.95:
            warnings.append("Container utilization is very high (>95%)")
        elif utilization < 0.3:
            warnings.append("Container utilization is low (<30%)")
        
        metrics = {
            'total_placements': len(placements),
            'total_volume_used': total_volume_used,
            'container_volume': container_volume,
            'utilization_rate': utilization,
            'overlap_count': len([1 for i in range(len(placement_boxes)) for j in range(i+1, len(placement_boxes)) 
                               if MathUtils.check_overlap(placement_boxes[i], placement_boxes[j])])
        }
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            metrics=metrics
        )
    
    def validate_stowage_plan(self, stowage_plan: Dict[str, Any]) -> ValidationResult:
        """Validate complete stowage plan"""
        issues = []
        warnings = []
        
        required_plan_fields = ['containers', 'unassigned_items', 'total_utilization']
        for field in required_plan_fields:
            if field not in stowage_plan:
                issues.append(f"Stowage plan missing required field: {field}")
        
        if not issues:
            containers = stowage_plan.get('containers', [])
            unassigned_items = stowage_plan.get('unassigned_items', [])
            
            # Validate each container assignment
            for i, container_assignment in enumerate(containers):
                container_validation = self.validate_container_data(container_assignment.get('container_data', {}))
                issues.extend([f"Container {i}: {issue}" for issue in container_validation.issues])
                warnings.extend([f"Container {i}: {warning}" for warning in container_validation.warnings])
                
                # Validate placements in container
                placements = container_assignment.get('placements', [])
                placement_validation = self.validate_placement(
                    container_assignment.get('container_data', {}),
                    placements
                )
                issues.extend([f"Container {i}: {issue}" for issue in placement_validation.issues])
                warnings.extend([f"Container {i}: {warning}" for warning in placement_validation.warnings])
            
            # Check overall plan metrics
            total_utilization = stowage_plan.get('total_utilization', 0)
            if total_utilization > 1.0:
                issues.append("Total utilization exceeds 100%")
            elif total_utilization < 0.1:
                warnings.append("Overall utilization is very low (<10%)")
            
            if unassigned_items:
                warnings.append(f"{len(unassigned_items)} items could not be assigned to containers")
        
        metrics = {
            'container_count': len(containers) if not issues else 0,
            'unassigned_items_count': len(unassigned_items) if not issues else 0,
            'total_utilization': stowage_plan.get('total_utilization', 0) if not issues else 0,
            'is_complete_plan': len(issues) == 0
        }
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            metrics=metrics
        )
    
    def get_validation_summary(self, validation_results: List[ValidationResult]) -> Dict[str, Any]:
        """Get summary of multiple validation results"""
        total_valid = sum(1 for result in validation_results if result.is_valid)
        total_issues = sum(len(result.issues) for result in validation_results)
        total_warnings = sum(len(result.warnings) for result in validation_results)
        
        return {
            'total_checks': len(validation_results),
            'passed_checks': total_valid,
            'failed_checks': len(validation_results) - total_valid,
            'total_issues': total_issues,
            'total_warnings': total_warnings,
            'success_rate': total_valid / len(validation_results) if validation_results else 0
        }