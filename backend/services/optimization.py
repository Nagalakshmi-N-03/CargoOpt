"""
Optimization Service
Orchestrates optimization workflows and manages optimization processes.
"""

import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from backend.config.settings import Config
from backend.config.database import db_manager
from backend.algorithms.genetic_algorithm import GeneticAlgorithm
from backend.algorithms.constraint_solver import ConstraintSolver
from backend.algorithms.stowage import StowagePlanner
from backend.services.data_processor import DataProcessor
from backend.services.validation import ValidationService
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class OptimizationStatus(Enum):
    """Optimization status enumeration."""
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class OptimizationAlgorithm(Enum):
    """Available optimization algorithms."""
    GENETIC = 'genetic'
    CONSTRAINT = 'constraint'
    HYBRID = 'hybrid'
    AUTO = 'auto'


class OptimizationOrchestrator:
    """
    Orchestrates multiple optimization runs and manages parallel execution.
    """
    
    def __init__(self, config: Config = None):
        """
        Initialize orchestrator.
        
        Args:
            config: Configuration object
        """
        self.config = config or Config()
        self.active_optimizations = {}
        self.lock = threading.Lock()
        
    def run_parallel_optimizations(
        self,
        optimization_configs: List[Dict]
    ) -> List[Dict]:
        """
        Run multiple optimizations in parallel.
        
        Args:
            optimization_configs: List of optimization configurations
            
        Returns:
            List of results
        """
        logger.info(f"Starting {len(optimization_configs)} parallel optimizations")
        
        results = []
        max_workers = min(self.config.NUM_WORKERS, len(optimization_configs))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._run_single_optimization, config): config
                for config in optimization_configs
            }
            
            for future in as_completed(futures):
                config = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Optimization failed: {e}")
                    results.append({
                        'status': 'failed',
                        'error': str(e),
                        'config': config
                    })
        
        logger.info(f"Completed {len(results)} parallel optimizations")
        return results
    
    def _run_single_optimization(self, config: Dict) -> Dict:
        """Run a single optimization."""
        service = OptimizationService(self.config)
        return service.optimize(
            container=config['container'],
            items=config['items'],
            algorithm=config.get('algorithm', 'genetic'),
            parameters=config.get('parameters', {})
        )


