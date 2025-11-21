"""
CargoOpt API Models and Validation Schemas
Defines data models and validation schemas for API requests/responses.
"""

from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError, post_load, pre_load
from datetime import datetime
from typing import Optional, List, Dict, Any

from backend.config.settings import Config


# ============================================================================
# Base Schemas
# ============================================================================

class BaseSchema(Schema):
    """Base schema with common configuration."""
    
    class Meta:
        strict = True
        ordered = True


class TimestampMixin:
    """Mixin for timestamp fields."""
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


# ============================================================================
# Container Schemas
# ============================================================================

class ContainerSchema(BaseSchema):
    """Schema for container data validation."""
    
    id = fields.Integer(dump_only=True)
    container_id = fields.String(
        required=False,
        validate=validate.Length(max=50),
        metadata={'description': 'Unique container identifier'}
    )
    name = fields.String(
        required=False,
        validate=validate.Length(max=200),
        metadata={'description': 'Container name'}
    )
    length = fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=50000),
        metadata={'description': 'Length in millimeters'}
    )
    width = fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=10000),
        metadata={'description': 'Width in millimeters'}
    )
    height = fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=10000),
        metadata={'description': 'Height in millimeters'}
    )
    max_weight = fields.Float(
        required=True,
        validate=validate.Range(min=0.1, max=100000),
        metadata={'description': 'Maximum weight capacity in kg'}
    )
    container_type = fields.String(
        required=False,
        validate=validate.OneOf(Config.CONTAINER_TYPES),
        load_default='standard',
        metadata={'description': 'Type of container'}
    )
    description = fields.String(
        required=False,
        validate=validate.Length(max=1000)
    )
    created_at = fields.DateTime(dump_only=True)
    
    @validates_schema
    def validate_dimensions(self, data, **kwargs):
        """Validate container dimensions are reasonable."""
        if 'length' in data and 'width' in data and 'height' in data:
            volume = data['length'] * data['width'] * data['height']
            if volume < 1000:  # Minimum 1 liter
                raise ValidationError('Container volume too small')
    
    @post_load
    def convert_to_mm(self, data, **kwargs):
        """Ensure all dimensions are in millimeters."""
        # Add _mm suffix fields for database storage
        data['length_mm'] = data.get('length')
        data['width_mm'] = data.get('width')
        data['height_mm'] = data.get('height')
        data['max_weight_kg'] = data.get('max_weight')
        return data


class ContainerResponseSchema(ContainerSchema):
    """Schema for container response with additional computed fields."""
    
    volume_m3 = fields.Method('get_volume_m3', dump_only=True)
    volume_display = fields.Method('get_volume_display', dump_only=True)
    
    def get_volume_m3(self, obj):
        """Calculate volume in cubic meters."""
        if isinstance(obj, dict):
            l, w, h = obj.get('length', 0), obj.get('width', 0), obj.get('height', 0)
        else:
            l, w, h = obj.length, obj.width, obj.height
        return round((l * w * h) / 1e9, 3)
    
    def get_volume_display(self, obj):
        """Get formatted volume display string."""
        vol = self.get_volume_m3(obj)
        return f"{vol} m³"


# ============================================================================
# Item Schemas
# ============================================================================

