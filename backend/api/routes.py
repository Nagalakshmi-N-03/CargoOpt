import logging
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import time
import uuid
import os

from backend.config.database import get_db
from backend.services.optimization import OptimizationService
from backend.services.data_processor import DataProcessor
from backend.utils.file_utils import FileUtils

from .models import (
    ContainerData,
    CargoItemData,
    OptimizationRequest,
    GeneticOptimizationRequest,
    MultiContainerRequest,
    BatchOptimizationRequest,
    PlacementValidationRequest,
    AlgorithmComparisonRequest,
    OptimizationResponse,
    BatchOptimizationResponse,
    ValidationResponse,
    ComparisonResponse,
    HealthResponse,
    AlgorithmInfo,
    ContainerTypeInfo,
    AlgorithmType,
    OptimizationStrategy
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["optimization"])

# Global cache for batch results
batch_results = {}

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="CargoOpt Backend",
        version="2.0.0",
        timestamp=time.time(),
        features=["optimization", "validation", "comparison", "batch", "export"]
    )

@router.get("/algorithms", response_model=List[AlgorithmInfo])
async def list_algorithms():
    """List all available optimization algorithms"""
    return [
        AlgorithmInfo(
            name="Basic Packing Algorithm",
            id="packing",
            endpoint="/api/v1/optimize/packing",
            description="First-fit decreasing algorithm for single container packing",
            best_for="Simple scenarios, fast results",
            parameters={
                "max_execution_time": 30,
                "strategy": ["balanced", "space_first", "stability_first"]
            }
        ),
        AlgorithmInfo(
            name="Genetic Algorithm",
            id="genetic",
            endpoint="/api/v1/optimize/genetic",
            description="Genetic algorithm for optimized container packing",
            best_for="Complex scenarios, maximum optimization",
            parameters={
                "generations": 100,
                "population_size": 50,
                "mutation_rate": 0.1,
                "crossover_rate": 0.8
            }
        ),
        AlgorithmInfo(
            name="Stowage Optimizer",
            id="stowage",
            endpoint="/api/v1/optimize/stowage",
            description="Multi-container stowage optimization",
            best_for="Multiple containers, distribution planning",
            parameters={
                "strategy": ["balanced", "space_first", "minimize_containers"],
                "minimize_containers": True
            }
        ),
        AlgorithmInfo(
            name="Auto Select",
            id="auto",
            endpoint="/api/v1/optimize/auto",
            description="Automatically selects the best algorithm",
            best_for="General use, balanced performance",
            parameters={}
        )
    ]

@router.post("/optimize/auto", response_model=OptimizationResponse)
async def optimize_auto(
    request: OptimizationRequest,
    db: Session = Depends(get_db)
):
    """
    Optimize packing with automatic algorithm selection
    """
    try:
        logger.info(f"Auto optimization request for {len(request.items)} items")
        
        optimization_service = OptimizationService(db)
        
        result = await optimization_service.optimize_single_container(
            container_data=request.container.dict(),
            items_data=[item.dict() for item in request.items],
            algorithm=request.algorithm.value,
            strategy=request.strategy.value
        )
        
        return OptimizationResponse(
            success=result['success'],
            algorithm=result.get('algorithm', 'auto'),
            result=result.get('result', {}),
            execution_time=result.get('result', {}).get('execution_time', 0),
            message=result.get('message', 'Optimization completed'),
            warnings=result.get('warnings', [])
        )
        
    except Exception as e:
        logger.error(f"Auto optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize/packing", response_model=OptimizationResponse)