class OptimizationService:
    """
    Main optimization service coordinating the optimization workflow.
    """
    
    def __init__(self, config: Config = None):
        """
        Initialize optimization service.
        
        Args:
            config: Configuration object
        """
        self.config = config or Config()
        self.data_processor = DataProcessor(config)
        self.validator = ValidationService(config)
        self.active_jobs = {}
        self.lock = threading.Lock()
        
        logger.info("OptimizationService initialized")
    
    def optimize(
        self,
        container: Dict,
        items: List[Dict],
        algorithm: str = 'genetic',
        parameters: Optional[Dict] = None,
        async_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Main optimization entry point.
        
        Args:
            container: Container specifications
            items: List of items to pack
            algorithm: Algorithm to use ('genetic', 'constraint', 'hybrid', 'auto')
            parameters: Optional algorithm parameters override
            async_mode: Run optimization asynchronously
            
        Returns:
            Optimization results dictionary
        """
        # Generate unique optimization ID
        optimization_id = str(uuid.uuid4())
        
        logger.info(f"Starting optimization {optimization_id} with algorithm: {algorithm}")
        
        # Validate input
        is_valid, validation_errors = self.validator.validate_optimization_request({
            'container': container,
            'items': items
        })
        
        if not is_valid:
            logger.error(f"Validation failed: {validation_errors}")
            return {
                'optimization_id': optimization_id,
                'status': OptimizationStatus.FAILED.value,
                'error': 'Validation failed',
                'validation_errors': validation_errors
            }
        
        # Create optimization record
        self._create_optimization_record(optimization_id, container, items, algorithm)
        
        if async_mode:
            # Run asynchronously
            thread = threading.Thread(
                target=self._run_optimization_async,
                args=(optimization_id, container, items, algorithm, parameters)
            )
            thread.start()
            
            return {
                'optimization_id': optimization_id,
                'status': OptimizationStatus.PENDING.value,
                'message': 'Optimization started asynchronously'
            }
        else:
            # Run synchronously
            return self._run_optimization_sync(
                optimization_id, container, items, algorithm, parameters
            )
    
    def _run_optimization_sync(
        self,
        optimization_id: str,
        container: Dict,
        items: List[Dict],
        algorithm: str,
        parameters: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Run optimization synchronously.
        
        Args:
            optimization_id: Unique optimization ID
            container: Container data
            items: Items data
            algorithm: Algorithm name
            parameters: Algorithm parameters
            
        Returns:
            Optimization results
        """
        try:
            # Update status to running
            self._update_optimization_status(optimization_id, OptimizationStatus.RUNNING)
            
            # Process input data
            processed_container, processed_items = self.data_processor.process_optimization_input(
                container, items
            )
            
            # Select and run algorithm
            result = self._execute_algorithm(
                algorithm,
                processed_container,
                processed_items,
                parameters
            )
            
            # Enhance result with additional data
            enhanced_result = self._enhance_result(
                result,
                optimization_id,
                processed_container,
                processed_items
            )
            
            # Save results
            self._save_optimization_results(optimization_id, enhanced_result)
            
            # Update status to completed
            self._update_optimization_status(optimization_id, OptimizationStatus.COMPLETED)
            
            logger.info(f"Optimization {optimization_id} completed successfully")
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Optimization {optimization_id} failed: {e}", exc_info=True)
            
            # Update status to failed
            self._update_optimization_status(
                optimization_id,
                OptimizationStatus.FAILED,
                error_message=str(e)
            )
            
            return {
                'optimization_id': optimization_id,
                'status': OptimizationStatus.FAILED.value,
                'error': str(e)
            }
    
    def _run_optimization_async(
        self,
        optimization_id: str,
        container: Dict,
        items: List[Dict],
        algorithm: str,
        parameters: Optional[Dict]
    ):
        """Run optimization asynchronously (same as sync but in thread)."""
        self._run_optimization_sync(
            optimization_id, container, items, algorithm, parameters
        )
    
    def _execute_algorithm(
        self,
        algorithm: str,
        container: Dict,
        items: List[Dict],
        parameters: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Execute the selected optimization algorithm.
        
        Args:
            algorithm: Algorithm name
            container: Processed container data
            items: Processed items data
            parameters: Algorithm parameters
            
        Returns:
            Algorithm results
        """
        algo_enum = OptimizationAlgorithm(algorithm.lower())
        
        if algo_enum == OptimizationAlgorithm.AUTO:
            # Auto-select algorithm based on problem size
            algo_enum = self._auto_select_algorithm(container, items)
            logger.info(f"Auto-selected algorithm: {algo_enum.value}")
        
        if algo_enum == OptimizationAlgorithm.GENETIC:
            return self._run_genetic_algorithm(container, items, parameters)
        
        elif algo_enum == OptimizationAlgorithm.CONSTRAINT:
            return self._run_constraint_solver(container, items, parameters)
        
        elif algo_enum == OptimizationAlgorithm.HYBRID:
            return self._run_hybrid_optimization(container, items, parameters)
        
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
    
    def _auto_select_algorithm(
        self,
        container: Dict,
        items: List[Dict]
    ) -> OptimizationAlgorithm:
        """
        Automatically select best algorithm based on problem characteristics.
        
        Args:
            container: Container data
            items: Items data
            
        Returns:
            Selected algorithm
        """
        num_items = len(items)
        
        # Count constraints
        has_hazmat = any(item.get('hazard_class') for item in items)
        has_fragile = any(item.get('fragile') for item in items)
        has_special = has_hazmat or has_fragile
        
        if num_items < 20:
            # Small problem - constraint solver is fast enough
            return OptimizationAlgorithm.CONSTRAINT
        elif num_items < 100:
            # Medium problem - hybrid approach
            return OptimizationAlgorithm.HYBRID if has_special else OptimizationAlgorithm.GENETIC
        else:
            # Large problem - genetic algorithm scales better
            return OptimizationAlgorithm.GENETIC
    
    def _run_genetic_algorithm(
        self,
        container: Dict,
        items: List[Dict],
        parameters: Optional[Dict]
    ) -> Dict[str, Any]:
        """Run genetic algorithm optimization."""
        logger.info("Running Genetic Algorithm optimization")
        
        ga = GeneticAlgorithm(container, items, self.config)
        
        # Override parameters if provided
        if parameters:
            if 'population_size' in parameters:
                ga.population_size = parameters['population_size']
            if 'generations' in parameters:
                ga.generations = parameters['generations']
            if 'mutation_rate' in parameters:
                ga.mutation_rate = parameters['mutation_rate']
            if 'crossover_rate' in parameters:
                ga.crossover_rate = parameters['crossover_rate']
        
        max_time = parameters.get('time_limit') if parameters else None
        result = ga.run(max_time=max_time)
        
        return result
    
    def _run_constraint_solver(
        self,
        container: Dict,
        items: List[Dict],
        parameters: Optional[Dict]
    ) -> Dict[str, Any]:
        """Run constraint programming solver."""
        logger.info("Running Constraint Programming optimization")
        
        solver = ConstraintSolver(container, items, self.config)
        
        max_time = parameters.get('time_limit') if parameters else None
        result = solver.solve(max_time=max_time)
        
        return result
    
    def _run_hybrid_optimization(
        self,
        container: Dict,
        items: List[Dict],
        parameters: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Run hybrid optimization combining genetic algorithm and constraint solver.
        
        Args:
            container: Container data
            items: Items data
            parameters: Algorithm parameters
            
        Returns:
            Best result from both algorithms
        """
        logger.info("Running Hybrid optimization (GA + CP)")
        
        # Run both algorithms with reduced time
        time_limit = parameters.get('time_limit', self.config.MAX_COMPUTATION_TIME) if parameters else self.config.MAX_COMPUTATION_TIME
        half_time = time_limit // 2
        
        # Run GA first
        ga_result = self._run_genetic_algorithm(
            container, items, {'time_limit': half_time}
        )
        
        # Run CP second
        cp_result = self._run_constraint_solver(
            container, items, {'time_limit': half_time}
        )
        
        # Select best result
        ga_score = ga_result.get('score', 0) if ga_result.get('status') == 'completed' else 0
        cp_score = cp_result.get('score', 0) if cp_result.get('status') == 'completed' else 0
        
        if ga_score >= cp_score:
            logger.info(f"GA produced better result: {ga_score} vs {cp_score}")
            best_result = ga_result
            best_result['algorithm'] = 'hybrid_ga'
        else:
            logger.info(f"CP produced better result: {cp_score} vs {ga_score}")
            best_result = cp_result
            best_result['algorithm'] = 'hybrid_cp'
        
        # Add comparison info
        best_result['hybrid_comparison'] = {
            'ga_score': ga_score,
            'cp_score': cp_score,
            'selected': 'genetic_algorithm' if ga_score >= cp_score else 'constraint_solver'
        }
        
        return best_result
    
    def _enhance_result(
        self,
        result: Dict,
        optimization_id: str,
        container: Dict,
        items: List[Dict]
    ) -> Dict[str, Any]:
        """
        Enhance optimization result with additional information.
        
        Args:
            result: Raw algorithm result
            optimization_id: Optimization ID
            container: Container data
            items: Items data
            
        Returns:
            Enhanced result
        """
        enhanced = result.copy()
        enhanced['optimization_id'] = optimization_id
        
        # Add container info
        enhanced['container'] = {
            'container_id': container.get('container_id'),
            'dimensions': {
                'length': container['length'],
                'width': container['width'],
                'height': container['height']
            },
            'volume': container.get('volume'),
            'max_weight': container.get('max_weight')
        }
        
        # Calculate additional metrics
        placements = result.get('placements', [])
        
        enhanced['metrics'] = {
            'total_items': len(items),
            'items_packed': len(placements),
            'items_unpacked': len(items) - len(placements),
            'packing_ratio': len(placements) / len(items) if items else 0,
            'utilization_percentage': result.get('utilization', 0),
            'computation_time_seconds': result.get('computation_time', 0)
        }
        
        # Weight statistics
        if placements:
            total_weight = sum(p.weight if hasattr(p, 'weight') else 0 for p in placements)
            enhanced['metrics']['total_weight_packed'] = total_weight
            enhanced['metrics']['weight_utilization'] = (
                (total_weight / container.get('max_weight', 1)) * 100
                if container.get('max_weight') else 0
            )
        
        # Validate with stowage rules if applicable
        if any(item.get('hazard_class') for item in items):
            planner = StowagePlanner(container, items)
            is_valid, violations = planner.validate_stowage(placements)
            enhanced['stowage_validation'] = {
                'is_valid': is_valid,
                'violations': violations
            }
        
        # Add timestamps
        enhanced['completed_at'] = datetime.utcnow().isoformat()
        
        return enhanced
    
    def _create_optimization_record(
        self,
        optimization_id: str,
        container: Dict,
        items: List[Dict],
        algorithm: str
    ):
        """Create optimization record in database."""
        try:
            db_manager.insert('optimizations', {
                'optimization_id': optimization_id,
                'status': OptimizationStatus.PENDING.value,
                'algorithm': algorithm,
                'container_data': json.dumps(container),
                'items_count': len(items),
                'started_at': datetime.utcnow(),
                'created_at': datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"Failed to create optimization record: {e}")
    
    def _update_optimization_status(
        self,
        optimization_id: str,
        status: OptimizationStatus,
        error_message: Optional[str] = None
    ):
        """Update optimization status in database."""
        try:
            update_data = {
                'status': status.value,
                'updated_at': datetime.utcnow()
            }
            
            if error_message:
                update_data['error_message'] = error_message
            
            if status == OptimizationStatus.COMPLETED:
                update_data['completed_at'] = datetime.utcnow()
            
            db_manager.update(
                'optimizations',
                update_data,
                'optimization_id = %s',
                (optimization_id,)
            )
        except Exception as e:
            logger.error(f"Failed to update optimization status: {e}")
    
    def _save_optimization_results(self, optimization_id: str, result: Dict):
        """Save optimization results to database."""
        try:
            import json
            
            db_manager.update(
                'optimizations',
                {
                    'result_data': json.dumps(result, default=str),
                    'utilization_percentage': result.get('utilization', 0),
                    'items_packed': result['metrics']['items_packed'],
                    'computation_time_seconds': result.get('computation_time', 0),
                    'updated_at': datetime.utcnow()
                },
                'optimization_id = %s',
                (optimization_id,)
            )
            
            # Save placements
            placements = result.get('placements', [])
            for placement in placements:
                self._save_placement(optimization_id, placement)
                
        except Exception as e:
            logger.error(f"Failed to save optimization results: {e}")
    
    def _save_placement(self, optimization_id: str, placement):
        """Save individual placement to database."""
        try:
            db_manager.insert('placements', {
                'optimization_id': optimization_id,
                'item_index': placement.item_index if hasattr(placement, 'item_index') else 0,
                'position_x': placement.x if hasattr(placement, 'x') else 0,
                'position_y': placement.y if hasattr(placement, 'y') else 0,
                'position_z': placement.z if hasattr(placement, 'z') else 0,
                'length': placement.length if hasattr(placement, 'length') else 0,
                'width': placement.width if hasattr(placement, 'width') else 0,
                'height': placement.height if hasattr(placement, 'height') else 0,
                'rotation': placement.rotation if hasattr(placement, 'rotation') else 0,
                'weight': placement.weight if hasattr(placement, 'weight') else 0,
                'created_at': datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"Failed to save placement: {e}")
    
    def get_optimization_status(self, optimization_id: str) -> Optional[Dict]:
        """
        Get current status of an optimization.
        
        Args:
            optimization_id: Optimization ID
            
        Returns:
            Status dictionary or None
        """
        try:
            result = db_manager.find_by_id(
                'optimizations',
                optimization_id,
                'optimization_id'
            )
            return result
        except Exception as e:
            logger.error(f"Failed to get optimization status: {e}")
            return None
    
    def cancel_optimization(self, optimization_id: str) -> bool:
        """
        Cancel a running optimization.
        
        Args:
            optimization_id: Optimization ID
            
        Returns:
            True if cancelled successfully
        """
        try:
            self._update_optimization_status(
                optimization_id,
                OptimizationStatus.CANCELLED
            )
            logger.info(f"Optimization {optimization_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel optimization: {e}")
            return False