class ItemSchema(BaseSchema):
    """Schema for item data validation."""
    
    id = fields.Integer(dump_only=True)
    item_id = fields.String(
        required=False,
        validate=validate.Length(max=50),
        metadata={'description': 'Unique item identifier'}
    )
    name = fields.String(
        required=False,
        validate=validate.Length(max=200),
        metadata={'description': 'Item name'}
    )
    length = fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=20000),
        metadata={'description': 'Length in millimeters'}
    )
    width = fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=10000),
        metadata={'description': 'Width in millimeters'}
    )
    height = fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=10000),
        metadata={'description': 'Height in millimeters'}
    )
    weight = fields.Float(
        required=True,
        validate=validate.Range(min=0.001, max=50000),
        metadata={'description': 'Weight in kilograms'}
    )
    quantity = fields.Integer(
        required=False,
        validate=validate.Range(min=1, max=10000),
        load_default=1,
        metadata={'description': 'Number of identical items'}
    )
    item_type = fields.String(
        required=False,
        validate=validate.OneOf(Config.ITEM_TYPES),
        load_default='other',
        metadata={'description': 'Category of item'}
    )
    storage_condition = fields.String(
        required=False,
        validate=validate.OneOf(Config.STORAGE_CONDITIONS),
        load_default='standard',
        metadata={'description': 'Required storage condition'}
    )
    fragile = fields.Boolean(
        required=False,
        load_default=False,
        metadata={'description': 'Whether item is fragile'}
    )
    stackable = fields.Boolean(
        required=False,
        load_default=True,
        metadata={'description': 'Whether items can be stacked on top'}
    )
    max_stack_weight = fields.Float(
        required=False,
        validate=validate.Range(min=0),
        metadata={'description': 'Maximum weight that can be placed on top (kg)'}
    )
    rotation_allowed = fields.Boolean(
        required=False,
        load_default=True,
        metadata={'description': 'Whether item can be rotated'}
    )
    keep_upright = fields.Boolean(
        required=False,
        load_default=False,
        metadata={'description': 'Whether item must stay upright'}
    )
    hazard_class = fields.String(
        required=False,
        validate=validate.OneOf(Config.HAZARD_CLASSES + [None, '']),
        allow_none=True,
        metadata={'description': 'IMDG hazard class if applicable'}
    )
    temperature_min = fields.Float(
        required=False,
        validate=validate.Range(min=-50, max=50),
        allow_none=True,
        metadata={'description': 'Minimum temperature requirement (°C)'}
    )
    temperature_max = fields.Float(
        required=False,
        validate=validate.Range(min=-50, max=100),
        allow_none=True,
        metadata={'description': 'Maximum temperature requirement (°C)'}
    )
    priority = fields.Integer(
        required=False,
        validate=validate.Range(min=1, max=10),
        load_default=5,
        metadata={'description': 'Loading priority (1=highest)'}
    )
    color = fields.String(
        required=False,
        validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$'),
        metadata={'description': 'Display color in hex format'}
    )
    description = fields.String(
        required=False,
        validate=validate.Length(max=1000)
    )
    created_at = fields.DateTime(dump_only=True)
    
    @validates('temperature_max')
    def validate_temp_range(self, value):
        """Validate temperature range is logical."""
        # This will be checked in validates_schema with access to all fields
        pass
    
    @validates_schema
    def validate_item(self, data, **kwargs):
        """Cross-field validation for items."""
        # Temperature range validation
        temp_min = data.get('temperature_min')
        temp_max = data.get('temperature_max')
        if temp_min is not None and temp_max is not None:
            if temp_min >= temp_max:
                raise ValidationError(
                    'temperature_min must be less than temperature_max',
                    field_name='temperature_min'
                )
        
        # Fragile items shouldn't have high stack weight
        if data.get('fragile') and data.get('max_stack_weight', 0) > 100:
            raise ValidationError(
                'Fragile items should have lower max_stack_weight',
                field_name='max_stack_weight'
            )
        
        # Hazardous items require hazard class
        if data.get('storage_condition') == 'hazardous' and not data.get('hazard_class'):
            raise ValidationError(
                'Hazardous items must specify hazard_class',
                field_name='hazard_class'
            )
    
    @post_load
    def convert_to_storage_format(self, data, **kwargs):
        """Convert to database storage format."""
        data['length_mm'] = data.get('length')
        data['width_mm'] = data.get('width')
        data['height_mm'] = data.get('height')
        data['weight_kg'] = data.get('weight')
        data['is_fragile'] = data.get('fragile', False)
        data['is_stackable'] = data.get('stackable', True)
        data['max_stack_weight_kg'] = data.get('max_stack_weight')
        return data


class ItemResponseSchema(ItemSchema):
    """Schema for item response with computed fields."""
    
    volume_cm3 = fields.Method('get_volume_cm3', dump_only=True)
    density = fields.Method('get_density', dump_only=True)
    
    def get_volume_cm3(self, obj):
        """Calculate volume in cubic centimeters."""
        if isinstance(obj, dict):
            l, w, h = obj.get('length', 0), obj.get('width', 0), obj.get('height', 0)
        else:
            l, w, h = obj.length, obj.width, obj.height
        return round((l * w * h) / 1000, 2)  # mm³ to cm³
    
    def get_density(self, obj):
        """Calculate density in kg/m³."""
        if isinstance(obj, dict):
            l, w, h = obj.get('length', 0), obj.get('width', 0), obj.get('height', 0)
            weight = obj.get('weight', 0)
        else:
            l, w, h = obj.length, obj.width, obj.height
            weight = obj.weight
        
        volume_m3 = (l * w * h) / 1e9
        if volume_m3 > 0:
            return round(weight / volume_m3, 2)
        return 0