async def optimize_packing(
    request: OptimizationRequest,
    db: Session = Depends(get_db)
):
    """
    Optimize packing using basic first-fit decreasing algorithm
    """
    try:
        logger.info(f"Packing optimization request for {len(request.items)} items")
        
        optimization_service = OptimizationService(db)
        
        result = await optimization_service.optimize_single_container(
            container_data=request.container.dict(),
            items_data=[item.dict() for item in request.items],
            algorithm="packing",
            strategy=request.strategy.value
        )
        
        return OptimizationResponse(
            success=result['success'],
            algorithm="packing",
            result=result.get('result', {}),
            execution_time=result.get('result', {}).get('execution_time', 0),
            message=result.get('message', 'Packing optimization completed'),
            warnings=result.get('warnings', [])
        )
        
    except Exception as e:
        logger.error(f"Packing optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize/genetic", response_model=OptimizationResponse)
async def optimize_genetic(
    request: GeneticOptimizationRequest,
    db: Session = Depends(get_db)
):
    """
    Optimize packing using genetic algorithm
    """
    try:
        logger.info(f"Genetic optimization request for {len(request.items)} items")
        
        optimization_service = OptimizationService(db)
        
        result = await optimization_service.optimize_single_container(
            container_data=request.container.dict(),
            items_data=[item.dict() for item in request.items],
            algorithm="genetic",
            generations=request.generations,
            population_size=request.population_size,
            mutation_rate=request.mutation_rate
        )
        
        return OptimizationResponse(
            success=result['success'],
            algorithm="genetic",
            result=result.get('result', {}),
            execution_time=result.get('result', {}).get('execution_time', 0),
            message=result.get('message', 'Genetic optimization completed'),
            warnings=result.get('warnings', [])
        )
        
    except Exception as e:
        logger.error(f"Genetic algorithm error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize/stowage", response_model=OptimizationResponse)
async def optimize_stowage(
    request: MultiContainerRequest,
    db: Session = Depends(get_db)
):
    """
    Optimize stowage across multiple containers
    """
    try:
        logger.info(f"Stowage optimization request for {len(request.containers)} containers, {len(request.items)} items")
        
        optimization_service = OptimizationService(db)
        
        result = await optimization_service.optimize_multi_container(
            containers_data=[container.dict() for container in request.containers],
            items_data=[item.dict() for item in request.items],
            strategy=request.strategy.value
        )
        
        return OptimizationResponse(
            success=result['success'],
            algorithm="stowage",
            result=result.get('result', {}),
            execution_time=result.get('result', {}).get('execution_time', 0),
            message=result.get('message', 'Stowage optimization completed'),
            warnings=result.get('warnings', [])
        )
        
    except Exception as e:
        logger.error(f"Stowage optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize/compare", response_model=ComparisonResponse)
async def compare_algorithms(
    request: AlgorithmComparisonRequest,
    db: Session = Depends(get_db)
):
    """
    Compare multiple algorithms on the same problem
    """
    try:
        logger.info(f"Algorithm comparison request for {len(request.algorithms)} algorithms")
        
        optimization_service = OptimizationService(db)
        
        result = await optimization_service.compare_algorithms(
            container_data=request.container.dict(),
            items_data=[item.dict() for item in request.items],
            algorithms=[algo.value for algo in request.algorithms]
        )
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error', 'Comparison failed'))
        
        comparison = result.get('comparison', {})
        best_algo = comparison.get('best_by_efficiency', 'unknown')
        
        return ComparisonResponse(
            success=True,
            comparison=comparison,
            recommendations=comparison.get('recommendation', '').split('. '),
            best_algorithm=best_algo,
            results=result.get('results', {})
        )
        
    except Exception as e:
        logger.error(f"Algorithm comparison error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize/batch", response_model=BatchOptimizationResponse)
