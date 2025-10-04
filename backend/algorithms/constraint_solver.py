import pulp
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
import math

@dataclass
class Container:
    id: str
    name: str
    length: float
    width: float
    height: float
    weight: float
    type: str

@dataclass
class Vehicle:
    id: str
    type: str
    max_weight: float
    length: float
    width: float
    height: float
    emission_factor: float

@dataclass
class OptimizationResult:
    assignments: Dict[str, List[str]]
    total_emissions: float
    utilization: float
    vehicle_count: int
    total_containers: int
    status: str

class ConstraintSolver:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def solve_optimization(self, containers: List[Container], vehicles: List[Vehicle], 
                          distance_km: float = 100.0) -> Optional[OptimizationResult]:
        """
        Solve the container loading and vehicle assignment problem with emissions optimization
        Matches the frontend OptimizationResult structure from previous work
        """
        try:
            # Create the optimization problem
            prob = pulp.LpProblem("CargoOptimization", pulp.LpMinimize)
            
            # Decision variables
            x = pulp.LpVariable.dicts("assign", 
                                    [(c.id, v.id) for c in containers for v in vehicles],
                                    cat='Binary')
            
            y = pulp.LpVariable.dicts("vehicle_used", 
                                    [v.id for v in vehicles], 
                                    cat='Binary')
            
            # Objective: Minimize total emissions (matching frontend calculation)
            prob += pulp.lpSum([
                x[c.id, v.id] * c.weight * v.emission_factor * distance_km
                for c in containers for v in vehicles
            ]), "Total_Emissions"
            
            # Constraints
            
            # Each container must be assigned to exactly one vehicle
            for c in containers:
                prob += pulp.lpSum([x[c.id, v.id] for v in vehicles]) == 1, f"Assign_Container_{c.id}"
            
            # Vehicle capacity constraints (weight)
            for v in vehicles:
                prob += (pulp.lpSum([x[c.id, v.id] * c.weight for c in containers]) 
                        <= v.max_weight * y[v.id]), f"Weight_Capacity_{v.id}"
            
            # 3D packing constraints
            for v in vehicles:
                # Volume constraint
                total_volume = pulp.lpSum([
                    x[c.id, v.id] * (c.length * c.width * c.height) 
                    for c in containers
                ])
                vehicle_volume = v.length * v.width * v.height
                prob += total_volume <= vehicle_volume * y[v.id], f"Volume_Capacity_{v.id}"
                
                # Individual dimension constraints
                for c in containers:
                    if not self._can_fit(c, v):
                        prob += x[c.id, v.id] == 0, f"Size_Constraint_{c.id}_{v.id}"
            
            # Solve the problem
            prob.solve(pulp.PULP_CBC_CMD(msg=0))
            
            if pulp.LpStatus[prob.status] == 'Optimal':
                return self._extract_solution(containers, vehicles, x, y, distance_km)
            else:
                self.logger.warning(f"No optimal solution found: {pulp.LpStatus[prob.status]}")
                return self._get_fallback_solution(containers, vehicles, distance_km)
                
        except Exception as e:
            self.logger.error(f"Error in optimization: {e}")
            return self._get_fallback_solution(containers, vehicles, distance_km)
    
    def _can_fit(self, container: Container, vehicle: Vehicle) -> bool:
        """Check if container can fit in vehicle in any orientation"""
        container_dims = [container.length, container.width, container.height]
        vehicle_dims = [vehicle.length, vehicle.width, vehicle.height]
        
        # Check all possible orientations
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    if (i != j and i != k and j != k and
                        container_dims[i] <= vehicle_dims[0] and
                        container_dims[j] <= vehicle_dims[1] and
                        container_dims[k] <= vehicle_dims[2]):
                        return True
        return False
    
    def _extract_solution(self, containers: List[Container], vehicles: List[Vehicle],
                         x: Dict, y: Dict, distance_km: float) -> OptimizationResult:
        """Extract solution from solved model matching frontend structure"""
        assignments = {}
        total_emissions = 0
        
        for v in vehicles:
            vehicle_containers = []
            for c in containers:
                if pulp.value(x[c.id, v.id]) == 1:
                    vehicle_containers.append(c.id)
                    total_emissions += c.weight * v.emission_factor * distance_km
            
            if vehicle_containers:
                assignments[v.id] = vehicle_containers
        
        vehicle_count = sum(1 for v in vehicles if pulp.value(y[v.id]) == 1)
        
        # Calculate utilization (matching frontend calculation)
        total_weight = sum(c.weight for c in containers)
        max_capacity = sum(v.max_weight for v in vehicles if pulp.value(y[v.id]) == 1)
        utilization = (total_weight / max_capacity * 100) if max_capacity > 0 else 0
        
        return OptimizationResult(
            assignments=assignments,
            total_emissions=round(total_emissions, 2),
            utilization=round(utilization, 1),
            vehicle_count=vehicle_count,
            total_containers=len(containers),
            status="optimal"
        )
    
    def _get_fallback_solution(self, containers: List[Container], 
                             vehicles: List[Vehicle], distance_km: float) -> OptimizationResult:
        """Provide a fallback solution when optimization fails"""
        # Simple greedy assignment as fallback
        assignments = {}
        remaining_containers = containers.copy()
        vehicles_sorted = sorted(vehicles, key=lambda v: v.emission_factor)
        
        total_emissions = 0
        vehicle_count = 0
        
        for vehicle in vehicles_sorted:
            if not remaining_containers:
                break
                
            vehicle_containers = []
            current_weight = 0
            current_volume = 0
            vehicle_volume = vehicle.length * vehicle.width * vehicle.height
            
            for container in remaining_containers[:]:
                if (current_weight + container.weight <= vehicle.max_weight and
                    current_volume + (container.length * container.width * container.height) <= vehicle_volume and
                    self._can_fit(container, vehicle)):
                    
                    vehicle_containers.append(container.id)
                    current_weight += container.weight
                    current_volume += (container.length * container.width * container.height)
                    total_emissions += container.weight * vehicle.emission_factor * distance_km
                    remaining_containers.remove(container)
            
            if vehicle_containers:
                assignments[vehicle.id] = vehicle_containers
                vehicle_count += 1
        
        # Calculate utilization
        total_weight = sum(c.weight for c in containers)
        used_capacity = sum(vehicle.max_weight for vehicle in vehicles_sorted[:vehicle_count])
        utilization = (total_weight / used_capacity * 100) if used_capacity > 0 else 0
        
        return OptimizationResult(
            assignments=assignments,
            total_emissions=round(total_emissions, 2),
            utilization=round(utilization, 1),
            vehicle_count=vehicle_count,
            total_containers=len(containers),
            status="fallback" if remaining_containers else "feasible"
        )