# ============================================================================
# Placement Schemas
# ============================================================================

class PlacementSchema(BaseSchema):
    """Schema for item placement in optimized layout."""
    
    id = fields.Integer(dump_only=True)
    item_id = fields.String(required=True)
    item_name = fields.String(dump_only=True)
    instance = fields.Integer(load_default=1)
    
    # Position (corner closest to origin)
    position_x = fields.Integer(required=True)
    position_y = fields.Integer(required=True)
    position_z = fields.Integer(required=True)
    
    # Dimensions after rotation
    length = fields.Integer(required=True)
    width = fields.Integer(required=True)
    height = fields.Integer(required=True)
    
    # Rotation
    rotation = fields.Integer(
        load_default=0,
        validate=validate.OneOf([0, 90, 180, 270])
    )
    
    # Stacking info
    stacked_on = fields.Integer(allow_none=True)
    weight_above = fields.Float(load_default=0)
    
    # Validation
    is_valid = fields.Boolean(load_default=True)
    violations = fields.List(fields.String(), load_default=[])
    
    # Display
    color = fields.String()


class PlacementResponseSchema(PlacementSchema):
    """Schema for placement response with computed fields."""
    
    center = fields.Method('get_center', dump_only=True)
    bounds = fields.Method('get_bounds', dump_only=True)
    
    def get_center(self, obj):
        """Calculate center point of placed item."""
        if isinstance(obj, dict):
            x = obj.get('position_x', 0) + obj.get('length', 0) / 2
            y = obj.get('position_y', 0) + obj.get('width', 0) / 2
            z = obj.get('position_z', 0) + obj.get('height', 0) / 2
        else:
            x = obj.position_x + obj.length / 2
            y = obj.position_y + obj.width / 2
            z = obj.position_z + obj.height / 2
        return {'x': x, 'y': y, 'z': z}
    
    def get_bounds(self, obj):
        """Get bounding box coordinates."""
        if isinstance(obj, dict):
            x, y, z = obj.get('position_x', 0), obj.get('position_y', 0), obj.get('position_z', 0)
            l, w, h = obj.get('length', 0), obj.get('width', 0), obj.get('height', 0)
        else:
            x, y, z = obj.position_x, obj.position_y, obj.position_z
            l, w, h = obj.length, obj.width, obj.height
        
        return {
            'min': {'x': x, 'y': y, 'z': z},
            'max': {'x': x + l, 'y': y + w, 'z': z + h}
        }


# ============================================================================
# Optimization Schemas
# ============================================================================

class OptimizationRequestSchema(BaseSchema):
    """Schema for optimization request validation."""
    
    container = fields.Nested(
        ContainerSchema,
        required=True,
        metadata={'description': 'Container dimensions and properties'}
    )
    items = fields.List(
        fields.Nested(ItemSchema),
        required=True,
        validate=validate.Length(min=1, max=1000),
        metadata={'description': 'List of items to pack'}
    )
    
    # Optimization parameters (optional overrides)
    algorithm = fields.String(
        required=False,
        validate=validate.OneOf(['genetic', 'constraint', 'hybrid']),
        load_default='genetic',
        metadata={'description': 'Optimization algorithm to use'}
    )
    population_size = fields.Integer(
        required=False,
        validate=validate.Range(min=10, max=500),
        metadata={'description': 'GA population size override'}
    )
    generations = fields.Integer(
        required=False,
        validate=validate.Range(min=5, max=500),
        metadata={'description': 'GA generations override'}
    )
    time_limit = fields.Integer(
        required=False,
        validate=validate.Range(min=10, max=600),
        metadata={'description': 'Maximum computation time in seconds'}
    )
    
    # Optimization priorities
    optimize_for = fields.String(
        required=False,
        validate=validate.OneOf(['utilization', 'stability', 'accessibility', 'balanced']),
        load_default='balanced',
        metadata={'description': 'Primary optimization objective'}
    )
    
    @validates('items')
    def validate_items_not_empty(self, items):
        """Ensure items list is not empty."""
        if not items:
            raise ValidationError('At least one item is required')
    
    @validates_schema
    def validate_request(self, data, **kwargs):
        """Validate entire optimization request."""
        container = data.get('container', {})
        items = data.get('items', [])
        
        # Check if any item is larger than container
        for i, item in enumerate(items):
            dims = sorted([item['length'], item['width'], item['height']])
            container_dims = sorted([container['length'], container['width'], container['height']])
            
            if dims[0] > container_dims[0] or dims[1] > container_dims[1] or dims[2] > container_dims[2]:
                raise ValidationError(
                    f'Item {i+1} dimensions exceed container dimensions',
                    field_name='items'
                )


