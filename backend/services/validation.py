"""
Validation Service
Provides comprehensive validation for optimization inputs and results.
"""

from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime

from backend.config.settings import Config
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ContainerValidator:
    """Validates container specifications."""
    
    @staticmethod
    def validate(container: Dict) -> Tuple[bool, List[str]]:
        """
        Validate container data.
        
        Args:
            container: Container dictionary
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        # Required fields
        required_fields = ['length', 'width', 'height']
        for field in required_fields:
            if field not in container:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(container[field], (int, float)) or container[field] <= 0:
                errors.append(f"Field '{field}' must be a positive number")
        
        # Max weight validation
        if 'max_weight' in container:
            if not isinstance(container['max_weight'], (int, float)) or container['max_weight'] <= 0:
                errors.append("max_weight must be a positive number")
        
        # Dimension limits
        if all(f in container for f in required_fields):
            if container['length'] > 50000:
                errors.append("Container length exceeds maximum (50,000 mm)")
            if container['width'] > 10000:
                errors.append("Container width exceeds maximum (10,000 mm)")
            if container['height'] > 10000:
                errors.append("Container height exceeds maximum (10,000 mm)")
            
            # Volume check
            volume = container['length'] * container['width'] * container['height']
            if volume < 1000:
                errors.append("Container volume too small (minimum 1 liter)")
        
        # Container type validation
        if 'container_type' in container:
            valid_types = Config.CONTAINER_TYPES
            if container['container_type'] not in valid_types:
                errors.append(f"Invalid container_type. Must be one of: {', '.join(valid_types)}")
        
        return len(errors) == 0, errors


class ItemValidator:
    """Validates item specifications."""
    
    @staticmethod
    def validate(item: Dict, item_index: int = 0) -> Tuple[bool, List[str]]:
        """
        Validate item data.
        
        Args:
            item: Item dictionary
            item_index: Index of item in list (for error messages)
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        prefix = f"Item {item_index + 1}: "
        
        # Required fields
        required_fields = ['length', 'width', 'height', 'weight']
        for field in required_fields:
            if field not in item:
                errors.append(f"{prefix}Missing required field: {field}")
            elif not isinstance(item[field], (int, float)) or item[field] <= 0:
                errors.append(f"{prefix}Field '{field}' must be a positive number")
        
        # Dimension limits
        if 'length' in item and item['length'] > 20000:
            errors.append(f"{prefix}Length exceeds maximum (20,000 mm)")
        if 'width' in item and item['width'] > 10000:
            errors.append(f"{prefix}Width exceeds maximum (10,000 mm)")
        if 'height' in item and item['height'] > 10000:
            errors.append(f"{prefix}Height exceeds maximum (10,000 mm)")
        
        # Weight limits
        if 'weight' in item:
            if item['weight'] > 50000:
                errors.append(f"{prefix}Weight exceeds maximum (50,000 kg)")
        
        # Quantity validation
        if 'quantity' in item:
            if not isinstance(item['quantity'], int) or item['quantity'] < 1:
                errors.append(f"{prefix}Quantity must be a positive integer")
            if item['quantity'] > 10000:
                errors.append(f"{prefix}Quantity exceeds maximum (10,000)")
        
        # Item type validation
        if 'item_type' in item:
            if item['item_type'] not in Config.ITEM_TYPES:
                errors.append(f"{prefix}Invalid item_type. Must be one of: {', '.join(Config.ITEM_TYPES)}")
        
        # Storage condition validation
        if 'storage_condition' in item:
            if item['storage_condition'] not in Config.STORAGE_CONDITIONS:
                errors.append(f"{prefix}Invalid storage_condition. Must be one of: {', '.join(Config.STORAGE_CONDITIONS)}")
        
        # Hazard class validation
        if 'hazard_class' in item and item['hazard_class']:
            if item['hazard_class'] not in Config.HAZARD_CLASSES:
                errors.append(f"{prefix}Invalid hazard_class. Must be one of: {', '.join(Config.HAZARD_CLASSES)}")
        
        # Temperature validation
        if 'temperature_min' in item and 'temperature_max' in item:
            if item['temperature_min'] >= item['temperature_max']:
                errors.append(f"{prefix}temperature_min must be less than temperature_max")
        
        # Boolean field validation
        boolean_fields = ['fragile', 'stackable', 'rotation_allowed', 'keep_upright']
        for field in boolean_fields:
            if field in item and not isinstance(item[field], bool):
                errors.append(f"{prefix}Field '{field}' must be a boolean")
        
        # Max stack weight validation
        if 'max_stack_weight' in item:
            if not isinstance(item['max_stack_weight'], (int, float)) or item['max_stack_weight'] < 0:
                errors.append(f"{prefix}max_stack_weight must be a non-negative number")
        
        # Priority validation
        if 'priority' in item:
            if not isinstance(item['priority'], int) or not (1 <= item['priority'] <= 10):
                errors.append(f"{prefix}priority must be an integer between 1 and 10")
        
        # Logical validations
        if item.get('keep_upright') and not item.get('rotation_allowed', True):
            # This is actually consistent, but log as warning
            pass
        
        if item.get('fragile') and item.get('stackable', True):
            if item.get('max_stack_weight', float('inf')) > 100:
                errors.append(f"{prefix}Fragile items should have lower max_stack_weight")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_items_list(items: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Validate a list of items.
        
        Args:
            items: List of item dictionaries
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        if not items:
            return False, ["Items list cannot be empty"]
        
        if len(items) > 1000:
            return False, ["Too many items (maximum 1,000)"]
        
        all_errors = []
        for idx, item in enumerate(items):
            is_valid, errors = ItemValidator.validate(item, idx)
            all_errors.extend(errors)
        
        return len(all_errors) == 0, all_errors


class ConstraintValidator:
    """Validates optimization constraints and feasibility."""
    
    @staticmethod
    def validate_feasibility(container: Dict, items: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Validate if optimization is feasible.
        
        Args:
            container: Container dictionary
            items: List of items
            
        Returns:
            Tuple of (is_feasible, list of issues)
        """
        issues = []
        
        # Calculate total volume
        container_volume = container['length'] * container['width'] * container['height']
        total_item_volume = sum(
            item['length'] * item['width'] * item['height'] * item.get('quantity', 1)
            for item in items
        )
        
        if total_item_volume > container_volume:
            utilization = (total_item_volume / container_volume) * 100
            issues.append(
                f"Total item volume exceeds container capacity by {utilization - 100:.1f}% "
                f"({total_item_volume:,} mm³ vs {container_volume:,} mm³)"
            )
        
        # Calculate total weight
        total_weight = sum(item['weight'] * item.get('quantity', 1) for item in items)
        max_weight = container.get('max_weight', float('inf'))
        
        if total_weight > max_weight:
            excess = total_weight - max_weight
            issues.append(
                f"Total weight exceeds container capacity by {excess:.2f} kg "
                f"({total_weight:.2f} kg vs {max_weight:.2f} kg)"
            )
        
        # Check if any single item is too large
        container_dims = [container['length'], container['width'], container['height']]
        container_dims_sorted = sorted(container_dims)
        
        for idx, item in enumerate(items):
            item_dims = sorted([item['length'], item['width'], item['height']])
            
            if (item_dims[0] > container_dims_sorted[0] or
                item_dims[1] > container_dims_sorted[1] or
                item_dims[2] > container_dims_sorted[2]):
                issues.append(
                    f"Item {idx + 1} ({item.get('item_id', 'unknown')}) is too large "
                    f"for container in at least one dimension "
                    f"({item['length']}x{item['width']}x{item['height']} mm)"
                )
        
        # Check hazmat compatibility
        hazmat_items = [item for item in items if item.get('hazard_class')]
        if len(hazmat_items) > 1:
            incompatible = ConstraintValidator._check_hazmat_compatibility(hazmat_items)
            if incompatible:
                issues.append(f"Incompatible hazardous materials detected: {incompatible}")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def _check_hazmat_compatibility(hazmat_items: List[Dict]) -> Optional[str]:
        """Check if hazardous materials are compatible."""
        from backend.algorithms.stowage import StowageRules
        
        prohibited_pairs = []
        
        for i, item1 in enumerate(hazmat_items):
            class1 = item1.get('hazard_class')
            for item2 in hazmat_items[i+1:]:
                class2 = item2.get('hazard_class')
                
                segregation = StowageRules.get_segregation_requirement(class1, class2)
                if segregation == 'prohibited':
                    prohibited_pairs.append(f"{class1} and {class2}")
        
        if prohibited_pairs:
            return ", ".join(prohibited_pairs)
        return None
    
    @staticmethod
    def validate_optimization_parameters(params: Dict) -> Tuple[bool, List[str]]:
        """
        Validate optimization parameters.
        
        Args:
            params: Parameters dictionary
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        if 'algorithm' in params:
            valid_algorithms = ['genetic', 'constraint', 'hybrid', 'auto']
            if params['algorithm'] not in valid_algorithms:
                errors.append(f"Invalid algorithm. Must be one of: {', '.join(valid_algorithms)}")
        
        if 'population_size' in params:
            if not isinstance(params['population_size'], int) or not (10 <= params['population_size'] <= 500):
                errors.append("population_size must be an integer between 10 and 500")
        
        if 'generations' in params:
            if not isinstance(params['generations'], int) or not (5 <= params['generations'] <= 500):
                errors.append("generations must be an integer between 5 and 500")
        
        if 'time_limit' in params:
            if not isinstance(params['time_limit'], int) or not (10 <= params['time_limit'] <= 600):
                errors.append("time_limit must be an integer between 10 and 600 seconds")
        
        if 'mutation_rate' in params:
            if not isinstance(params['mutation_rate'], (int, float)) or not (0 <= params['mutation_rate'] <= 1):
                errors.append("mutation_rate must be a number between 0 and 1")
        
        if 'crossover_rate' in params:
            if not isinstance(params['crossover_rate'], (int, float)) or not (0 <= params['crossover_rate'] <= 1):
                errors.append("crossover_rate must be a number between 0 and 1")
        
        return len(errors) == 0, errors


class ValidationService:
    """
    Main validation service coordinating all validation operations.
    """
    
    def __init__(self, config: Config = None):
        """
        Initialize validation service.
        
        Args:
            config: Configuration object
        """
        self.config = config or Config()
        self.container_validator = ContainerValidator()
        self.item_validator = ItemValidator()
        self.constraint_validator = ConstraintValidator()
        
        logger.info("ValidationService initialized")
    
    def validate_optimization_request(self, request: Dict) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate complete optimization request.
        
        Args:
            request: Optimization request dictionary
            
        Returns:
            Tuple of (is_valid, dictionary of errors by category)
        """
        errors = {
            'container': [],
            'items': [],
            'constraints': [],
            'parameters': []
        }
        
        # Validate container
        if 'container' not in request:
            errors['container'].append("Missing container data")
        else:
            is_valid, container_errors = self.container_validator.validate(request['container'])
            errors['container'].extend(container_errors)
        
        # Validate items
        if 'items' not in request:
            errors['items'].append("Missing items data")
        else:
            is_valid, items_errors = self.item_validator.validate_items_list(request['items'])
            errors['items'].extend(items_errors)
        
        # Validate feasibility
        if 'container' in request and 'items' in request and not errors['container'] and not errors['items']:
            is_feasible, constraint_errors = self.constraint_validator.validate_feasibility(
                request['container'],
                request['items']
            )
            errors['constraints'].extend(constraint_errors)
        
        # Validate parameters
        if 'parameters' in request:
            is_valid, param_errors = self.constraint_validator.validate_optimization_parameters(
                request['parameters']
            )
            errors['parameters'].extend(param_errors)
        
        # Remove empty error categories
        errors = {k: v for k, v in errors.items() if v}
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("Validation passed")
        else:
            logger.warning(f"Validation failed with {sum(len(v) for v in errors.values())} errors")
        
        return is_valid, errors
    
    def validate_placement_result(
        self,
        placements: List,
        container: Dict,
        items: List[Dict]
    ) -> Tuple[bool, List[str]]:
        """
        Validate optimization result placements.
        
        Args:
            placements: List of placements
            container: Container data
            items: Items data
            
        Returns:
            Tuple of (is_valid, list of violations)
        """
        violations = []
        
        # Check each placement
        for i, placement in enumerate(placements):
            # Check within container bounds
            if hasattr(placement, 'x'):
                if (placement.x < 0 or
                    placement.y < 0 or
                    placement.z < 0 or
                    placement.x + placement.length > container['length'] or
                    placement.y + placement.width > container['width'] or
                    placement.z + placement.height > container['height']):
                    violations.append(f"Placement {i} is outside container bounds")
            
            # Check for overlaps
            for j, other in enumerate(placements[i+1:], i+1):
                if self._check_overlap(placement, other):
                    violations.append(f"Placement {i} overlaps with placement {j}")
        
        # Check total weight
        total_weight = sum(
            p.weight if hasattr(p, 'weight') else 0
            for p in placements
        )
        if total_weight > container.get('max_weight', float('inf')):
            violations.append(f"Total weight ({total_weight:.2f} kg) exceeds container capacity")
        
        return len(violations) == 0, violations
    
    @staticmethod
    def _check_overlap(p1, p2) -> bool:
        """Check if two placements overlap."""
        if not (hasattr(p1, 'x') and hasattr(p2, 'x')):
            return False
        
        return not (
            p1.x + p1.length <= p2.x or p2.x + p2.length <= p1.x or
            p1.y + p1.width <= p2.y or p2.y + p2.width <= p1.y or
            p1.z + p1.height <= p2.z or p2.z + p2.height <= p1.z
        )