async def batch_optimize(
    request: BatchOptimizationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Process multiple optimization tasks in batch
    """
    try:
        optimization_service = OptimizationService(db)
        batch_id = request.batch_id or str(uuid.uuid4())
        
        # Prepare tasks
        optimization_tasks = []
        for i, task in enumerate(request.tasks):
            optimization_tasks.append({
                'id': f"task_{i}",
                'container': task.container.dict(),
                'items': [item.dict() for item in task.items],
                'algorithm': task.algorithm.value,
                'strategy': task.strategy.value
            })
        
        # Store initial batch result
        batch_results[batch_id] = {
            'status': 'processing',
            'total_tasks': len(optimization_tasks),
            'completed_tasks': 0,
            'results': [],
            'started_at': time.time(),
            'parallel': request.parallel_processing
        }
        
        # Run in background
        background_tasks.add_task(
            process_batch_optimization,
            batch_id,
            optimization_tasks,
            optimization_service,
            request.parallel_processing
        )
        
        return BatchOptimizationResponse(
            success=True,
            batch_id=batch_id,
            total_tasks=len(optimization_tasks),
            completed_tasks=0,
            failed_tasks=0,
            results=[],
            summary={
                'status': 'processing',
                'progress': 0,
                'estimated_time_remaining': None
            }
        )
        
    except Exception as e:
        logger.error(f"Batch optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_batch_optimization(
    batch_id: str, 
    tasks: List[Dict], 
    optimization_service: OptimizationService,
    parallel: bool = False
):
    """Background task to process batch optimization"""
    try:
        results = []
        
        for task in tasks:
            try:
                result = await optimization_service.optimize_single_container(
                    container_data=task['container'],
                    items_data=task['items'],
                    algorithm=task.get('algorithm', 'auto'),
                    strategy=task.get('strategy', 'balanced')
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Batch task {task['id']} failed: {str(e)}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'task_id': task['id']
                })
            
            # Update batch progress
            batch_results[batch_id]['completed_tasks'] = len(results)
            batch_results[batch_id]['results'] = results
            
            # Small delay to prevent overwhelming the system
            if not parallel:
                import asyncio
                await asyncio.sleep(0.1)
        
        # Finalize batch result
        batch_results[batch_id]['status'] = 'completed'
        batch_results[batch_id]['completed_at'] = time.time()
        
    except Exception as e:
        logger.error(f"Batch processing error: {str(e)}")
        batch_results[batch_id]['status'] = 'failed'
        batch_results[batch_id]['error'] = str(e)

@router.get("/optimize/batch/{batch_id}/status")
async def get_batch_status(batch_id: str):
    """Get batch processing status"""
    if batch_id not in batch_results:
        raise HTTPException(status_code=404, detail="Batch ID not found")
    
    batch_data = batch_results[batch_id]
    
    successful_tasks = [r for r in batch_data['results'] if r.get('success', False)]
    failed_tasks = [r for r in batch_data['results'] if not r.get('success', False)]
    
    response = {
        "batch_id": batch_id,
        "status": batch_data['status'],
        "progress": {
            "total_tasks": batch_data['total_tasks'],
            "completed_tasks": batch_data['completed_tasks'],
            "percentage": round((batch_data['completed_tasks'] / batch_data['total_tasks']) * 100, 1)
        },
        "summary": {
            "successful_tasks": len(successful_tasks),
            "failed_tasks": len(failed_tasks),
            "success_rate": len(successful_tasks) / batch_data['total_tasks'] if batch_data['total_tasks'] > 0 else 0
        }
    }
    
    if batch_data['status'] == 'completed':
        response['results'] = batch_data['results']
    
    elif batch_data['status'] == 'failed':
        response['error'] = batch_data.get('error', 'Unknown error')
    
    return response

@router.post("/validate/data", response_model=ValidationResponse)
async def validate_data(
    container: ContainerData,
    items: List[CargoItemData],
    db: Session = Depends(get_db)
):
    """
    Validate container and items data before optimization
    """
    try:
        data_processor = DataProcessor(db)
        
        container_validation = data_processor.validate_container_data(container.dict())
        items_validation = data_processor.validate_cargo_items([item.dict() for item in items])
        
        is_valid = container_validation['is_valid'] and items_validation['is_valid']
        
        issues = []
        if not container_validation['is_valid']:
            issues.append(f"Container: {container_validation.get('error', 'Invalid data')}")
        if not items_validation['is_valid']:
            issues.append(f"Items: {items_validation.get('error', 'Invalid data')}")
        
        return ValidationResponse(
            success=True,
            valid=is_valid,
            metrics={
                'container': container_validation,
                'items': items_validation
            },
            issues=issues,
            message="Data validation completed"
        )
        
    except Exception as e:
        logger.error(f"Data validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate/placement", response_model=ValidationResponse)
async def validate_placement(
    request: PlacementValidationRequest,
    db: Session = Depends(get_db)
):
    """
    Validate if placements are valid (no overlaps, within container bounds)
    """
    try:
        optimization_service = OptimizationService(db)
        
        result = await optimization_service.validate_optimization(
            container_data=request.container.dict(),
            items_data=[item.dict() for item in request.items],
            placements=[placement.dict() for placement in request.placements]
        )
        
        return ValidationResponse(
            success=result['success'],
            valid=result.get('valid', False),
            metrics=result.get('metrics'),
            issues=result.get('message', '').split('. ') if not result.get('valid', False) else [],
            message=result.get('message', 'Placement validation completed')
        )
        
    except Exception as e:
        logger.error(f"Placement validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/containers/types", response_model=List[ContainerTypeInfo])
async def get_container_types():
    """Get standard container types and dimensions"""
    standard_containers = [
        ContainerTypeInfo(
            name="Standard 20ft Container",
            length=605.0,
            width=244.0,
            height=259.0,
            max_weight=28200.0,
            volume=38.3,
            description="Standard 20-foot dry container"
        ),
        ContainerTypeInfo(
            name="Standard 40ft Container",
            length=1219.0,
            width=244.0,
            height=259.0,
            max_weight=26700.0,
            volume=76.3,
            description="Standard 40-foot dry container"
        ),
        ContainerTypeInfo(
            name="High Cube 40ft Container",
            length=1219.0,
            width=244.0,
            height=289.0,
            max_weight=26700.0,
            volume=85.7,
            description="High cube 40-foot container with extra height"
        ),
        ContainerTypeInfo(
            name="Refrigerated 20ft Container",
            length=543.0,
            width=229.0,
            height=226.0,
            max_weight=30480.0,
            volume=28.0,
            description="20-foot refrigerated container"
        )
    ]
    
    return standard_containers

@router.post("/export/result")
async def export_optimization_result(
    result: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Export optimization result to Excel file
    """
    try:
        data_processor = DataProcessor(db)
        export_id = str(uuid.uuid4())
        filename = f"exports/optimization_result_{export_id}.xlsx"
        
        # Run export in background
        background_tasks.add_task(
            data_processor.export_to_csv,
            result,
            filename
        )
        
        return {
            "success": True,
            "export_id": export_id,
            "message": "Export started in background",
            "download_endpoint": f"/api/v1/export/download/{export_id}"
        }
        
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/download/{export_id}")
async def download_export(export_id: str):
    """
    Download exported optimization result
    """
    filename = f"exports/optimization_result_{export_id}.xlsx"
    
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Export file not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(
        filename,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename=f"cargo_optimization_{export_id}.xlsx"
    )

@router.get("/optimize/history")
async def get_optimization_history(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    algorithm: Optional[AlgorithmType] = None,
    min_utilization: Optional[float] = Query(None, ge=0, le=1),
    max_utilization: Optional[float] = Query(None, ge=0, le=1)
):
    """Get optimization history with filtering"""
    try:
        optimization_service = OptimizationService(db)
        
        result = optimization_service.get_optimization_history(
            limit=limit,
            algorithm=algorithm.value if algorithm else None
        )
        
        # Apply additional filters
        if min_utilization is not None or max_utilization is not None:
            filtered_history = []
            for item in result['history']:
                utilization = item['utilization_rate']
                if min_utilization is not None and utilization < min_utilization:
                    continue
                if max_utilization is not None and utilization > max_utilization:
                    continue
                filtered_history.append(item)
            
            result['history'] = filtered_history
            result['count'] = len(filtered_history)
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching optimization history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))