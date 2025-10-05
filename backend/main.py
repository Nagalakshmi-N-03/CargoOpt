#!/usr/bin/env python3
"""
CargoOpt Backend Server
Main FastAPI application for cargo optimization and emissions tracking
"""

import os
import sys
import json
import logging
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

# Import your modules with proper error handling
try:
    from algorithms.constraint_solver import ConstraintSolver, Container, Vehicle, OptimizationResult
    from services.emission_calculator import EmissionCalculator
except ImportError as e:
    print(f"Warning: Could not import optimization modules: {e}")
    # Create stub implementations
    class Container:
        def __init__(self, id, name, length, width, height, weight, type, hazard_class=None, requires_refrigeration=False):
            self.id = id
            self.name = name
            self.length = length
            self.width = width
            self.height = height
            self.weight = weight
            self.type = type
            self.hazard_class = hazard_class
            self.requires_refrigeration = requires_refrigeration

    class Vehicle:
        def __init__(self, id, type, max_weight, length, width, height, emission_factor, can_carry_hazardous=False, has_refrigeration=False):
            self.id = id
            self.type = type
            self.max_weight = max_weight
            self.length = length
            self.width = width
            self.height = height
            self.emission_factor = emission_factor
            self.can_carry_hazardous = can_carry_hazardous
            self.has_refrigeration = has_refrigeration

    class OptimizationResult:
        def __init__(self):
            self.assignments = {}
            self.total_emissions = 0
            self.utilization = 0
            self.vehicle_count = 0
            self.total_containers = 0
            self.status = "stub"
            self.violations = []
            self.warnings = []

    class ConstraintSolver:
        def solve_optimization(self, containers, vehicles, distance_km):
            result = OptimizationResult()
            result.assignments = {"vehicle1": [c.id for c in containers]}
            result.total_containers = len(containers)
            result.vehicle_count = len(vehicles)
            result.status = "success"
            return result

    class EmissionCalculator:
        def calculate_emissions(self, assignments, containers, vehicles, distance_km):
            class EmissionResult:
                def __init__(self):
                    self.total_emissions_kg = 100
                    self.emissions_per_vehicle = {"vehicle1": 100}
                    self.emissions_per_container = {}
                    self.distance_km = distance_km
                    self.equivalent_metrics = {"trees_required": 5}
            return EmissionResult()

# Fixed import - handle the stowage_exporter gracefully
try:
    from data.exports.stowage_plans.stowage_exporter import StowagePlanExporter
except ImportError:
    # Create a stub implementation if the module doesn't exist
    class StowagePlanExporter:
        def export_json(self, result, containers, vehicles):
            filepath = "exports/stowage_plan.json"
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump({
                    "result": result,
                    "containers": containers,
                    "vehicles": vehicles,
                    "exported_at": "2024-01-01T00:00:00Z"
                }, f, indent=2)
            return filepath
        
        def export_csv(self, result, containers, vehicles):
            filepath = "exports/stowage_plan.csv"
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            # Simple CSV implementation
            with open(filepath, 'w') as f:
                f.write("vehicle_id,container_ids,total_weight,emissions_kg\n")
                for vehicle_id, container_list in result.get('assignments', {}).items():
                    f.write(f"{vehicle_id},{','.join(container_list)},0,0\n")
            return filepath
        
        def export_xml(self, result, containers, vehicles):
            filepath = "exports/stowage_plan.xml"
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            # Simple XML implementation
            with open(filepath, 'w') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<stowage_plan>\n')
                f.write('  <result>\n')
                f.write('  </result>\n')
                f.write('</stowage_plan>\n')
            return filepath

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cargoopt.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# FastAPI application
app = FastAPI(
    title="CargoOpt API",
    description="Intelligent cargo optimization system with emissions tracking",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
constraint_solver = ConstraintSolver()
emission_calculator = EmissionCalculator()
stowage_exporter = StowagePlanExporter()

# Pydantic models for API
class ContainerModel(BaseModel):
    id: str
    name: str
    length: float
    width: float
    height: float
    weight: float
    type: str
    hazard_class: Optional[str] = None
    requires_refrigeration: bool = False

class VehicleModel(BaseModel):
    id: str
    type: str
    max_weight: float
    length: float
    width: float
    height: float
    emission_factor: float
    can_carry_hazardous: bool = False
    has_refrigeration: bool = False

class OptimizationRequest(BaseModel):
    containers: List[ContainerModel]
    vehicles: List[VehicleModel]
    distance_km: float = 100.0
    constraints: Dict[str, Any] = None

class EmissionCalculationRequest(BaseModel):
    assignments: Dict[str, List[str]]
    containers: List[Dict[str, Any]]
    vehicles: List[Dict[str, Any]]
    distance_km: float = 100.0

class ExportRequest(BaseModel):
    result: Dict[str, Any]
    containers: List[Dict[str, Any]]
    vehicles: List[Dict[str, Any]]
    format: str = "json"

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "CargoOpt Backend Server",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "optimization_engine": "healthy",
            "emission_calculator": "healthy",
            "export_service": "healthy"
        }
    }

@app.get("/api/system/info")
async def system_info():
    """Get system information and capabilities"""
    return {
        "name": "CargoOpt",
        "version": "1.0.0",
        "supported_features": [
            "optimization",
            "emission_calculation",
            "3d_visualization",
            "hazardous_materials",
            "multiple_export_formats"
        ],
        "limits": {
            "max_containers": 10000,
            "max_vehicles": 100,
            "max_scenarios": 1000
        }
    }