class OptimizationResponseSchema(BaseSchema):
    """Schema for optimization response."""
    
    optimization_id = fields.String(required=True)
    status = fields.String(
        required=True,
        validate=validate.OneOf(['pending', 'running', 'completed', 'failed', 'cancelled'])
    )
    
    # Results
    utilization = fields.Float(metadata={'description': 'Space utilization percentage'})
    total_items = fields.Integer()
    items_packed = fields.Integer()
    items_unpacked = fields.Integer()
    total_weight = fields.Float()
    weight_utilization = fields.Float()
    
    # Placements
    placements = fields.List(fields.Nested(PlacementResponseSchema))
    unpacked_items = fields.List(fields.Nested(ItemResponseSchema))
    
    # Statistics
    computation_time = fields.Float(metadata={'description': 'Time in seconds'})
    algorithm_used = fields.String()
    fitness_score = fields.Float()
    
    # Validation results
    is_valid = fields.Boolean()
    violations = fields.List(fields.Dict())
    warnings = fields.List(fields.String())
    
    # Timestamps
    started_at = fields.DateTime()
    completed_at = fields.DateTime()
    
    # Container reference
    container = fields.Nested(ContainerResponseSchema)


class OptimizationStatusSchema(BaseSchema):
    """Schema for optimization status response."""
    
    optimization_id = fields.String(required=True)
    status = fields.String(required=True)
    progress = fields.Float(metadata={'description': 'Progress percentage 0-100'})
    current_generation = fields.Integer()
    best_fitness = fields.Float()
    estimated_time_remaining = fields.Integer(metadata={'description': 'Seconds remaining'})
    message = fields.String()


# ============================================================================
# History and Export Schemas
# ============================================================================

class OptimizationHistorySchema(BaseSchema):
    """Schema for optimization history listing."""
    
    optimization_id = fields.String()
    status = fields.String()
    utilization = fields.Float()
    items_packed = fields.Integer()
    total_items = fields.Integer()
    container_size = fields.String()
    algorithm = fields.String()
    computation_time = fields.Float()
    started_at = fields.DateTime()
    completed_at = fields.DateTime()


class ExportRequestSchema(BaseSchema):
    """Schema for export request."""
    
    format = fields.String(
        required=True,
        validate=validate.OneOf(['pdf', 'json', 'png', 'jpg', 'xlsx', 'csv'])
    )
    include_3d_view = fields.Boolean(load_default=True)
    include_item_list = fields.Boolean(load_default=True)
    include_statistics = fields.Boolean(load_default=True)
    dpi = fields.Integer(
        validate=validate.Range(min=72, max=600),
        load_default=300
    )
    page_size = fields.String(
        validate=validate.OneOf(['A4', 'Letter', 'A3']),
        load_default='A4'
    )


class ExportResponseSchema(BaseSchema):
    """Schema for export response."""
    
    export_id = fields.String()
    optimization_id = fields.String()
    format = fields.String()
    file_url = fields.String()
    file_size = fields.Integer()
    created_at = fields.DateTime()


# ============================================================================
# Bulk Operation Schemas
# ============================================================================

class BulkItemsSchema(BaseSchema):
    """Schema for bulk item operations."""
    
    items = fields.List(
        fields.Nested(ItemSchema),
        required=True,
        validate=validate.Length(min=1, max=1000)
    )
    operation = fields.String(
        validate=validate.OneOf(['create', 'update', 'delete']),
        load_default='create'
    )


class BulkResponseSchema(BaseSchema):
    """Schema for bulk operation response."""
    
    success_count = fields.Integer()
    error_count = fields.Integer()
    errors = fields.List(fields.Dict())
    created_ids = fields.List(fields.String())


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorSchema(BaseSchema):
    """Schema for error responses."""
    
    error = fields.String(required=True)
    message = fields.String(required=True)
    status_code = fields.Integer(required=True)
    details = fields.Dict()
    timestamp = fields.DateTime(load_default=datetime.utcnow)


class ValidationErrorSchema(BaseSchema):
    """Schema for validation error responses."""
    
    error = fields.String(load_default='Validation Error')
    message = fields.String(load_default='Input validation failed')
    status_code = fields.Integer(load_default=422)
    field_errors = fields.Dict(keys=fields.String(), values=fields.List(fields.String()))