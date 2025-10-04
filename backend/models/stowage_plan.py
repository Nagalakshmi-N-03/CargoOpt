import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)

class StowageStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ContainerStatus(str, Enum):
    EMPTY = "empty"
    PARTIALLY_LOADED = "partially_loaded"
    FULLY_LOADED = "fully_loaded"
    OVERLOADED = "overloaded"

@dataclass
class ContainerAssignment:
    container_id: str
    container_data: Dict[str, Any]
    items: List[Dict[str, Any]]
    placements: List[Dict[str, Any]]
    utilization_rate: float
    weight_utilization: float
    status: ContainerStatus
    total_volume_used: float
    total_weight_used: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def validate_assignment(self) -> Dict[str, Any]:
        """Validate container assignment for constraints"""
        issues = []
        warnings = []
        
        # Check weight constraints
        max_weight = self.container_data.get('max_weight', 0)
        if self.total_weight_used > max_weight:
            issues.append(f"Container {self.container_id} is overloaded: {self.total_weight_used:.2f}kg > {max_weight:.2f}kg")
        
        # Check volume constraints
        container_volume = (
            self.container_data['length'] * 
            self.container_data['width'] * 
            self.container_data['height']
        )
        if self.total_volume_used > container_volume:
            issues.append(f"Container {self.container_id} volume exceeded: {self.total_volume_used:.2f}cm³ > {container_volume:.2f}cm³")
        
        # Check utilization thresholds
        if self.utilization_rate < 0.3:
            warnings.append(f"Container {self.container_id} has low space utilization: {self.utilization_rate:.1%}")
        
        if self.weight_utilization < 0.3:
            warnings.append(f"Container {self.container_id} has low weight utilization: {self.weight_utilization:.1%}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

@dataclass
class StowagePlan:
    plan_id: str
    containers: List[ContainerAssignment]
    unassigned_items: List[Dict[str, Any]]
    total_utilization: float
    total_containers_used: int
    total_items_packed: int
    total_volume_used: float
    total_weight_used: float
    algorithm_used: str
    strategy: str
    status: StowageStatus
    created_at: datetime
    execution_time: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not hasattr(self, 'created_at') or self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stowage plan to dictionary"""
        data = asdict(self)
        # Convert datetime to string for JSON serialization
        data['created_at'] = self.created_at.isoformat()
        return data
    
    def to_json(self) -> str:
        """Convert stowage plan to JSON string"""
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StowagePlan':
        """Create StowagePlan from dictionary"""
        # Convert string back to datetime
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        # Recreate container assignments
        if 'containers' in data:
            containers_data = data['containers']
            data['containers'] = [
                ContainerAssignment(**container_data) 
                for container_data in containers_data
            ]
        
        return cls(**data)
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive stowage metrics"""
        total_container_volume = sum(
            assignment.container_data['length'] * 
            assignment.container_data['width'] * 
            assignment.container_data['height']
            for assignment in self.containers
        )
        
        total_container_weight = sum(
            assignment.container_data.get('max_weight', 0)
            for assignment in self.containers
        )
        
        space_efficiency = self.total_volume_used / total_container_volume if total_container_volume > 0 else 0
        weight_efficiency = self.total_weight_used / total_container_weight if total_container_weight > 0 else 0
        
        # Calculate balance score (how evenly containers are utilized)
        utilization_rates = [assignment.utilization_rate for assignment in self.containers]
        if utilization_rates:
            avg_utilization = sum(utilization_rates) / len(utilization_rates)
            balance_score = 1 - (sum(abs(rate - avg_utilization) for rate in utilization_rates) / len(utilization_rates))
        else:
            balance_score = 0
        
        overall_efficiency = (space_efficiency * 0.6 + weight_efficiency * 0.3 + balance_score * 0.1)
        
        return {
            'space_efficiency': round(space_efficiency, 4),
            'weight_efficiency': round(weight_efficiency, 4),
            'balance_score': round(balance_score, 4),
            'overall_efficiency': round(overall_efficiency, 4),
            'container_count': len(self.containers),
            'items_packed': self.total_items_packed,
            'items_unassigned': len(self.unassigned_items),
            'packing_rate': self.total_items_packed / (self.total_items_packed + len(self.unassigned_items)) if (self.total_items_packed + len(self.unassigned_items)) > 0 else 0
        }
    
    def validate_plan(self) -> Dict[str, Any]:
        """Validate the entire stowage plan"""
        all_issues = []
        all_warnings = []
        
        # Validate each container assignment
        for assignment in self.containers:
            validation = assignment.validate_assignment()
            all_issues.extend(validation['issues'])
            all_warnings.extend(validation['warnings'])
        
        # Check for unassigned items
        if self.unassigned_items:
            all_warnings.append(f"{len(self.unassigned_items)} items could not be assigned to containers")
        
        # Check overall efficiency
        metrics = self.calculate_metrics()
        if metrics['overall_efficiency'] < 0.6:
            all_warnings.append(f"Low overall efficiency: {metrics['overall_efficiency']:.1%}")
        
        return {
            'valid': len(all_issues) == 0,
            'issues': all_issues,
            'warnings': all_warnings,
            'metrics': metrics
        }
    
    def get_container_summary(self) -> List[Dict[str, Any]]:
        """Get summary for each container"""
        summary = []
        for assignment in self.containers:
            container_data = assignment.container_data
            summary.append({
                'container_id': assignment.container_id,
                'name': container_data.get('name', 'Unknown'),
                'type': container_data.get('type', 'custom'),
                'items_count': len(assignment.items),
                'utilization_rate': assignment.utilization_rate,
                'weight_utilization': assignment.weight_utilization,
                'status': assignment.status,
                'total_volume_used': assignment.total_volume_used,
                'total_weight_used': assignment.total_weight_used
            })
        return summary
    
    def get_unassigned_items_summary(self) -> Dict[str, Any]:
        """Get summary of unassigned items"""
        if not self.unassigned_items:
            return {'count': 0, 'total_volume': 0, 'total_weight': 0}
        
        total_volume = sum(
            item['length'] * item['width'] * item['height'] * item.get('quantity', 1)
            for item in self.unassigned_items
        )
        total_weight = sum(
            item['weight'] * item.get('quantity', 1)
            for item in self.unassigned_items
        )
        
        return {
            'count': len(self.unassigned_items),
            'total_volume': total_volume,
            'total_weight': total_weight,
            'items': self.unassigned_items
        }