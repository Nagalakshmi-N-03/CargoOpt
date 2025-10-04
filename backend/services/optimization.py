import logging
import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import asyncio

from backend.algorithms.packing import PackingAlgorithm
from backend.algorithms.genetic_algorithm import GeneticAlgorithm
from backend.algorithms.stowage import StowageOptimizer
from backend.services.data_processor import DataProcessor
from backend.models import OptimizationResult

logger = logging.getLogger(__name__)

class OptimizationService:
    def __init__(self, db: Session):
        self.db = db
        self.data_processor = DataProcessor(db)
        self.packing_algo = PackingAlgorithm()
        self.genetic_algo = GeneticAlgorithm()
        self.stowage_algo = StowageOptimizer()
        self.logger = logging.getLogger(__name__)
    
    async def optimize_single_container(self, container_data: Dict, items_data: List[Dict], 
                                      algorithm: str = "auto", **kwargs) -> Dict:
        """
        Optimize packing for a single container
        """
        try:
            start_time = time.time()
            
            # Validate input data
            container_validation = self.data_processor.validate_container_data(container_data)
            items_validation = self.data_processor.validate_cargo_items(items_data)
            
            if not container_validation['is_valid']:
                raise ValueError(f"Invalid container data: {container_validation['error']}")
            
            if not items_validation['is_valid']:
                raise ValueError(f"Invalid items data: {items_validation['error']}")
            
            # Choose algorithm automatically if not specified
            if algorithm == "auto":
                algorithm = self._select_algorithm(container_data, items_validation['items'])
            
            # Run optimization
            if algorithm == "packing":
                result = self.packing_algo.optimize(container_data, items_data)
            elif algorithm == "genetic":
                generations = kwargs.get('generations', 100)
                population_size = kwargs.get('population_size', 50)
                mutation_rate = kwargs.get('mutation_rate', 0.1)
                
                self.genetic_algo.population_size = population_size
                self.genetic_algo.mutation_rate = mutation_rate
                result = self.genetic_algo.optimize(container_data, items_data, generations)
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")
            
            execution_time = time.time() - start_time
            
            # Calculate comprehensive metrics
            comprehensive_metrics = self.data_processor.calculate_packing_metrics(
                container_data, items_validation['items'], result['placements']
            )
            
            # Merge metrics
            result['metrics'].update(comprehensive_metrics)
            result['execution_time'] = round(execution_time, 4)
            result['algorithm_used'] = algorithm
            
            # Generate report
            report = self.data_processor.generate_packing_report(result, algorithm)
            result['report'] = report
            
            # Save to database
            self._save_optimization_result(result, algorithm, container_data)
            
            return {
                'success': True,
                'algorithm': algorithm,
                'result': result,
                'validation': {
                    'container': container_validation,
                    'items': items_validation
                }
            }
            
        except Exception as e:
            self.logger.error(f"Single container optimization failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'algorithm': algorithm
            }
    
    async def optimize_multi_container(self, containers_data: List[Dict], items_data: List[Dict],
                                     strategy: str = "balanced") -> Dict:
        """
        Optimize packing across multiple containers
        """
        try:
            start_time = time.time()
            
            # Validate all containers
            validated_containers = []
            for container in containers_data:
                validation = self.data_processor.validate_container_data(container)
                if not validation['is_valid']:
                    raise ValueError(f"Invalid container data: {validation['error']}")
                validated_containers.append(container)
            
            # Validate items
            items_validation = self.data_processor.validate_cargo_items(items_data)
            if not items_validation['is_valid']:
                raise ValueError(f"Invalid items data: {items_validation['error']}")
            
            # Run stowage optimization
            result = self.stowage_algo.optimize(containers_data, items_data)
            execution_time = time.time() - start_time
            
            # Add execution time and strategy
            result['execution_time'] = round(execution_time, 4)
            result['strategy'] = strategy
            result['algorithm_used'] = 'stowage'
            
            # Save results for each container
            for container_id, assignment in result['container_assignments'].items():
                container_result = {
                    'placements': [],  # Stowage doesn't provide detailed placements
                    'metrics': assignment['metrics'],
                    'algorithm': 'stowage',
                    'container_id': container_id
                }
                self._save_optimization_result(container_result, 'stowage', assignment['container'])
            
            return {
                'success': True,
                'algorithm': 'stowage',
                'strategy': strategy,
                'result': result,
                'validation': {
                    'containers': f"Validated {len(validated_containers)} containers",
                    'items': items_validation
                }
            }
            
        except Exception as e:
            self.logger.error(f"Multi-container optimization failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'algorithm': 'stowage'
            }
    
    async def compare_algorithms(self, container_data: Dict, items_data: List[Dict], 
                               algorithms: List[str] = None) -> Dict:
        """
        Compare multiple algorithms on the same problem
        """
        try:
            if algorithms is None:
                algorithms = ['packing', 'genetic']
            
            results = {}
            
            for algorithm in algorithms:
                self.logger.info(f"Running {algorithm} algorithm...")
                
                if algorithm == 'packing':
                    result = await self.optimize_single_container(container_data, items_data, 'packing')
                elif algorithm == 'genetic':
                    result = await self.optimize_single_container(container_data, items_data, 'genetic')
                else:
                    self.logger.warning(f"Unknown algorithm: {algorithm}")
                    continue
                
                if result['success']:
                    results[algorithm] = result['result']
            
            # Compare results
            comparison = self.data_processor.compare_algorithms(results)
            
            return {
                'success': True,
                'comparison': comparison,
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"Algorithm comparison failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def batch_optimize(self, optimization_tasks: List[Dict]) -> Dict:
        """
        Process multiple optimization tasks in batch
        """
        try:
            results = []
            
            for task in optimization_tasks:
                container_data = task.get('container')
                items_data = task.get('items')
                algorithm = task.get('algorithm', 'auto')
                task_id = task.get('id', f"task_{len(results)}")
                
                if not container_data or not items_data:
                    self.logger.warning(f"Skipping task {task_id}: missing container or items data")
                    continue
                
                result = await self.optimize_single_container(container_data, items_data, algorithm)
                result['task_id'] = task_id
                results.append(result)
            
            # Generate batch summary
            summary = self._generate_batch_summary(results)
            
            return {
                'success': True,
                'summary': summary,
                'results': results,
                'total_tasks': len(optimization_tasks),
                'processed_tasks': len(results)
            }
            
        except Exception as e:
            self.logger.error(f"Batch optimization failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_optimization_history(self, limit: int = 10, algorithm: str = None) -> Dict:
        """
        Get optimization history from database
        """
        try:
            query = self.db.query(OptimizationResult)
            
            if algorithm:
                query = query.filter(OptimizationResult.algorithm == algorithm)
            
            results = query.order_by(OptimizationResult.created_at.desc()).limit(limit).all()
            
            history = []
            for result in results:
                history.append({
                    'id': result.id,
                    'algorithm': result.algorithm,
                    'utilization_rate': result.utilization_rate,
                    'total_items_packed': result.total_items_packed,
                    'execution_time': result.execution_time,
                    'container_volume': result.total_volume_used / result.utilization_rate if result.utilization_rate > 0 else 0,
                    'created_at': result.created_at.isoformat()
                })
            
            return {
                'success': True,
                'count': len(history),
                'history': history
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get optimization history: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _select_algorithm(self, container: Dict, items: List[Dict]) -> str:
        """
        Automatically select the best algorithm based on problem characteristics
        """
        total_items = sum(item['quantity'] for item in items)
        total_volume = sum(item['volume'] * item['quantity'] for item in items)
        container_volume = container['length'] * container['width'] * container['height']
        
        # Use genetic algorithm for complex problems
        if total_items > 20 or total_volume / container_volume > 0.8:
            return "genetic"
        else:
            return "packing"
    
    def _save_optimization_result(self, result: Dict, algorithm: str, container_data: Dict):
        """
        Save optimization result to database
        """
        try:
            metrics = result.get('metrics', {})
            volume_metrics = metrics.get('volume_metrics', {})
            
            optimization_result = OptimizationResult(
                algorithm=algorithm,
                container_id=0,  # You might want to use actual container IDs
                utilization_rate=volume_metrics.get('utilization_rate', metrics.get('utilization_rate', 0)),
                total_items_packed=metrics.get('total_items_packed', metrics.get('packed_items', 0)),
                total_volume_used=volume_metrics.get('used_volume', metrics.get('total_volume_used', 0)),
                total_weight_used=metrics.get('total_weight_used', 0),
                execution_time=result.get('execution_time', 0),
                placement_data=result
            )
            
            self.db.add(optimization_result)
            self.db.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to save optimization result: {str(e)}")
            # Don't raise to avoid breaking the optimization process
    
    def _generate_batch_summary(self, results: List[Dict]) -> Dict:
        """
        Generate summary for batch optimization results
        """
        successful_tasks = [r for r in results if r.get('success', False)]
        failed_tasks = [r for r in results if not r.get('success', False)]
        
        if not successful_tasks:
            return {
                'total_tasks': len(results),
                'successful_tasks': 0,
                'failed_tasks': len(failed_tasks),
                'average_utilization': 0,
                'best_utilization': 0
            }
        
        utilizations = []
        for task in successful_tasks:
            result = task.get('result', {})
            metrics = result.get('metrics', {})
            volume_metrics = metrics.get('volume_metrics', {})
            utilization = volume_metrics.get('utilization_rate', metrics.get('utilization_rate', 0))
            utilizations.append(utilization)
        
        return {
            'total_tasks': len(results),
            'successful_tasks': len(successful_tasks),
            'failed_tasks': len(failed_tasks),
            'success_rate': len(successful_tasks) / len(results),
            'average_utilization': sum(utilizations) / len(utilizations),
            'best_utilization': max(utilizations),
            'worst_utilization': min(utilizations)
        }
    
    async def validate_optimization(self, container_data: Dict, items_data: List[Dict], 
                                  placements: List[Dict]) -> Dict:
        """
        Validate optimization result
        """
        try:
            # Validate container and items
            container_validation = self.data_processor.validate_container_data(container_data)
            items_validation = self.data_processor.validate_cargo_items(items_data)
            
            if not container_validation['is_valid']:
                return {
                    'success': False,
                    'valid': False,
                    'error': f"Invalid container: {container_validation['error']}"
                }
            
            if not items_validation['is_valid']:
                return {
                    'success': False,
                    'valid': False,
                    'error': f"Invalid items: {items_validation['error']}"
                }
            
            # Validate placements
            is_valid = self.packing_algo.validate_placement(container_data, placements)
            
            if is_valid:
                # Calculate metrics for validation
                metrics = self.data_processor.calculate_packing_metrics(
                    container_data, items_validation['items'], placements
                )
                
                return {
                    'success': True,
                    'valid': True,
                    'metrics': metrics,
                    'message': "Optimization result is valid"
                }
            else:
                return {
                    'success': True,
                    'valid': False,
                    'message': "Placements have issues (overlaps or out of bounds)"
                }
                
        except Exception as e:
            self.logger.error(f"Optimization validation failed: {str(e)}")
            return {
                'success': False,
                'valid': False,
                'error': str(e)
            }