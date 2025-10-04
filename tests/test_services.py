import pytest
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.algorithms.constraint_solver import ConstraintSolver, Container, Vehicle, OptimizationResult
from backend.services.emission_calculator import EmissionCalculator, EmissionResult
from backend.data.exports.stowage_plans.stowage_exporter import StowagePlanExporter


class TestConstraintSolver:
    """Test cases for Constraint Solver service"""
    
    @pytest.fixture
    def solver(self):
        return ConstraintSolver()
    
    @pytest.fixture
    def sample_containers(self):
        return [
            Container(
                id="cont_1", name="Small Box", length=1.2, width=0.8, height=0.8,
                weight=150, type="box"
            ),
            Container(
                id="cont_2", name="Medium Crate", length=1.0, width=1.0, height=1.0,
                weight=200, type="crate"
            ),
            Container(
                id="cont_3", name="Large Pallet", length=1.5, width=1.0, height=0.5,
                weight=100, type="pallet"
            )
        ]
    
    @pytest.fixture
    def sample_vehicles(self):
        return [
            Vehicle(
                id="vehicle_1", type="small_truck", max_weight=1000,
                length=3.0, width=2.0, height=2.0, emission_factor=0.00012
            ),
            Vehicle(
                id="vehicle_2", type="van", max_weight=800,
                length=2.5, width=1.8, height=1.8, emission_factor=0.00015
            )
        ]
    
    def test_solver_initialization(self, solver):
        """Test constraint solver initialization"""
        assert solver is not None
        assert hasattr(solver, 'solve_optimization')
        assert hasattr(solver, '_validate_inputs')
    
    def test_solve_optimization_success(self, solver, sample_containers, sample_vehicles):
        """Test successful optimization"""
        with patch('pulp.LpProblem') as mock_problem:
            mock_problem.return_value.solve.return_value = 1  # Optimal solution
            
            result = solver.solve_optimization(sample_containers, sample_vehicles, 100.0)
            
            assert result is not None
            assert isinstance(result, OptimizationResult)
            assert hasattr(result, 'assignments')
            assert hasattr(result, 'total_emissions')
            assert hasattr(result, 'utilization')
            assert hasattr(result, 'vehicle_count')
            assert hasattr(result, 'total_containers')
            assert hasattr(result, 'status')
    
    def test_solve_optimization_no_vehicles(self, solver, sample_containers):
        """Test optimization with no vehicles"""
        vehicles = []
        
        result = solver.solve_optimization(sample_containers, vehicles, 100.0)
        
        assert result is not None
        assert result.status in ['invalid_input', 'fallback']
        assert result.vehicle_count == 0
    
    def test_solve_optimization_no_containers(self, solver, sample_vehicles):
        """Test optimization with no containers"""
        containers = []
        
        result = solver.solve_optimization(containers, sample_vehicles, 100.0)
        
        assert result is not None
        assert result.status in ['invalid_input', 'fallback']
        assert result.total_containers == 0
    
    def test_solve_optimization_overweight_containers(self, solver):
        """Test optimization with containers that exceed vehicle capacity"""
        heavy_container = Container(
            id="heavy_1", name="Heavy Container", length=1.0, width=1.0, height=1.0,
            weight=2000, type="heavy"  # Weight exceeds vehicle capacity
        )
        
        small_vehicle = Vehicle(
            id="small_1", type="small_van", max_weight=500,  # Too small for container
            length=2.0, width=1.5, height=1.5, emission_factor=0.00015
        )
        
        result = solver.solve_optimization([heavy_container], [small_vehicle], 100.0)
        
        assert result is not None
        # Should return fallback or indicate no solution
    
    def test_solve_optimization_hazardous_materials(self, solver):
        """Test optimization with hazardous materials"""
        hazardous_container = Container(
            id="haz_1", name="Flammable Liquid", length=1.0, width=1.0, height=1.0,
            weight=300, type="hazardous", hazard_class="3"
        )
        
        regular_vehicle = Vehicle(
            id="regular_1", type="regular_truck", max_weight=1000,
            length=3.0, width=2.0, height=2.0, emission_factor=0.00012,
            can_carry_hazardous=False
        )
        
        hazmat_vehicle = Vehicle(
            id="hazmat_1", type="hazmat_truck", max_weight=2000,
            length=5.0, width=2.5, height=2.5, emission_factor=0.00010,
            can_carry_hazardous=True
        )
        
        result = solver.solve_optimization(
            [hazardous_container], 
            [regular_vehicle, hazmat_vehicle], 
            100.0
        )
        
        assert result is not None
        # Hazardous container should be assigned to hazmat vehicle
    
    def test_validate_inputs_success(self, solver, sample_containers, sample_vehicles):
        """Test input validation with valid data"""
        validation_result = solver._validate_inputs(sample_containers, sample_vehicles)
        
        assert validation_result["valid"] is True
        assert len(validation_result["violations"]) == 0
    
    def test_validate_inputs_invalid_container(self, solver, sample_vehicles):
        """Test input validation with invalid container data"""
        invalid_container = Container(
            id="invalid_1", name="Invalid", length=0, width=0, height=0,  # Invalid dimensions
            weight=-100, type="invalid"  # Negative weight
        )
        
        validation_result = solver._validate_inputs([invalid_container], sample_vehicles)
        
        assert validation_result["valid"] is False
        assert len(validation_result["violations"]) > 0
    
    def test_validate_inputs_duplicate_ids(self, solver, sample_vehicles):
        """Test input validation with duplicate container IDs"""
        duplicate_container_1 = Container(
            id="duplicate", name="First", length=1.0, width=1.0, height=1.0,
            weight=100, type="box"
        )
        duplicate_container_2 = Container(
            id="duplicate", name="Second", length=1.0, width=1.0, height=1.0,
            weight=200, type="crate"  # Same ID
        )
        
        validation_result = solver._validate_inputs(
            [duplicate_container_1, duplicate_container_2], 
            sample_vehicles
        )
        
        assert validation_result["valid"] is False
        assert any("duplicate" in violation.lower() for violation in validation_result["violations"])
    
    def test_can_fit_method(self, solver):
        """Test container fitting logic"""
        small_container = Container(
            id="small", name="Small", length=1.0, width=1.0, height=1.0,
            weight=100, type="box"
        )
        
        large_vehicle = Vehicle(
            id="large", type="large_truck", max_weight=2000,
            length=5.0, width=2.5, height=2.5, emission_factor=0.00008
        )
        
        # Small container should fit in large vehicle
        assert solver._can_fit(small_container, large_vehicle) is True
        
        # Test with container that's too large
        huge_container = Container(
            id="huge", name="Huge", length=6.0, width=3.0, height=3.0,  # Too large
            weight=100, type="oversize"
        )
        
        assert solver._can_fit(huge_container, large_vehicle) is False
    
    def test_fallback_solution(self, solver, sample_containers, sample_vehicles):
        """Test fallback solution generation"""
        # Force solver to use fallback by making optimization fail
        with patch('pulp.LpProblem') as mock_problem:
            mock_problem.return_value.solve.return_value = -1  # No solution
            
            result = solver.solve_optimization(sample_containers, sample_vehicles, 100.0)
            
            assert result is not None
            assert result.status in ['fallback', 'feasible']
    
    def test_volume_calculation(self, solver):
        """Test volume calculation for containers and vehicles"""
        container = Container(
            id="test", name="Test", length=2.0, width=1.5, height=1.0,
            weight=100, type="box"
        )
        
        vehicle = Vehicle(
            id="test_vehicle", type="test", max_weight=1000,
            length=4.0, width=2.0, height=2.0, emission_factor=0.00010
        )
        
        container_volume = container.length * container.width * container.height
        vehicle_volume = vehicle.length * vehicle.width * vehicle.height
        
        assert container_volume == 3.0  # 2.0 * 1.5 * 1.0
        assert vehicle_volume == 16.0   # 4.0 * 2.0 * 2.0
        assert container_volume <= vehicle_volume  # Should fit


