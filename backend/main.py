#!/usr/bin/env python3
"""
CargoOpt Backend Server
Main FastAPI application for cargo optimization and emissions tracking
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import uvicorn

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

from algorithms.constraint_solver import ConstraintSolver, Container, Vehicle, OptimizationResult
from services.emission_calculator import EmissionCalculator
from data.exports.stowage_plans.stowage_exporter import StowagePlanExporter

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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
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
        "timestamp": "2024-01-01T00:00:00Z",  # You might want to use actual timestamp
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
            import json
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            return {"error": "IMDG codes file not found"}
    except Exception as e:
        logger.error(f"Error loading IMDG codes: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load IMDG codes")

@app.get("/api/reference/stability_rules")
async def get_stability_rules():
    """Get stability rules and loading parameters"""
    try:
        file_path = backend_dir / "data" / "reference" / "stability_rules.json"
        if file_path.exists():
            import json
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            return {"error": "Stability rules file not found"}
    except Exception as e:
        logger.error(f"Error loading stability rules: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load stability rules")

@app.get("/api/scenarios")
async def get_sample_scenarios():
    """Get sample optimization scenarios"""
    try:
        file_path = backend_dir / "data" / "sample" / "test_scenarios.json"
        if file_path.exists():
            import json
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get("scenarios", [])
        else:
            return []
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
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )