"""
CargoOpt Test Configuration
Pytest fixtures and configuration for testing
"""

import pytest
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import json
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config.settings import Config, TestingConfig
from backend.config.database import DatabaseManager
from backend.algorithms.genetic_algorithm import GeneticAlgorithm
from backend.algorithms.constraint_solver import ConstraintSolver
from backend.algorithms.packing import PackingEngine
from backend.services.data_processor import DataProcessor
from backend.services.validation import ValidationService


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return TestingConfig()


@pytest.fixture(scope="session")
def test_data_dir():
    """Provide path to test data directory."""
    return Path(__file__).parent / 'test_data'


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def db_manager(test_config):
    """Provide database manager for tests."""
    # Use in-memory SQLite for tests
    db = DatabaseManager()
    # Initialize with test config
    yield db
    # Cleanup
    db.close_all_connections()


@pytest.fixture(scope="function")
def db_session(db_manager):
    """Provide a clean database session for each test."""
    with db_manager.get_cursor(commit=False) as cursor:
        yield cursor
        # Rollback after each test


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_container():
    """Provide a sample container specification."""
    return {
        'container_id': 'test_container_1',
        'name': 'Test 20ft Container',
        'length': 5898,  # mm
        'width': 2352,
        'height': 2393,
        'max_weight': 28180,  # kg
        'container_type': 'standard'
    }


@pytest.fixture
def sample_container_40ft():
    """Provide a 40ft container specification."""
    return {
        'container_id': 'test_container_40ft',
        'name': 'Test 40ft Container',
        'length': 12032,
        'width': 2352,
        'height': 2393,
        'max_weight': 26680,
        'container_type': 'standard'
    }


@pytest.fixture
def sample_items():
    """Provide sample items for packing."""
    return [
        {
            'item_id': 'item_1',
            'name': 'Box A',
            'length': 1000,
            'width': 800,
            'height': 600,
            'weight': 50,
            'quantity': 1,
            'fragile': False,
            'stackable': True,
            'rotation_allowed': True
        },
        {
            'item_id': 'item_2',
            'name': 'Box B',
            'length': 1200,
            'width': 1000,
            'height': 800,
            'weight': 75,
            'quantity': 2,
            'fragile': False,
            'stackable': True,
            'rotation_allowed': True
        },
        {
            'item_id': 'item_3',
            'name': 'Fragile Box',
            'length': 800,
            'width': 600,
            'height': 500,
            'weight': 30,
            'quantity': 1,
            'fragile': True,
            'stackable': False,
            'rotation_allowed': False
        }
    ]


@pytest.fixture
def sample_heavy_items():
    """Provide heavy items for weight testing."""
    return [
        {
            'item_id': 'heavy_1',
            'name': 'Heavy Machinery',
            'length': 2000,
            'width': 1500,
            'height': 1200,
            'weight': 5000,
            'quantity': 1,
            'fragile': False,
            'stackable': False,
            'rotation_allowed': False
        },
        {
            'item_id': 'heavy_2',
            'name': 'Steel Crate',
            'length': 1800,
            'width': 1200,
            'height': 1000,
            'weight': 3000,
            'quantity': 1,
            'fragile': False,
            'stackable': True,
            'rotation_allowed': True
        }
    ]


@pytest.fixture
def sample_hazmat_items():
    """Provide hazardous materials items."""
    return [
        {
            'item_id': 'hazmat_1',
            'name': 'Flammable Liquid',
            'length': 1000,
            'width': 800,
            'height': 600,
            'weight': 100,
            'quantity': 1,
            'hazard_class': '3',
            'storage_condition': 'hazardous'
        },
        {
            'item_id': 'hazmat_2',
            'name': 'Corrosive Material',
            'length': 800,
            'width': 600,
            'height': 500,
            'weight': 80,
            'quantity': 1,
            'hazard_class': '8',
            'storage_condition': 'hazardous'
        }
    ]


@pytest.fixture
def sample_optimization_request(sample_container, sample_items):
    """Provide complete optimization request."""
    return {
        'container': sample_container,
        'items': sample_items,
        'algorithm': 'genetic',
        'parameters': {
            'population_size': 20,
            'generations': 10,
            'time_limit': 30
        }
    }


# ============================================================================
# Algorithm Fixtures
# ============================================================================

@pytest.fixture
def genetic_algorithm(sample_container, sample_items, test_config):
    """Provide configured genetic algorithm instance."""
    return GeneticAlgorithm(sample_container, sample_items, test_config)


@pytest.fixture
def constraint_solver(sample_container, sample_items, test_config):
    """Provide configured constraint solver instance."""
    return ConstraintSolver(sample_container, sample_items, test_config)


@pytest.fixture
def packing_engine(sample_container, sample_items):
    """Provide packing engine instance."""
    return PackingEngine(sample_container, sample_items)


# ============================================================================
# Service Fixtures
# ============================================================================

@pytest.fixture
def data_processor(test_config):
    """Provide data processor service."""
    return DataProcessor(test_config)


@pytest.fixture
def validation_service(test_config):
    """Provide validation service."""
    return ValidationService(test_config)


# ============================================================================
# Test Data Loaders
# ============================================================================

@pytest.fixture
def load_test_data(test_data_dir):
    """Provide function to load test data from JSON files."""
    def _load(filename):
        filepath = test_data_dir / filename
        if not filepath.exists():
            pytest.skip(f"Test data file not found: {filename}")
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    return _load


@pytest.fixture
def test_containers_data(load_test_data):
    """Load test containers data."""
    return load_test_data('test_containers.json')


@pytest.fixture
def test_items_data(load_test_data):
    """Load test items data."""
    return load_test_data('test_items.json')


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_optimization_result():
    """Provide mock optimization result."""
    return {
        'optimization_id': 'test_opt_123',
        'status': 'completed',
        'algorithm': 'genetic_algorithm',
        'utilization': 85.5,
        'items_packed': 10,
        'total_items': 10,
        'computation_time': 5.2,
        'fitness_score': 0.92,
        'placements': [
            {
                'item_index': 0,
                'x': 0,
                'y': 0,
                'z': 0,
                'length': 1000,
                'width': 800,
                'height': 600,
                'rotation': 0,
                'weight': 50
            }
        ],
        'is_valid': True,
        'violations': []
    }


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def assert_almost_equal():
    """Provide function for floating point comparison."""
    def _assert(actual, expected, tolerance=0.01):
        assert abs(actual - expected) < tolerance, \
            f"Expected {expected}, got {actual} (tolerance: {tolerance})"
    return _assert


@pytest.fixture
def timer():
    """Provide a simple timer for performance testing."""
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = datetime.now()
        
        def stop(self):
            self.end_time = datetime.now()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return (self.end_time - self.start_time).total_seconds()
            return None
    
    return Timer()


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "algorithms: marks tests for optimization algorithms"
    )
    config.addinivalue_line(
        "markers", "services: marks tests for service layer"
    )
    config.addinivalue_line(
        "markers", "api: marks tests for API endpoints"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    # Skip slow tests unless explicitly requested
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="run slow tests"
    )
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests"
    )


# ============================================================================
# Session Hooks
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment before all tests."""
    # Set environment variables for testing
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'true'
    
    yield
    
    # Cleanup after all tests
    pass


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test(tmpdir):
    """Clean up after each test."""
    yield
    # Cleanup temporary files, database connections, etc.