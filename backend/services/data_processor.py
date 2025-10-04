import logging
import json
import pandas as pd
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import math

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def validate_container_data(self, container_data: Dict) -> Dict:
        """
        Validate and normalize container data
        """
        try:
            required_fields = ['length', 'width', 'height', 'max_weight']
            
            # Check required fields
            for field in required_fields:
                if field not in container_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate dimensions
            length = float(container_data['length'])
            width = float(container_data['width'])
            height = float(container_data['height'])
            max_weight = float(container_data['max_weight'])
            
            if any(dim <= 0 for dim in [length, width, height, max_weight]):
                raise ValueError("All dimensions and weight must be positive")
            
            # Calculate volume
            volume = length * width * height
            
            return {
                'length': length,
                'width': width,
                'height': height,
                'max_weight': max_weight,
                'volume': volume,
                'is_valid': True
            }
            
        except Exception as e:
            self.logger.error(f"Container data validation failed: {str(e)}")
            return {
                'is_valid': False,
                'error': str(e)
            }
    
    def validate_cargo_items(self, items_data: List[Dict]) -> Dict:
        """
        Validate and normalize cargo items data
        """
        try:
            validated_items = []
            total_volume = 0
            total_weight = 0
            item_count = 0
            
            required_fields = ['id', 'length', 'width', 'height', 'weight']
            
            for item in items_data:
                # Check required fields
                for field in required_fields:
                    if field not in item:
                        raise ValueError(f"Missing required field in item: {field}")
                
                # Validate dimensions
                length = float(item['length'])
                width = float(item['width'])
                height = float(item['height'])
                weight = float(item['weight'])
                quantity = int(item.get('quantity', 1))
                
                if any(dim <= 0 for dim in [length, width, height, weight]):
                    raise ValueError(f"Item {item['id']}: All dimensions and weight must be positive")
                
                if quantity <= 0:
                    raise ValueError(f"Item {item['id']}: Quantity must be positive")
                
                # Calculate item metrics
                volume = length * width * height
                total_volume += volume * quantity
                total_weight += weight * quantity
                item_count += quantity
                
                validated_item = {
                    'id': item['id'],
                    'name': item.get('name', f"Item_{item['id']}"),
                    'length': length,
                    'width': width,
                    'height': height,
                    'weight': weight,
                    'quantity': quantity,
                    'volume': volume,
                    'fragile': bool(item.get('fragile', False)),
                    'stackable': bool(item.get('stackable', True)),
                    'rotation_allowed': bool(item.get('rotation_allowed', True))
                }
                
                validated_items.append(validated_item)
            
            return {
                'items': validated_items,
                'summary': {
                    'total_items': item_count,
                    'total_volume': total_volume,
                    'total_weight': total_weight,
                    'unique_items': len(validated_items)
                },
                'is_valid': True
            }
            
        except Exception as e:
            self.logger.error(f"Cargo items validation failed: {str(e)}")
            return {
                'is_valid': False,
                'error': str(e),
                'items': [],
                'summary': {}
            }
    
    def calculate_packing_metrics(self, container: Dict, items: List[Dict], placements: List[Dict]) -> Dict:
        """
        Calculate comprehensive packing metrics
        """
        try:
            container_volume = container['length'] * container['width'] * container['height']
            used_volume = 0
            used_weight = 0
            packed_items = 0
            
            # Calculate volume utilization from placements
            for placement in placements:
                dims = placement['dimensions']
                used_volume += dims[0] * dims[1] * dims[2]
                packed_items += 1
            
            # Calculate weight utilization (simplified)
            for item in items:
                if any(p['item_id'] == item['id'] for p in placements):
                    used_weight += item['weight'] * item['quantity']
            
            volume_utilization = used_volume / container_volume if container_volume > 0 else 0
            weight_utilization = used_weight / container['max_weight'] if container['max_weight'] > 0 else 0
            
            # Calculate efficiency score
            efficiency_score = self._calculate_efficiency_score(
                volume_utilization, 
                weight_utilization,
                packed_items,
                len(items)
            )
            
            return {
                'volume_metrics': {
                    'container_volume': round(container_volume, 2),
                    'used_volume': round(used_volume, 2),
                    'available_volume': round(container_volume - used_volume, 2),
                    'utilization_rate': round(volume_utilization, 4)
                },
                'weight_metrics': {
                    'max_weight': container['max_weight'],
                    'used_weight': round(used_weight, 2),
                    'available_weight': round(container['max_weight'] - used_weight, 2),
                    'utilization_rate': round(weight_utilization, 4)
                },
                'item_metrics': {
                    'total_items': sum(item['quantity'] for item in items),
                    'packed_items': packed_items,
                    'packing_rate': round(packed_items / sum(item['quantity'] for item in items), 4) if items else 0
                },
                'efficiency_score': round(efficiency_score, 4)
            }
            
        except Exception as e:
            self.logger.error(f"Metrics calculation failed: {str(e)}")
            raise
    
    def _calculate_efficiency_score(self, volume_util: float, weight_util: float, 
                                  packed_items: int, total_items: int) -> float:
        """
        Calculate overall efficiency score (0-1)
        """
        volume_score = volume_util * 0.4  # 40% weight
        weight_score = weight_util * 0.3  # 30% weight
        packing_score = (packed_items / total_items) * 0.3 if total_items > 0 else 0  # 30% weight
        
        return volume_score + weight_score + packing_score
    
    def generate_packing_report(self, optimization_result: Dict, algorithm: str) -> Dict:
        """
        Generate comprehensive packing report
        """
        try:
            metrics = optimization_result.get('metrics', {})
            placements = optimization_result.get('placements', [])
            
            report = {
                'algorithm_used': algorithm,
                'timestamp': pd.Timestamp.now().isoformat(),
                'summary': {
                    'utilization_rate': metrics.get('utilization_rate', 0),
                    'total_items_packed': metrics.get('total_items_packed', 0),
                    'total_volume_used': metrics.get('total_volume_used', 0),
                    'efficiency_score': metrics.get('efficiency_score', 0)
                },
                'placement_analysis': self._analyze_placements(placements),
                'recommendations': self._generate_recommendations(metrics, algorithm)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
            raise
    
    def _analyze_placements(self, placements: List[Dict]) -> Dict:
        """
        Analyze placement patterns and characteristics
        """
        if not placements:
            return {}
        
        total_volume = 0
        rotated_items = 0
        placement_heights = []
        
        for placement in placements:
            dims = placement['dimensions']
            total_volume += dims[0] * dims[1] * dims[2]
            
            if placement.get('rotated', False):
                rotated_items += 1
            
            placement_heights.append(placement['position'][2] + dims[2])
        
        avg_height = sum(placement_heights) / len(placement_heights) if placement_heights else 0
        max_height = max(placement_heights) if placement_heights else 0
        
        return {
            'total_placements': len(placements),
            'rotated_items': rotated_items,
            'rotation_rate': rotated_items / len(placements) if placements else 0,
            'average_height': round(avg_height, 2),
            'max_height': round(max_height, 2),
            'total_placed_volume': round(total_volume, 2)
        }
    
    def _generate_recommendations(self, metrics: Dict, algorithm: str) -> List[str]:
        """
        Generate optimization recommendations
        """
        recommendations = []
        
        utilization = metrics.get('utilization_rate', 0)
        packed_items = metrics.get('total_items_packed', 0)
        total_items = metrics.get('total_items', packed_items)
        
        if utilization < 0.6:
            recommendations.append("Consider using a smaller container or adding more items")
        
        if utilization > 0.9:
            recommendations.append("Excellent space utilization achieved")
        
        if packed_items < total_items:
            recommendations.append(f"{total_items - packed_items} items could not be packed. Consider using multiple containers.")
        
        if algorithm == "packing" and utilization < 0.7:
            recommendations.append("Try genetic algorithm for potentially better optimization")
        
        if not recommendations:
            recommendations.append("Good optimization result achieved")
        
        return recommendations
    
    def export_to_csv(self, optimization_result: Dict, filename: str) -> str:
        """
        Export optimization result to CSV
        """
        try:
            placements = optimization_result.get('placements', [])
            metrics = optimization_result.get('metrics', {})
            
            # Create placements DataFrame
            placements_data = []
            for placement in placements:
                placements_data.append({
                    'item_id': placement['item_id'],
                    'x_position': placement['position'][0],
                    'y_position': placement['position'][1],
                    'z_position': placement['position'][2],
                    'length': placement['dimensions'][0],
                    'width': placement['dimensions'][1],
                    'height': placement['dimensions'][2],
                    'rotated': placement.get('rotated', False)
                })
            
            df_placements = pd.DataFrame(placements_data)
            
            # Create metrics DataFrame
            metrics_data = [{
                'utilization_rate': metrics.get('utilization_rate', 0),
                'total_items_packed': metrics.get('total_items_packed', 0),
                'total_volume_used': metrics.get('total_volume_used', 0),
                'total_weight_used': metrics.get('total_weight_used', 0),
                'algorithm': optimization_result.get('algorithm', 'unknown')
            }]
            
            df_metrics = pd.DataFrame(metrics_data)
            
            # Save to CSV
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df_placements.to_excel(writer, sheet_name='Placements', index=False)
                df_metrics.to_excel(writer, sheet_name='Metrics', index=False)
            
            return filename
            
        except Exception as e:
            self.logger.error(f"CSV export failed: {str(e)}")
            raise
    
    def compare_algorithms(self, results: Dict[str, Dict]) -> Dict:
        """
        Compare results from different algorithms
        """
        try:
            comparison = {}
            
            for algo_name, result in results.items():
                metrics = result.get('metrics', {})
                comparison[algo_name] = {
                    'utilization_rate': metrics.get('utilization_rate', 0),
                    'total_items_packed': metrics.get('total_items_packed', 0),
                    'total_volume_used': metrics.get('total_volume_used', 0),
                    'execution_time': result.get('execution_time', 0),
                    'efficiency_score': metrics.get('efficiency_score', 0)
                }
            
            # Find best algorithm
            best_utilization = max(comp['utilization_rate'] for comp in comparison.values())
            best_efficiency = max(comp['efficiency_score'] for comp in comparison.values())
            fastest = min(comp['execution_time'] for comp in comparison.values())
            
            best_algo_util = next(algo for algo, comp in comparison.items() 
                                if comp['utilization_rate'] == best_utilization)
            best_algo_eff = next(algo for algo, comp in comparison.items() 
                               if comp['efficiency_score'] == best_efficiency)
            fastest_algo = next(algo for algo, comp in comparison.items() 
                              if comp['execution_time'] == fastest)
            
            return {
                'comparison': comparison,
                'best_by_utilization': best_algo_util,
                'best_by_efficiency': best_algo_eff,
                'fastest': fastest_algo,
                'recommendation': self._get_algorithm_recommendation(comparison)
            }
            
        except Exception as e:
            self.logger.error(f"Algorithm comparison failed: {str(e)}")
            raise
    
    def _get_algorithm_recommendation(self, comparison: Dict) -> str:
        """
        Get algorithm recommendation based on comparison
        """
        if not comparison:
            return "No data available for comparison"
        
        best_utilization = max(comp['utilization_rate'] for comp in comparison.values())
        best_efficiency = max(comp['efficiency_score'] for comp in comparison.values())
        
        if best_utilization > 0.85 and best_efficiency > 0.8:
            return "All algorithms performed well. Use genetic for complex scenarios, packing for simple ones."
        elif best_utilization < 0.6:
            return "Consider reviewing item sizes or container selection"
        else:
            return "Good results achieved. Consider genetic algorithm for maximum optimization."