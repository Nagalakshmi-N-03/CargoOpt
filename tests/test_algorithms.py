import pytest
import asyncio
import json
import os
import sys
from typing import Dict, List, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.algorithms.packing import PackingAlgorithm
from backend.algorithms.genetic_algorithm import GeneticAlgorithm
from backend.algorithms.stowage import StowageOptimizer
from backend.services.validation import ValidationService
from backend.models.stowage_plan import StowagePlan, ContainerAssignment, StowageStatus

class TestAlgorithms:
    """Test cases for optimization algorithms"""
    
    @classmethod
    def setup_class(cls):
        """Setup test data"""
        cls.validation_service = ValidationService()
        cls.packing_algo = PackingAlgorithm()
        cls.genetic_algo = GeneticAlgorithm()
        cls.stowage_algo = StowageOptimizer()
        
        # Load test data
        test_data_path = os.path.join(os.path.dirname(__file__), 'test_data', 'test_containers.json')
        with open(test_data_path, 'r') as f:
            cls.test_data = json.load(f)
    
    def test_packing_algorithm_basic(self):
        """Test basic packing algorithm functionality"""
        container = self.test_data['standard_containers'][0]
        items = [item for item in self.test_data['test_items'] if item['id'] in [1, 4]]
        
        result = self.packing_algo.optimize(container, items)
        
        assert 'placements' in result
        assert 'metrics' in result
        assert result['metrics']['utilization_rate'] >= 0
        assert result['metrics']['total_items_packed'] >= 0
        
        # Validate the result
        validation = self.validation_service.validate_placement(container, result['placements'])
        assert validation.is_valid, f"Placement validation failed: {validation.issues}"
    
    def test_genetic_algorithm_basic(self):
        """Test genetic algorithm functionality"""
        container = self.test_data['standard_containers'][1]
        items = [item for item in self.test_data['test_items'] if item['id'] in [2, 3]]
        
        result = self.genetic_algo.optimize(container, items, generations=10)
        
        assert 'placements' in result
        assert 'metrics' in result
        assert result['metrics']['utilization_rate'] >= 0
        assert result['metrics']['total_items_packed'] >= 0
        
        # Validate the result
        validation = self.validation_service.validate_placement(container, result['placements'])
        assert validation.is_valid, f"Placement validation failed: {validation.issues}"
    
    def test_stowage_algorithm_basic(self):
        """Test stowage algorithm functionality"""
        containers = self.test_data['standard_containers'][:2]  # Use first two containers
        items = self.test_data['test_items'][:3]  # Use first three items
        
        result = self.stowage_algo.optimize(containers, items)
        
        assert 'container_assignments' in result
        assert 'overall_metrics' in result
        assert result['overall_metrics']['total_containers_used'] >= 0
        assert result['overall_metrics']['total_items_packed'] >= 0
        
        # Validate each container assignment
        for container_id, assignment in result['container_assignments'].items():
            container_data = assignment['container']
            placements = assignment.get('items', [])  # Note: stowage might not provide detailed placements
            
            if placements and isinstance(placements[0], dict) and 'position' in placements[0]:
                validation = self.validation_service.validate_placement(container_data, placements)
                assert validation.is_valid, f"Container {container_id} validation failed: {validation.issues}"
    
    def test_algorithm_comparison(self):
        """Compare different algorithms on the same problem"""
        container = self.test_data['standard_containers'][0]
        items = [item for item in self.test_data['test_items'] if item['id'] in [1, 2]]
        
        # Run both algorithms
        packing_result = self.packing_algo.optimize(container, items)
        genetic_result = self.genetic_algo.optimize(container, items, generations=20)
        
        # Both should produce valid results
        packing_validation = self.validation_service.validate_placement(container, packing_result['placements'])
        genetic_validation = self.validation_service.validate_placement(container, genetic_result['placements'])
        
        assert packing_validation.is_valid, f"Packing algorithm failed: {packing_validation.issues}"
        assert genetic_validation.is_valid, f"Genetic algorithm failed: {genetic_validation.issues}"
        
        # Both should pack at least some items
        assert packing_result['metrics']['total_items_packed'] > 0
        assert genetic_result['metrics']['total_items_packed'] > 0
    
    def test_empty_container(self):
        """Test algorithm behavior with empty container"""
        container = self.test_data['standard_containers'][0]
        items = []  # No items
        
        result = self.packing_algo.optimize(container, items)
        
        assert result['metrics']['total_items_packed'] == 0
        assert result['metrics']['utilization_rate'] == 0
        assert len(result['placements']) == 0
    
    def test_single_item(self):
        """Test algorithm with single item"""
        container = self.test_data['standard_containers'][0]
        items = [self.test_data['test_items'][0]]  # Single small box
        
        result = self.packing_algo.optimize(container, items)
        
        assert result['metrics']['total_items_packed'] == 1
        assert result['metrics']['utilization_rate'] > 0
        assert len(result['placements']) == 1
        
        # Validate placement
        validation = self.validation_service.validate_placement(container, result['placements'])
        assert validation.is_valid, f"Single item placement failed: {validation.issues}"
    
    @pytest.mark.asyncio
    async def test_async_optimization(self):
        """Test async optimization workflow"""
        from backend.services.optimization import OptimizationService
        
        # Mock database session
        class MockDB:
            def query(self, *args, **kwargs):
                return self
            def filter(self, *args, **kwargs):
                return self
            def order_by(self, *args, **kwargs):
                return self
            def limit(self, *args, **kwargs):
                return self
            def all(self):
                return []
            def add(self, *args, **kwargs):
                pass
            def commit(self):
                pass
        
        optimization_service = OptimizationService(MockDB())
        
        container = self.test_data['standard_containers'][0]
        items = self.test_data['test_items'][:2]
        
        result = await optimization_service.optimize_single_container(
            container_data=container,
            items_data=items,
            algorithm="packing"
        )
        
        assert result['success'] == True
        assert 'result' in result
        assert result['result']['metrics']['total_items_packed'] >= 0
    
    def test_stowage_plan_model(self):
        """Test StowagePlan model functionality"""
        from datetime import datetime
        
        # Create a mock container assignment
        container_assignment = ContainerAssignment(
            container_id="test_container_1",
            container_data=self.test_data['standard_containers'][0],
            items=self.test_data['test_items'][:2],
            placements=[],
            utilization_rate=0.75,
            weight_utilization=0.6,
            status="fully_loaded",
            total_volume_used=1000.0,