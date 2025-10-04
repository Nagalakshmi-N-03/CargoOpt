import math
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

@dataclass
class EmissionFactors:
    TRUCK_SMALL: float = 0.00012  # kg CO2 per kg-km
    TRUCK_MEDIUM: float = 0.00010
    TRUCK_LARGE: float = 0.00008
    VAN: float = 0.00015
    DEFAULT: float = 0.00010

@dataclass
class EmissionResult:
    total_emissions_kg: float
    emissions_per_vehicle: Dict[str, float]
    emissions_per_container: Dict[str, float]
    distance_km: float
    equivalent_metrics: Dict[str, float]

class EmissionCalculator:
    def __init__(self):
        self.factors = EmissionFactors()
        self.logger = logging.getLogger(__name__)
    
    def calculate_emissions(self, assignments: Dict[str, List[str]], 
                          containers: List[Dict], 
                          vehicles: List[Dict],
                          distance_km: float = 100.0) -> EmissionResult:
        """
        Calculate emissions for the given assignments
        Matches the frontend emission calculation logic
        """
        try:
            # Create lookup dictionaries
            container_lookup = {c['id']: c for c in containers}
            vehicle_lookup = {v['id']: v for v in vehicles}
            
            emissions_per_vehicle = {}
            emissions_per_container = {}
            total_emissions = 0.0
            
            # Calculate emissions for each vehicle
            for vehicle_id, container_ids in assignments.items():
                vehicle = vehicle_lookup.get(vehicle_id)
                if not vehicle:
                    continue
                
                emission_factor = self._get_emission_factor(vehicle)
                vehicle_emissions = 0.0
                
                for container_id in container_ids:
                    container = container_lookup.get(container_id)
                    if container:
                        container_emissions = (container['weight'] * 
                                             emission_factor * distance_km)
                        emissions_per_container[container_id] = container_emissions
                        vehicle_emissions += container_emissions
                
                emissions_per_vehicle[vehicle_id] = vehicle_emissions
                total_emissions += vehicle_emissions
            
            # Calculate equivalent metrics (matching frontend)
            equivalent_metrics = self._calculate_equivalent_metrics(total_emissions)
            
            return EmissionResult(
                total_emissions_kg=round(total_emissions, 2),
                emissions_per_vehicle={k: round(v, 2) for k, v in emissions_per_vehicle.items()},
                emissions_per_container={k: round(v, 2) for k, v in emissions_per_container.items()},
                distance_km=distance_km,
                equivalent_metrics=equivalent_metrics
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating emissions: {e}")
            raise
    
    def _get_emission_factor(self, vehicle: Dict) -> float:
        """Get emission factor based on vehicle type matching frontend logic"""
        vehicle_type = vehicle.get('type', '').lower()
        
        if 'small' in vehicle_type:
            return self.factors.TRUCK_SMALL
        elif 'medium' in vehicle_type:
            return self.factors.TRUCK_MEDIUM
        elif 'large' in vehicle_type:
            return self.factors.TRUCK_LARGE
        elif 'van' in vehicle_type:
            return self.factors.VAN
        else:
            return self.factors.DEFAULT
    
    def _calculate_equivalent_metrics(self, emissions_kg: float) -> Dict[str, float]:
        """Calculate equivalent environmental metrics matching frontend"""
        # Conversion factors (same as frontend)
        KM_DRIVEN_PER_KG_CO2 = 10.0  # Average car emits ~0.2 kg CO2 per km
        TREES_PER_KG_CO2_YEAR = 0.02  # One tree absorbs ~50 kg CO2 per year
        LITERS_GASOLINE_PER_KG_CO2 = 0.43  # 1L gasoline ≈ 2.3 kg CO2
        SMARTPHONE_CHARGES_PER_KG_CO2 = 121.0  # Based on average smartphone energy use
        
        return {
            "equivalent_km_driven": round(emissions_kg * KM_DRIVEN_PER_KG_CO2, 2),
            "equivalent_trees_year": round(emissions_kg * TREES_PER_KG_CO2_YEAR, 2),
            "equivalent_gasoline_liters": round(emissions_kg * LITERS_GASOLINE_PER_KG_CO2, 2),
            "equivalent_smartphone_charges": round(emissions_kg * SMARTPHONE_CHARGES_PER_KG_CO2, 2)
        }
    
    def calculate_savings(self, baseline_emissions: float, optimized_emissions: float) -> Dict[str, float]:
        """Calculate emission savings matching frontend metrics"""
        savings_kg = baseline_emissions - optimized_emissions
        savings_percentage = (savings_kg / baseline_emissions * 100) if baseline_emissions > 0 else 0
        
        return {
            "savings_kg": round(max(0, savings_kg), 2),
            "savings_percentage": round(max(0, savings_percentage), 1),
            "baseline_emissions": round(baseline_emissions, 2),
            "optimized_emissions": round(optimized_emissions, 2)
        }
    
    def validate_vehicle_capacity(self, assignments: Dict[str, List[str]], 
                                containers: List[Dict], vehicles: List[Dict]) -> Dict[str, List[str]]:
        """Validate assignments against vehicle capacities"""
        violations = {}
        container_lookup = {c['id']: c for c in containers}
        vehicle_lookup = {v['id']: v for v in vehicles}
        
        for vehicle_id, container_ids in assignments.items():
            vehicle = vehicle_lookup.get(vehicle_id)
            if not vehicle:
                continue
                
            total_weight = sum(container_lookup[cid]['weight'] for cid in container_ids)
            total_volume = sum(container_lookup[cid]['length'] * container_lookup[cid]['width'] * container_lookup[cid]['height'] 
                             for cid in container_ids)
            vehicle_volume = vehicle['length'] * vehicle['width'] * vehicle['height']
            
            vehicle_violations = []
            if total_weight > vehicle['max_weight']:
                vehicle_violations.append(f"Weight exceeded: {total_weight:.1f}kg > {vehicle['max_weight']}kg")
            if total_volume > vehicle_volume:
                vehicle_violations.append(f"Volume exceeded: {total_volume:.1f}m³ > {vehicle_volume:.1f}m³")
            
            if vehicle_violations:
                violations[vehicle_id] = vehicle_violations
        
        return violations