class TestEmissionCalculator:
    """Test cases for Emission Calculator service"""
    
    @pytest.fixture
    def calculator(self):
        return EmissionCalculator()
    
    @pytest.fixture
    def sample_assignments(self):
        return {
            "vehicle_1": ["cont_1", "cont_2"],
            "vehicle_2": ["cont_3"]
        }
    
    @pytest.fixture
    def sample_containers(self):
        return [
            {"id": "cont_1", "weight": 150},
            {"id": "cont_2", "weight": 200},
            {"id": "cont_3", "weight": 100}
        ]
    
    @pytest.fixture
    def sample_vehicles(self):
        return [
            {"id": "vehicle_1", "emission_factor": 0.00012},
            {"id": "vehicle_2", "emission_factor": 0.00015}
        ]
    
    def test_calculator_initialization(self, calculator):
        """Test emission calculator initialization"""
        assert calculator is not None
        assert hasattr(calculator, 'calculate_emissions')
        assert hasattr(calculator, 'calculate_savings')
        assert hasattr(calculator.factors, 'TRUCK_SMALL')
        assert hasattr(calculator.factors, 'TRUCK_MEDIUM')
        assert hasattr(calculator.factors, 'TRUCK_LARGE')
    
    def test_calculate_emissions_success(self, calculator, sample_assignments, sample_containers, sample_vehicles):
        """Test successful emission calculation"""
        result = calculator.calculate_emissions(
            sample_assignments, sample_containers, sample_vehicles, 100.0
        )
        
        assert isinstance(result, EmissionResult)
        assert hasattr(result, 'total_emissions_kg')
        assert hasattr(result, 'emissions_per_vehicle')
        assert hasattr(result, 'emissions_per_container')
        assert hasattr(result, 'distance_km')
        assert hasattr(result, 'equivalent_metrics')
        
        # Verify calculations
        expected_emissions_vehicle_1 = (150 + 200) * 0.00012 * 100  # 4.2 kg
        expected_emissions_vehicle_2 = 100 * 0.00015 * 100  # 1.5 kg
        expected_total = expected_emissions_vehicle_1 + expected_emissions_vehicle_2
        
        assert abs(result.total_emissions_kg - expected_total) < 0.01
        assert "vehicle_1" in result.emissions_per_vehicle
        assert "vehicle_2" in result.emissions_per_vehicle
    
    def test_calculate_emissions_missing_data(self, calculator):
        """Test emission calculation with missing data"""
        result = calculator.calculate_emissions({}, [], [], 100.0)
        
        assert result.total_emissions_kg == 0.0
        assert result.emissions_per_vehicle == {}
        assert result.emissions_per_container == {}
    
    def test_calculate_emissions_unknown_vehicle(self, calculator, sample_assignments, sample_containers):
        """Test emission calculation with unknown vehicle"""
        vehicles = [{"id": "unknown_vehicle", "emission_factor": 0.00010}]
        
        result = calculator.calculate_emissions(
            sample_assignments, sample_containers, vehicles, 100.0
        )
        
        # Should handle missing vehicles gracefully
        assert result is not None
    
    def test_get_emission_factor(self, calculator):
        """Test emission factor selection based on vehicle type"""
        test_cases = [
            ({"type": "small_truck"}, calculator.factors.TRUCK_SMALL),
            ({"type": "medium_truck"}, calculator.factors.TRUCK_MEDIUM),
            ({"type": "large_truck"}, calculator.factors.TRUCK_LARGE),
            ({"type": "van"}, calculator.factors.VAN),
            ({"type": "unknown"}, calculator.factors.DEFAULT),
            ({}, calculator.factors.DEFAULT)
        ]
        
        for vehicle_data, expected_factor in test_cases:
            factor = calculator._get_emission_factor(vehicle_data)
            assert factor == expected_factor
    
    def test_calculate_savings(self, calculator):
        """Test emission savings calculation"""
        baseline_emissions = 100.0
        optimized_emissions = 70.0
        
        savings = calculator.calculate_savings(baseline_emissions, optimized_emissions)
        
        assert savings["savings_kg"] == 30.0
        assert savings["savings_percentage"] == 30.0
        assert savings["baseline_emissions"] == 100.0
        assert savings["optimized_emissions"] == 70.0
    
    def test_calculate_savings_no_baseline(self, calculator):
        """Test savings calculation with zero baseline"""
        savings = calculator.calculate_savings(0, 50.0)
        
        assert savings["savings_kg"] == 0.0
        assert savings["savings_percentage"] == 0.0
    
    def test_calculate_equivalent_metrics(self, calculator):
        """Test equivalent metrics calculation"""
        emissions_kg = 50.0
        
        metrics = calculator._calculate_equivalent_metrics(emissions_kg)
        
        assert "equivalent_km_driven" in metrics
        assert "equivalent_trees_year" in metrics
        assert "equivalent_gasoline_liters" in metrics
        assert "equivalent_smartphone_charges" in metrics
        
        # Verify calculations
        assert metrics["equivalent_km_driven"] == 50.0 * 10  # 500 km
        assert metrics["equivalent_trees_year"] == 50.0 * 0.02  # 1.0 trees
        assert metrics["equivalent_gasoline_liters"] == 50.0 * 0.43  # 21.5 liters
    
    def test_validate_vehicle_capacity(self, calculator):
        """Test vehicle capacity validation"""
        assignments = {
            "vehicle_1": ["cont_1", "cont_2"]
        }
        
        containers = [
            {"id": "cont_1", "weight": 400, "length": 1.0, "width": 1.0, "height": 1.0},
            {"id": "cont_2", "weight": 400, "length": 1.0, "width": 1.0, "height": 1.0}
        ]
        
        vehicles = [
            {
                "id": "vehicle_1", 
                "max_weight": 1000,
                "length": 3.0, "width": 2.0, "height": 2.0
            }
        ]
        
        violations = calculator.validate_vehicle_capacity(assignments, containers, vehicles)
        
        # Total weight = 800kg, volume = 2m³, vehicle capacity = 1000kg, 12m³
        # Should not have violations
        assert violations == {}
    
    def test_validate_vehicle_capacity_violations(self, calculator):
        """Test vehicle capacity validation with violations"""
        assignments = {
            "overloaded_vehicle": ["heavy_cont"]
        }
        
        containers = [
            {"id": "heavy_cont", "weight": 1200, "length": 2.0, "width": 2.0, "height": 2.0}
        ]
        
        vehicles = [
            {
                "id": "overloaded_vehicle",
                "max_weight": 1000,  # Exceeded by 200kg
                "length": 2.0, "width": 2.0, "height": 2.0  # Volume = 8m³, container = 8m³
            }
        ]
        
        violations = calculator.validate_vehicle_capacity(assignments, containers, vehicles)
        
        assert "overloaded_vehicle" in violations
        assert any("weight" in violation.lower() for violation in violations["overloaded_vehicle"])


