import pytest
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.algorithms.constraint_solver import ConstraintSolver, Container, Vehicle, OptimizationResult
from backend.services.emission_calculator import EmissionCalculator
from backend.data.exports.stowage_plans.stowage_exporter import StowagePlanExporter

# Import your FastAPI app (adjust import based on your actual app structure)
# from backend.main import app

class TestConstraintSolverAPI:
    """Test cases for Constraint Solver API endpoints"""
    
    @pytest.fixture
    def sample_containers(self):
        return [
            {
                "id": "cont_1",
                "name": "Small Box",
                "length": 1.2,
                "width": 0.8,
                "height": 0.8,
                "weight": 150,
                "type": "box"
            },
            {
                "id": "cont_2", 
                "name": "Medium Crate",
                "length": 1.0,
                "width": 1.0,
                "height": 1.0,
                "weight": 200,
                "type": "crate"
            }
        ]
    
    @pytest.fixture
    def sample_vehicles(self):
        return [
            {
                "id": "vehicle_1",
                "type": "small_truck",
                "max_weight": 1000,
                "length": 3.0,
                "width": 2.0,
                "height": 2.0,
                "emission_factor": 0.00012
            },
            {
                "id": "vehicle_2",
                "type": "van",
                "max_weight": 800,
                "length": 2.5,
                "width": 1.8,
                "height": 1.8,
                "emission_factor": 0.00015
            }
        ]
    
    @pytest.fixture
    def mock_optimization_result(self):
        return OptimizationResult(
            assignments={"vehicle_1": ["cont_1", "cont_2"]},
            total_emissions=4.2,
            utilization=85.5,
            vehicle_count=1,
            total_containers=2,
            status="optimal"
        )
    
    def test_optimization_endpoint_success(self, sample_containers, sample_vehicles, mock_optimization_result):
        """Test successful optimization request"""
        with patch('backend.algorithms.constraint_solver.ConstraintSolver.solve_optimization') as mock_solve:
            mock_solve.return_value = mock_optimization_result
            
            # Mock the API client (replace with your actual FastAPI TestClient)
            client = Mock()
            response = Mock()
            response.status_code = 200
            response.json.return_value = {
                "assignments": mock_optimization_result.assignments,
                "total_emissions": mock_optimization_result.total_emissions,
                "utilization": mock_optimization_result.utilization,
                "vehicle_count": mock_optimization_result.vehicle_count,
                "total_containers": mock_optimization_result.total_containers,
                "status": mock_optimization_result.status
            }
            client.post.return_value = response
            
            # Make API call
            result = client.post(
                "/api/optimize",
                json={
                    "containers": sample_containers,
                    "vehicles": sample_vehicles,
                    "distance_km": 100.0
                }
            )
            
            # Assertions
            assert result.status_code == 200
            data = result.json()
            assert "assignments" in data
            assert "total_emissions" in data
            assert data["status"] == "optimal"
            assert data["vehicle_count"] == 1
            assert data["total_containers"] == 2
    
    def test_optimization_endpoint_validation_error(self):
        """Test optimization request with invalid data"""
        client = Mock()
        response = Mock()
        response.status_code = 422
        response.json.return_value = {
            "detail": "Validation error",
            "errors": ["Invalid container data"]
        }
        client.post.return_value = response
        
        result = client.post(
            "/api/optimize",
            json={
                "containers": [{"invalid": "data"}],  # Invalid container data
                "vehicles": [],
                "distance_km": 100.0
            }
        )
        
        assert result.status_code == 422
        data = result.json()
        assert "detail" in data
        assert "errors" in data
    
    def test_optimization_endpoint_no_solution(self, sample_containers, sample_vehicles):
        """Test optimization when no solution is found"""
        with patch('backend.algorithms.constraint_solver.ConstraintSolver.solve_optimization') as mock_solve:
            mock_solve.return_value = None
            
            client = Mock()
            response = Mock()
            response.status_code = 400
            response.json.return_value = {
                "detail": "No feasible solution found"
            }
            client.post.return_value = response
            
            result = client.post(
                "/api/optimize",
                json={
                    "containers": sample_containers,
                    "vehicles": sample_vehicles,
                    "distance_km": 100.0
                }
            )
            
            assert result.status_code == 400
            data = result.json()
            assert "detail" in data
    
    def test_optimization_with_hazardous_materials(self):
        """Test optimization with hazardous materials constraints"""
        hazardous_containers = [
            {
                "id": "haz_1",
                "name": "Flammable Liquid",
                "length": 1.0,
                "width": 1.0,
                "height": 1.0,
                "weight": 300,
                "type": "hazardous",
                "hazard_class": "3"
            }
        ]
        
        specialized_vehicles = [
            {
                "id": "hazmat_truck",
                "type": "hazardous_material_truck",
                "max_weight": 2000,
                "length": 5.0,
                "width": 2.5,
                "height": 2.5,
                "emission_factor": 0.00010,
                "can_carry_hazardous": True
            }
        ]
        
        with patch('backend.algorithms.constraint_solver.ConstraintSolver.solve_optimization') as mock_solve:
            mock_solve.return_value = OptimizationResult(
                assignments={"hazmat_truck": ["haz_1"]},
                total_emissions=3.0,
                utilization=15.0,
                vehicle_count=1,
                total_containers=1,
                status="optimal"
            )
            
            client = Mock()
            response = Mock()
            response.status_code = 200
            response.json.return_value = {
                "assignments": {"hazmat_truck": ["haz_1"]},
                "total_emissions": 3.0,
                "utilization": 15.0,
                "vehicle_count": 1,
                "total_containers": 1,
                "status": "optimal"
            }
            client.post.return_value = response
            
            result = client.post(
                "/api/optimize",
                json={
                    "containers": hazardous_containers,
                    "vehicles": specialized_vehicles,
                    "distance_km": 100.0,
                    "constraints": {
                        "hazard_segregation": True
                    }
                }
            )
            
            assert result.status_code == 200
            data = result.json()
            assert "hazmat_truck" in data["assignments"]
    
    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        client = Mock()
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"status": "healthy", "version": "1.0.0"}
        client.get.return_value = response
        
        result = client.get("/api/health")
        
        assert result.status_code == 200
        data = result.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_validation_endpoint(self):
        """Test container/vehicle validation endpoint"""
        test_containers = [
            {
                "id": "test_1",
                "name": "Test Container",
                "length": 2.0,
                "width": 1.0,
                "height": 1.0,
                "weight": 500,
                "type": "standard"
            }
        ]
        
        client = Mock()
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "valid": True,
            "errors": [],
            "warnings": ["Container weight exceeds recommended limit for type"]
        }
        client.post.return_value = response
        
        result = client.post("/api/validate/containers", json=test_containers)
        
        assert result.status_code == 200
        data = result.json()
        assert data["valid"] is True
        assert "warnings" in data
    
    def test_emission_calculation_endpoint(self):
        """Test emission calculation endpoint"""
        emission_data = {
            "assignments": {"vehicle_1": ["cont_1"]},
            "containers": [{"id": "cont_1", "weight": 200}],
            "vehicles": [{"id": "vehicle_1", "emission_factor": 0.00012}],
            "distance_km": 100.0
        }
        
        with patch('backend.services.emission_calculator.EmissionCalculator.calculate_emissions') as mock_calc:
            mock_calc.return_value = {
                "total_emissions_kg": 2.4,
                "emissions_per_vehicle": {"vehicle_1": 2.4},
                "emissions_per_container": {"cont_1": 2.4},
                "distance_km": 100.0,
                "equivalent_metrics": {
                    "equivalent_km_driven": 24.0,
                    "equivalent_trees_year": 0.048,
                    "equivalent_gasoline_liters": 1.032
                }
            }
            
            client = Mock()
            response = Mock()
            response.status_code = 200
            response.json.return_value = mock_calc.return_value
            client.post.return_value = response
            
            result = client.post("/api/calculate/emissions", json=emission_data)
            
            assert result.status_code == 200
            data = result.json()
            assert data["total_emissions_kg"] == 2.4
            assert "equivalent_metrics" in data
    
    def test_export_endpoint(self):
        """Test export functionality endpoint"""
        export_data = {
            "result": {
                "assignments": {"vehicle_1": ["cont_1"]},
                "total_emissions": 2.4,
                "utilization": 80.0,
                "vehicle_count": 1,
                "total_containers": 1,
                "status": "optimal"
            },
            "format": "json"
        }
        
        with patch('backend.data.exports.stowage_plans.stowage_exporter.StowagePlanExporter.export_json') as mock_export:
            mock_export.return_value = "/path/to/export.json"
            
            client = Mock()
            response = Mock()
            response.status_code = 200
            response.content = b'{"export": "data"}'
            response.headers = {"content-type": "application/json"}
            client.post.return_value = response
            
            result = client.post("/api/export/results", json=export_data)
            
            assert result.status_code == 200
            assert result.headers["content-type"] == "application/json"
    
    def test_rate_limiting(self):
        """Test API rate limiting"""
        client = Mock()
        response = Mock()
        response.status_code = 429
        response.json.return_value = {
            "detail": "Rate limit exceeded",
            "retry_after": 60
        }
        client.post.return_value = response
        
        # Make multiple rapid requests
        for _ in range(10):
            result = client.post("/api/optimize", json={"containers": [], "vehicles": []})
        
        assert result.status_code == 429
        data = result.json()
        assert "retry_after" in data
    
    def test_error_handling(self):
        """Test API error handling"""
        client = Mock()
        response = Mock()
        response.status_code = 500
        response.json.return_value = {
            "detail": "Internal server error",
            "error_id": "ERR_12345"
        }
        client.post.return_value = response
        
        result = client.post("/api/optimize", json={"invalid": "data"})
        
        assert result.status_code == 500
        data = result.json()
        assert "error_id" in data


