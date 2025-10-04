import pytest
import tempfile
import os
from backend.algorithms.constraint_solver import Container, Vehicle

@pytest.fixture
def temp_export_dir():
    """Create a temporary directory for export tests"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir

@pytest.fixture
def sample_container():
    """Provide a sample container for testing"""
    return Container(
        id="test_container",
        name="Test Container",
        length=1.0,
        width=1.0,
        height=1.0,
        weight=100,
        type="box"
    )

@pytest.fixture
def sample_vehicle():
    """Provide a sample vehicle for testing"""
    return Vehicle(
        id="test_vehicle",
        type="small_truck",
        max_weight=1000,
        length=3.0,
        width=2.0,
        height=2.0,
        emission_factor=0.00012
    )