class TestStowagePlanExporter:
    """Test cases for Stowage Plan Exporter service"""
    
    @pytest.fixture
    def exporter(self, tmp_path):
        return StowagePlanExporter(export_dir=str(tmp_path))
    
    @pytest.fixture
    def sample_optimization_result(self):
        return {
            "assignments": {
                "vehicle_1": ["cont_1", "cont_2"],
                "vehicle_2": ["cont_3"]
            },
            "total_emissions": 5.7,
            "utilization": 85.5,
            "vehicle_count": 2,
            "total_containers": 3,
            "status": "optimal"
        }
    
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
            },
            {
                "id": "cont_3",
                "name": "Large Pallet",
                "length": 1.5,
                "width": 1.0,
                "height": 0.5,
                "weight": 100,
                "type": "pallet"
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
    
    def test_exporter_initialization(self, exporter, tmp_path):
        """Test stowage plan exporter initialization"""
        assert exporter is not None
        assert exporter.export_dir == tmp_path
        assert tmp_path.exists()
    
    def test_export_json(self, exporter, sample_optimization_result, sample_containers, sample_vehicles):
        """Test JSON export functionality"""
        filepath = exporter.export_json(
            sample_optimization_result, sample_containers, sample_vehicles
        )
        
        assert filepath is not None
        assert os.path.exists(filepath)
        
        # Verify file content
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert "metadata" in data
        assert "summary" in data
        assert "assignments" in data
        assert "containers" in data
        assert "vehicles" in data
        assert "emission_analysis" in data
        
        assert data["summary"]["total_containers"] == 3
        assert data["summary"]["total_vehicles"] == 2
    
    def test_export_csv(self, exporter, sample_optimization_result, sample_containers, sample_vehicles):
        """Test CSV export functionality"""
        filepath = exporter.export_csv(
            sample_optimization_result, sample_containers, sample_vehicles
        )
        
        assert filepath is not None
        assert os.path.exists(filepath)
        
        # Verify file has content
        with open(filepath, 'r') as f:
            content = f.read()
        
        assert "Vehicle_ID" in content
        assert "Container_ID" in content
        assert "cont_1" in content
    
    def test_export_xml(self, exporter, sample_optimization_result, sample_containers, sample_vehicles):
        """Test XML export functionality"""
        filepath = exporter.export_xml(
            sample_optimization_result, sample_containers, sample_vehicles
        )
        
        assert filepath is not None
        assert os.path.exists(filepath)
        
        # Verify file has content
        with open(filepath, 'r') as f:
            content = f.read()
        
        assert "<?xml" in content
        assert "StowagePlan" in content
        assert "vehicle_1" in content
    
    def test_export_comprehensive_report(self, exporter, sample_optimization_result, sample_containers, sample_vehicles):
        """Test comprehensive report export"""
        manifest_path = exporter.export_comprehensive_report(
            sample_optimization_result, sample_containers, sample_vehicles
        )
        
        assert manifest_path is not None
        assert os.path.exists(manifest_path)
        
        # Verify manifest file
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        assert "export_date" in manifest
        assert "files" in manifest
        assert "json" in manifest["files"]
        assert "csv" in manifest["files"]
        assert "xml" in manifest["files"]
        
        # Verify all export files exist
        for filepath in manifest["files"].values():
            assert os.path.exists(filepath)
    
    def test_calculate_emission_analysis(self, exporter, sample_optimization_result, sample_containers, sample_vehicles):
        """Test emission analysis calculation"""
        analysis = exporter._calculate_emission_analysis(
            sample_optimization_result, sample_containers, sample_vehicles
        )
        
        assert "total_emissions_kg" in analysis
        assert "emissions_by_vehicle" in analysis
        assert "weight_distribution" in analysis
        assert "efficiency_metrics" in analysis
        
        assert "vehicle_1" in analysis["emissions_by_vehicle"]
        assert "vehicle_2" in analysis["emissions_by_vehicle"]
        
        vehicle_1_data = analysis["emissions_by_vehicle"]["vehicle_1"]
        assert "emissions_kg" in vehicle_1_data
        assert "total_weight" in vehicle_1_data
        assert "vehicle_type" in vehicle_1_data
        assert "utilization_percentage" in vehicle_1_data
    
    def test_list_exported_plans(self, exporter, sample_optimization_result, sample_containers, sample_vehicles):
        """Test listing exported plans"""
        # First export some plans
        exporter.export_json(sample_optimization_result, sample_containers, sample_vehicles)
        exporter.export_csv(sample_optimization_result, sample_containers, sample_vehicles)
        
        plans = exporter.list_exported_plans()
        
        assert len(plans) >= 1  # At least one JSON plan
        for plan in plans:
            assert "filename" in plan
            assert "filepath" in plan
            assert "size_kb" in plan
            assert "modified" in plan
    
    def test_export_with_custom_filename(self, exporter, sample_optimization_result, sample_containers, sample_vehicles):
        """Test export with custom filename"""
        custom_filename = "custom_export.json"
        filepath = exporter.export_json(
            sample_optimization_result, sample_containers, sample_vehicles, custom_filename
        )
        
        assert filepath.endswith(custom_filename)
        assert os.path.exists(filepath)


class TestIntegration:
    """Integration tests for multiple services"""
    
    def test_full_optimization_workflow(self, tmp_path):
        """Test complete optimization workflow"""
        # Initialize services
        solver = ConstraintSolver()
        calculator = EmissionCalculator()
        exporter = StowagePlanExporter(export_dir=str(tmp_path))
        
        # Sample data
        containers = [
            Container(
                id="cont_1", name="Test Container", length=1.0, width=1.0, height=1.0,
                weight=200, type="box"
            )
        ]
        
        vehicles = [
            Vehicle(
                id="vehicle_1", type="small_truck", max_weight=1000,
                length=3.0, width=2.0, height=2.0, emission_factor=0.00012
            )
        ]
        
        # Run optimization
        optimization_result = solver.solve_optimization(containers, vehicles, 100.0)
        
        assert optimization_result is not None
        
        # Calculate emissions
        containers_dict = [{"id": c.id, "weight": c.weight} for c in containers]
        vehicles_dict = [{"id": v.id, "emission_factor": v.emission_factor} for v in vehicles]
        
        emission_result = calculator.calculate_emissions(
            optimization_result.assignments,
            containers_dict,
            vehicles_dict,
            100.0
        )
        
        assert emission_result is not None
        
        # Export results
        export_data = {
            "assignments": optimization_result.assignments,
            "total_emissions": optimization_result.total_emissions,
            "utilization": optimization_result.utilization,
            "vehicle_count": optimization_result.vehicle_count,
            "total_containers": optimization_result.total_containers,
            "status": optimization_result.status
        }
        
        containers_export = [
            {
                "id": c.id, "name": c.name, "length": c.length, "width": c.width,
                "height": c.height, "weight": c.weight, "type": c.type
            }
            for c in containers
        ]
        
        vehicles_export = [
            {
                "id": v.id, "type": v.type, "max_weight": v.max_weight,
                "length": v.length, "width": v.width, "height": v.height,
                "emission_factor": v.emission_factor
            }
            for v in vehicles
        ]
        
        export_path = exporter.export_json(export_data, containers_export, vehicles_export)
        
        assert os.path.exists(export_path)
        
        # Verify the exported file contains expected data
        with open(export_path, 'r') as f:
            exported_data = json.load(f)
        
        assert exported_data["summary"]["total_containers"] == 1
        assert exported_data["summary"]["total_vehicles"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])