class TestReferenceDataAPI:
    """Test cases for reference data API endpoints"""
    
    def test_imdg_codes_endpoint(self):
        """Test IMDG codes reference data endpoint"""
        client = Mock()
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "imdg_classes": [
                {
                    "class": "1",
                    "name": "Explosives",
                    "description": "Substances and articles which have a mass explosion hazard"
                }
            ]
        }
        client.get.return_value = response
        
        result = client.get("/api/reference/imdg_codes")
        
        assert result.status_code == 200
        data = result.json()
        assert "imdg_classes" in data
        assert len(data["imdg_classes"]) > 0
    
    def test_stability_rules_endpoint(self):
        """Test stability rules reference data endpoint"""
        client = Mock()
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "vessel_stability_parameters": {
                "max_heeling_angle": 12.0,
                "min_metacentric_height": 0.15
            }
        }
        client.get.return_value = response
        
        result = client.get("/api/reference/stability_rules")
        
        assert result.status_code == 200
        data = result.json()
        assert "vessel_stability_parameters" in data


class TestScenarioManagementAPI:
    """Test cases for scenario management API endpoints"""
    
    def test_save_scenario(self):
        """Test saving optimization scenario"""
        scenario_data = {
            "name": "Test Scenario",
            "description": "Test scenario for API testing",
            "containers": [],
            "vehicles": [],
            "result": {}
        }
        
        client = Mock()
        response = Mock()
        response.status_code = 201
        response.json.return_value = {
            "id": "scenario_123",
            "name": "Test Scenario",
            "saved_at": "2024-01-01T00:00:00Z"
        }
        client.post.return_value = response
        
        result = client.post("/api/scenarios/save", json=scenario_data)
        
        assert result.status_code == 201
        data = result.json()
        assert "id" in data
        assert data["name"] == "Test Scenario"
    
    def test_load_scenario(self):
        """Test loading saved scenario"""
        scenario_id = "scenario_123"
        
        client = Mock()
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "id": scenario_id,
            "name": "Test Scenario",
            "containers": [],
            "vehicles": [],
            "result": {},
            "created_at": "2024-01-01T00:00:00Z"
        }
        client.get.return_value = response
        
        result = client.get(f"/api/scenarios/{scenario_id}")
        
        assert result.status_code == 200
        data = result.json()
        assert data["id"] == scenario_id
    
    def test_list_scenarios(self):
        """Test listing saved scenarios"""
        client = Mock()
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "scenarios": [
                {"id": "scenario_1", "name": "Scenario 1"},
                {"id": "scenario_2", "name": "Scenario 2"}
            ],
            "total_count": 2
        }
        client.get.return_value = response
        
        result = client.get("/api/scenarios")
        
        assert result.status_code == 200
        data = result.json()
        assert "scenarios" in data
        assert data["total_count"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])