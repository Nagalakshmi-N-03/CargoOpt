"""
Emission Calculator Service
Calculates carbon footprint and environmental impact metrics.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math

from backend.config.settings import Config
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class EmissionFactors:
    """Standard emission factors for transportation."""
    
    # CO2 emissions in kg per ton-km
    TRUCK_EMISSION_FACTOR = 0.062  # kg CO2 per ton-km
    SHIP_EMISSION_FACTOR = 0.008   # kg CO2 per ton-km
    RAIL_EMISSION_FACTOR = 0.022   # kg CO2 per ton-km
    AIR_EMISSION_FACTOR = 0.602    # kg CO2 per ton-km
    
    # Fuel consumption factors (liters per 100 km)
    TRUCK_FUEL_CONSUMPTION = 30    # L/100km for loaded truck
    SHIP_FUEL_CONSUMPTION = 150    # kg/nautical mile for container ship
    
    # CO2 per liter of fuel
    DIESEL_CO2_PER_LITER = 2.68    # kg CO2 per liter


class FuelEfficiencyCalculator:
    """Calculates fuel efficiency metrics."""
    
    @staticmethod
    def calculate_truck_fuel_consumption(
        distance_km: float,
        cargo_weight_kg: float,
        utilization: float
    ) -> Dict[str, float]:
        """
        Calculate truck fuel consumption.
        
        Args:
            distance_km: Distance in kilometers
            cargo_weight_kg: Cargo weight in kg
            utilization: Container utilization (0-1)
            
        Returns:
            Dictionary with fuel metrics
        """
        # Base consumption
        base_consumption = EmissionFactors.TRUCK_FUEL_CONSUMPTION
        
        # Adjust for load (empty truck uses ~70% fuel of full truck)
        load_factor = 0.7 + (0.3 * utilization)
        fuel_per_100km = base_consumption * load_factor
        
        # Total fuel
        total_fuel = (distance_km / 100) * fuel_per_100km
        
        # Fuel efficiency (ton-km per liter)
        cargo_tons = cargo_weight_kg / 1000
        efficiency = (cargo_tons * distance_km) / total_fuel if total_fuel > 0 else 0
        
        return {
            'fuel_consumption_liters': round(total_fuel, 2),
            'fuel_per_100km': round(fuel_per_100km, 2),
            'efficiency_ton_km_per_liter': round(efficiency, 2),
            'distance_km': distance_km,
            'cargo_tons': round(cargo_tons, 2)
        }
    
    @staticmethod
    def calculate_ship_fuel_consumption(
        distance_nm: float,
        cargo_weight_kg: float,
        ship_capacity_teu: int = 5000
    ) -> Dict[str, float]:
        """
        Calculate ship fuel consumption.
        
        Args:
            distance_nm: Distance in nautical miles
            cargo_weight_kg: Cargo weight in kg
            ship_capacity_teu: Ship capacity in TEU
            
        Returns:
            Dictionary with fuel metrics
        """
        # Base consumption (kg fuel per nautical mile)
        base_consumption = EmissionFactors.SHIP_FUEL_CONSUMPTION
        
        # Scale by ship size
        size_factor = math.sqrt(ship_capacity_teu / 5000)
        fuel_per_nm = base_consumption * size_factor
        
        # Total fuel in kg
        total_fuel_kg = distance_nm * fuel_per_nm
        
        # Convert to liters (HFO density ~0.98 kg/L)
        total_fuel_liters = total_fuel_kg / 0.98
        
        cargo_tons = cargo_weight_kg / 1000
        efficiency = (cargo_tons * distance_nm) / total_fuel_liters if total_fuel_liters > 0 else 0
        
        return {
            'fuel_consumption_liters': round(total_fuel_liters, 2),
            'fuel_consumption_kg': round(total_fuel_kg, 2),
            'fuel_per_nm': round(fuel_per_nm, 2),
            'efficiency_ton_nm_per_liter': round(efficiency, 2),
            'distance_nm': distance_nm,
            'cargo_tons': round(cargo_tons, 2)
        }


class CarbonFootprintAnalyzer:
    """Analyzes carbon footprint of transportation."""
    
    @staticmethod
    def calculate_emissions(
        transport_mode: str,
        distance: float,
        cargo_weight_kg: float,
        utilization: float = 1.0
    ) -> Dict[str, float]:
        """
        Calculate CO2 emissions for transportation.
        
        Args:
            transport_mode: 'truck', 'ship', 'rail', or 'air'
            distance: Distance in km (or nm for ship)
            cargo_weight_kg: Cargo weight in kg
            utilization: Container utilization factor (0-1)
            
        Returns:
            Dictionary with emission metrics
        """
        cargo_tons = cargo_weight_kg / 1000
        
        # Select emission factor
        emission_factors = {
            'truck': EmissionFactors.TRUCK_EMISSION_FACTOR,
            'ship': EmissionFactors.SHIP_EMISSION_FACTOR,
            'rail': EmissionFactors.RAIL_EMISSION_FACTOR,
            'air': EmissionFactors.AIR_EMISSION_FACTOR
        }
        
        factor = emission_factors.get(transport_mode, EmissionFactors.TRUCK_EMISSION_FACTOR)
        
        # Calculate base emissions (ton-km)
        ton_km = cargo_tons * distance
        base_emissions = ton_km * factor
        
        # Adjust for utilization (better utilization = lower emissions per ton)
        utilization_factor = 1.0 / utilization if utilization > 0 else 1.0
        adjusted_emissions = base_emissions * utilization_factor
        
        # Calculate equivalent metrics
        trees_to_offset = adjusted_emissions / 21  # One tree absorbs ~21 kg CO2/year
        
        return {
            'co2_emissions_kg': round(adjusted_emissions, 2),
            'co2_emissions_tons': round(adjusted_emissions / 1000, 4),
            'ton_km': round(ton_km, 2),
            'emission_factor': factor,
            'transport_mode': transport_mode,
            'distance': distance,
            'utilization_factor': round(utilization, 2),
            'trees_to_offset': round(trees_to_offset, 1)
        }
    
    @staticmethod
    def calculate_utilization_impact(
        cargo_weight_kg: float,
        container_capacity_kg: float,
        current_utilization: float,
        improved_utilization: float,
        distance_km: float,
        transport_mode: str = 'truck'
    ) -> Dict[str, float]:
        """
        Calculate emission savings from improved utilization.
        
        Args:
            cargo_weight_kg: Cargo weight
            container_capacity_kg: Container capacity
            current_utilization: Current space utilization (0-1)
            improved_utilization: Improved space utilization (0-1)
            distance_km: Distance
            transport_mode: Transportation mode
            
        Returns:
            Dictionary with savings metrics
        """
        # Current emissions
        current = CarbonFootprintAnalyzer.calculate_emissions(
            transport_mode, distance_km, cargo_weight_kg, current_utilization
        )
        
        # Improved emissions
        improved = CarbonFootprintAnalyzer.calculate_emissions(
            transport_mode, distance_km, cargo_weight_kg, improved_utilization
        )
        
        # Savings
        emissions_saved = current['co2_emissions_kg'] - improved['co2_emissions_kg']
        percentage_saved = (emissions_saved / current['co2_emissions_kg']) * 100 if current['co2_emissions_kg'] > 0 else 0
        
        return {
            'current_emissions_kg': current['co2_emissions_kg'],
            'improved_emissions_kg': improved['co2_emissions_kg'],
            'emissions_saved_kg': round(emissions_saved, 2),
            'percentage_saved': round(percentage_saved, 2),
            'current_utilization': round(current_utilization * 100, 2),
            'improved_utilization': round(improved_utilization * 100, 2),
            'utilization_improvement': round((improved_utilization - current_utilization) * 100, 2)
        }


class EmissionCalculator:
    """
    Main emission calculator service.
    """
    
    def __init__(self, config: Config = None):
        """
        Initialize emission calculator.
        
        Args:
            config: Configuration object
        """
        self.config = config or Config()
        self.fuel_calculator = FuelEfficiencyCalculator()
        self.carbon_analyzer = CarbonFootprintAnalyzer()
        
        logger.info("EmissionCalculator initialized")
    
    def calculate_optimization_impact(
        self,
        container: Dict,
        placements: List,
        distance_km: float = 1000,
        transport_mode: str = 'truck'
    ) -> Dict[str, any]:
        """
        Calculate environmental impact of an optimization result.
        
        Args:
            container: Container specifications
            placements: List of placements
            distance_km: Transportation distance
            transport_mode: Mode of transport
            
        Returns:
            Dictionary with environmental metrics
        """
        # Calculate utilization
        container_volume = container['length'] * container['width'] * container['height']
        used_volume = sum(
            p.length * p.width * p.height if hasattr(p, 'length') else 0
            for p in placements
        )
        utilization = used_volume / container_volume if container_volume > 0 else 0
        
        # Calculate total weight
        total_weight = sum(
            p.weight if hasattr(p, 'weight') else 0
            for p in placements
        )
        
        # Calculate emissions
        emissions = self.carbon_analyzer.calculate_emissions(
            transport_mode, distance_km, total_weight, utilization
        )
        
        # Calculate fuel consumption
        if transport_mode == 'truck':
            fuel_metrics = self.fuel_calculator.calculate_truck_fuel_consumption(
                distance_km, total_weight, utilization
            )
        elif transport_mode == 'ship':
            distance_nm = distance_km * 0.539957  # km to nautical miles
            fuel_metrics = self.fuel_calculator.calculate_ship_fuel_consumption(
                distance_nm, total_weight
            )
        else:
            fuel_metrics = {}
        
        # Calculate cost (approximate)
        fuel_cost_per_liter = 1.5  # USD per liter (approximate)
        fuel_cost = fuel_metrics.get('fuel_consumption_liters', 0) * fuel_cost_per_liter
        
        return {
            'emissions': emissions,
            'fuel': fuel_metrics,
            'cost_estimate_usd': round(fuel_cost, 2),
            'utilization_percentage': round(utilization * 100, 2),
            'environmental_rating': self._calculate_rating(utilization, emissions['co2_emissions_kg'])
        }
    
    def compare_scenarios(
        self,
        scenario1: Dict,
        scenario2: Dict,
        distance_km: float = 1000,
        transport_mode: str = 'truck'
    ) -> Dict[str, any]:
        """
        Compare environmental impact of two optimization scenarios.
        
        Args:
            scenario1: First scenario (container, placements)
            scenario2: Second scenario (container, placements)
            distance_km: Transportation distance
            transport_mode: Mode of transport
            
        Returns:
            Comparison metrics
        """
        impact1 = self.calculate_optimization_impact(
            scenario1['container'],
            scenario1['placements'],
            distance_km,
            transport_mode
        )
        
        impact2 = self.calculate_optimization_impact(
            scenario2['container'],
            scenario2['placements'],
            distance_km,
            transport_mode
        )
        
        emissions_diff = impact1['emissions']['co2_emissions_kg'] - impact2['emissions']['co2_emissions_kg']
        fuel_diff = impact1['fuel'].get('fuel_consumption_liters', 0) - impact2['fuel'].get('fuel_consumption_liters', 0)
        
        return {
            'scenario1': impact1,
            'scenario2': impact2,
            'comparison': {
                'emissions_difference_kg': round(emissions_diff, 2),
                'fuel_difference_liters': round(fuel_diff, 2),
                'cost_difference_usd': round(impact1['cost_estimate_usd'] - impact2['cost_estimate_usd'], 2),
                'better_scenario': 'scenario2' if emissions_diff > 0 else 'scenario1',
                'improvement_percentage': round(abs(emissions_diff / impact1['emissions']['co2_emissions_kg']) * 100, 2) if impact1['emissions']['co2_emissions_kg'] > 0 else 0
            }
        }
    
    def calculate_annual_savings(
        self,
        current_utilization: float,
        improved_utilization: float,
        shipments_per_year: int,
        avg_distance_km: float,
        avg_weight_kg: float,
        transport_mode: str = 'truck'
    ) -> Dict[str, float]:
        """
        Calculate annual environmental and cost savings.
        
        Args:
            current_utilization: Current average utilization
            improved_utilization: Improved utilization with optimization
            shipments_per_year: Number of shipments per year
            avg_distance_km: Average distance per shipment
            avg_weight_kg: Average cargo weight
            transport_mode: Transportation mode
            
        Returns:
            Annual savings metrics
        """
        # Single shipment savings
        single_savings = self.carbon_analyzer.calculate_utilization_impact(
            avg_weight_kg,
            avg_weight_kg / current_utilization if current_utilization > 0 else avg_weight_kg,
            current_utilization,
            improved_utilization,
            avg_distance_km,
            transport_mode
        )
        
        # Annual totals
        annual_emissions_saved = single_savings['emissions_saved_kg'] * shipments_per_year
        
        # Cost savings (approximate)
        fuel_saved_liters = (single_savings['current_emissions_kg'] - single_savings['improved_emissions_kg']) / EmissionFactors.DIESEL_CO2_PER_LITER
        annual_fuel_saved = fuel_saved_liters * shipments_per_year
        fuel_cost_per_liter = 1.5
        annual_cost_saved = annual_fuel_saved * fuel_cost_per_liter
        
        # Equivalent metrics
        trees_needed = annual_emissions_saved / 21
        cars_equivalent = annual_emissions_saved / 4600  # Average car emits ~4.6 tons CO2/year
        
        return {
            'annual_emissions_saved_kg': round(annual_emissions_saved, 2),
            'annual_emissions_saved_tons': round(annual_emissions_saved / 1000, 2),
            'annual_fuel_saved_liters': round(annual_fuel_saved, 2),
            'annual_cost_saved_usd': round(annual_cost_saved, 2),
            'trees_equivalent': round(trees_needed, 1),
            'cars_removed_equivalent': round(cars_equivalent, 2),
            'shipments_per_year': shipments_per_year,
            'utilization_improvement': round((improved_utilization - current_utilization) * 100, 2)
        }
    
    def _calculate_rating(self, utilization: float, emissions_kg: float) -> str:
        """
        Calculate environmental rating.
        
        Args:
            utilization: Space utilization (0-1)
            emissions_kg: CO2 emissions
            
        Returns:
            Rating string (A+ to F)
        """
        # Rate based on utilization
        if utilization >= 0.9:
            return 'A+'
        elif utilization >= 0.8:
            return 'A'
        elif utilization >= 0.7:
            return 'B'
        elif utilization >= 0.6:
            return 'C'
        elif utilization >= 0.5:
            return 'D'
        elif utilization >= 0.4:
            return 'E'
        else:
            return 'F'
    
    def generate_sustainability_report(
        self,
        optimization_result: Dict,
        distance_km: float = 1000,
        transport_mode: str = 'truck',
        baseline_utilization: float = 0.65
    ) -> Dict[str, any]:
        """
        Generate comprehensive sustainability report.
        
        Args:
            optimization_result: Optimization result with container and placements
            distance_km: Transportation distance
            transport_mode: Mode of transport
            baseline_utilization: Baseline utilization for comparison
            
        Returns:
            Comprehensive sustainability report
        """
        container = optimization_result.get('container', {})
        placements = optimization_result.get('placements', [])
        utilization = optimization_result.get('utilization', 0) / 100
        
        # Current impact
        current_impact = self.calculate_optimization_impact(
            container, placements, distance_km, transport_mode
        )
        
        # Baseline comparison
        total_weight = sum(p.weight if hasattr(p, 'weight') else 0 for p in placements)
        baseline_emissions = self.carbon_analyzer.calculate_emissions(
            transport_mode, distance_km, total_weight, baseline_utilization
        )
        
        improvement = self.carbon_analyzer.calculate_utilization_impact(
            total_weight,
            total_weight / baseline_utilization if baseline_utilization > 0 else total_weight,
            baseline_utilization,
            utilization,
            distance_km,
            transport_mode
        )
        
        return {
            'current_performance': current_impact,
            'baseline_comparison': {
                'baseline_utilization': round(baseline_utilization * 100, 2),
                'baseline_emissions_kg': baseline_emissions['co2_emissions_kg'],
                'improvement': improvement
            },
            'recommendations': self._generate_recommendations(utilization, current_impact),
            'report_date': datetime.now().isoformat()
        }
    
    def _generate_recommendations(self, utilization: float, impact: Dict) -> List[str]:
        """Generate sustainability recommendations."""
        recommendations = []
        
        if utilization < 0.7:
            recommendations.append(
                f"Space utilization is at {utilization*100:.1f}%. "
                "Consider consolidating shipments to improve efficiency."
            )
        
        if utilization < 0.8:
            recommendations.append(
                "Optimizing packing can reduce CO2 emissions by up to "
                f"{(0.8 - utilization) * 100:.1f}%."
            )
        
        rating = impact.get('environmental_rating', 'C')
        if rating in ['D', 'E', 'F']:
            recommendations.append(
                "Current environmental rating is " + rating + ". "
                "Significant improvements possible through better optimization."
            )
        
        if impact['emissions']['co2_emissions_kg'] > 1000:
            recommendations.append(
                "Consider rail or sea transport for long distances to reduce emissions."
            )
        
        return recommendations