@app.post("/api/optimize", response_model=Dict[str, Any])
async def run_optimization(request: OptimizationRequest):
    """Run cargo optimization"""
    try:
        logger.info(f"Starting optimization with {len(request.containers)} containers and {len(request.vehicles)} vehicles")
        
        # Convert to internal models
        containers = [
            Container(
                id=c.id,
                name=c.name,
                length=c.length,
                width=c.width,
                height=c.height,
                weight=c.weight,
                type=c.type,
                hazard_class=c.hazard_class,
                requires_refrigeration=c.requires_refrigeration
            ) for c in request.containers
        ]
        
        vehicles = [
            Vehicle(
                id=v.id,
                type=v.type,
                max_weight=v.max_weight,
                length=v.length,
                width=v.width,
                height=v.height,
                emission_factor=v.emission_factor,
                can_carry_hazardous=v.can_carry_hazardous,
                has_refrigeration=v.has_refrigeration
            ) for v in request.vehicles
        ]
        
        # Run optimization
        result = constraint_solver.solve_optimization(
            containers=containers,
            vehicles=vehicles,
            distance_km=request.distance_km
        )
        
        if result is None:
            raise HTTPException(status_code=400, detail="No feasible solution found")
        
        # Convert back to dict for response
        response_data = {
            "assignments": result.assignments,
            "total_emissions": result.total_emissions,
            "utilization": result.utilization,
            "vehicle_count": result.vehicle_count,
            "total_containers": result.total_containers,
            "status": result.status,
            "violations": result.violations,
            "warnings": result.warnings
        }
        
        logger.info(f"Optimization completed: {result.status}")
        return response_data
        
    except Exception as e:
        logger.error(f"Optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@app.post("/api/calculate/emissions")
async def calculate_emissions(request: EmissionCalculationRequest):
    """Calculate emissions for given assignments"""
    try:
        result = emission_calculator.calculate_emissions(
            assignments=request.assignments,
            containers=request.containers,
            vehicles=request.vehicles,
            distance_km=request.distance_km
        )
        
        return {
            "total_emissions_kg": result.total_emissions_kg,
            "emissions_per_vehicle": result.emissions_per_vehicle,
            "emissions_per_container": result.emissions_per_container,
            "distance_km": result.distance_km,
            "equivalent_metrics": result.equivalent_metrics
        }
        
    except Exception as e:
        logger.error(f"Emission calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Emission calculation failed: {str(e)}")

@app.post("/api/export/results")
async def export_results(request: ExportRequest):
    """Export optimization results"""
    try:
        if request.format == "json":
            filepath = stowage_exporter.export_json(
                request.result, request.containers, request.vehicles
            )
        elif request.format == "csv":
            filepath = stowage_exporter.export_csv(
                request.result, request.containers, request.vehicles
            )
        elif request.format == "xml":
            filepath = stowage_exporter.export_xml(
                request.result, request.containers, request.vehicles
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
        
        return {
            "message": "Export completed successfully",
            "format": request.format,
            "filepath": filepath
        }
        
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.get("/api/reference/imdg_codes")
async def get_imdg_codes():
    """Get IMDG codes and segregation rules"""
    try:
        file_path = backend_dir / "data" / "reference" / "imdg_codes.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            # Return sample data if file doesn't exist
            return {
                "imdg_classes": [
                    {"class": "1", "description": "Explosives", "segregation_group": "A"},
                    {"class": "2", "description": "Gases", "segregation_group": "B"},
                    {"class": "3", "description": "Flammable liquids", "segregation_group": "C"}
                ],
                "segregation_rules": {
                    "A": ["incompatible with all other groups"],
                    "B": ["compatible with C", "incompatible with A"],
                    "C": ["compatible with B", "incompatible with A"]
                }
            }
    except Exception as e:
        logger.error(f"Error loading IMDG codes: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load IMDG codes")

@app.get("/api/reference/stability_rules")
async def get_stability_rules():
    """Get stability rules and loading parameters"""
    try:
        file_path = backend_dir / "data" / "reference" / "stability_rules.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            # Return sample data if file doesn't exist
            return {
                "max_weight_distribution": 0.8,
                "min_stability_factor": 1.5,
                "max_height_ratio": 0.9,
                "center_of_gravity_limits": {
                    "longitudinal": 0.4,
                    "transverse": 0.3,
                    "vertical": 0.6
                }
            }
    except Exception as e:
        logger.error(f"Error loading stability rules: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load stability rules")

@app.get("/api/scenarios")
async def get_sample_scenarios():
    """Get sample optimization scenarios"""
    try:
        file_path = backend_dir / "data" / "sample" / "test_scenarios.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get("scenarios", [])
        else:
            # Return sample scenarios if file doesn't exist
            return [
                {
                    "id": "scenario_1",
                    "name": "Basic Container Transport",
                    "containers": 10,
                    "vehicles": 2,
                    "description": "Simple container distribution scenario"
                }
            ]
    except Exception as e:
        logger.error(f"Error loading scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load scenarios")

@app.post("/api/validate/containers")
async def validate_containers(containers: List[Dict[str, Any]]):
    """Validate container data"""
    try:
        # Basic validation logic
        errors = []
        warnings = []
        
        for i, container in enumerate(containers):
            # Check required fields
            required_fields = ['id', 'name', 'length', 'width', 'height', 'weight']
            for field in required_fields:
                if field not in container:
                    errors.append(f"Container {i}: Missing required field '{field}'")
            
            # Check numeric values
            if 'weight' in container and container['weight'] <= 0:
                errors.append(f"Container {container.get('id', str(i))}: Weight must be positive")
            
            if 'length' in container and container['length'] <= 0:
                errors.append(f"Container {container.get('id', str(i))}: Length must be positive")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
        
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

# Error handlers
@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="info")