"""
Service Layer Tests
Tests for service classes (DataProcessor, ValidationService, etc.)
"""

import pytest
from backend.services.data_processor import DataProcessor, DataTransformer
from backend.services.validation import ValidationService
from backend.services.emission_calculator import EmissionCalculator


@pytest.mark.services
@pytest.mark.unit
class TestDataProcessor:
    """Test data processing service."""
    
    def test_normalize_dimensions(self, data_processor):
        """Test dimension normalization."""
        item = {'length': 1, 'width': 0.8, 'height': 0.6}  # meters
        normalized = DataTransformer.normalize_dimensions(item, 'm')
        
        assert normalized['length'] == 1000  # mm
        assert normalized['width'] == 800
        assert normalized['height'] == 600
    
    def test_expand_quantities(self, data_processor):
        """Test quantity expansion."""
        items = [{'item_id': 'test', 'length': 1000, 'width': 800, 
                 'height': 600, 'weight': 50, 'quantity': 3}]
        
        expanded = DataTransformer.expand_quantities(items)
        assert len(expanded) == 3
        assert all(item['instance'] in [1, 2, 3] for item in expanded)
    
    def test_process_optimization_input(self, data_processor, 
                                       sample_container, sample_items):
        """Test complete input processing."""
        container, items = data_processor.process_optimization_input(
            sample_container, sample_items, normalize=True
        )
        
        assert 'volume' in container
        assert len(items) > 0
        assert all('volume' in item for item in items)


@pytest.mark.services
@pytest.mark.unit
class TestValidationService:
    """Test validation service."""
    
    def test_validate_container(self, validation_service, sample_container):
        """Test container validation."""
        is_valid, errors = validation_service.container_validator.validate(sample_container)
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_items(self, validation_service, sample_items):
        """Test items validation."""
        is_valid, errors = validation_service.item_validator.validate_items_list(sample_items)
        assert is_valid
    
    def test_validate_optimization_request(self, validation_service, 
                                          sample_optimization_request):
        """Test complete request validation."""
        is_valid, errors = validation_service.validate_optimization_request(
            sample_optimization_request
        )
        assert is_valid
        assert len(errors) == 0


@pytest.mark.services
class TestEmissionCalculator:
    """Test emission calculator."""
    
    def test_calculate_emissions(self):
        """Test emissions calculation."""
        calc = EmissionCalculator()
        
        emissions = calc.carbon_analyzer.calculate_emissions(
            transport_mode='truck',
            distance=100,  # km
            cargo_weight_kg=5000,
            utilization=0.8
        )
        
        assert emissions['co2_emissions_kg'] > 0
        assert emissions['transport_mode'] == 'truck'