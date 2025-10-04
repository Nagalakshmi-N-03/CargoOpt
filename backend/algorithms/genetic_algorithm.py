import logging
import random
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import copy

logger = logging.getLogger(__name__)

@dataclass
class Chromosome:
    placements: List
    fitness: float = 0.0

class GeneticAlgorithm:
    def __init__(self, population_size: int = 50, mutation_rate: float = 0.1):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.name = "Genetic Algorithm"
        self.logger = logging.getLogger(__name__)
    
    def optimize(self, container_data: Dict, items_data: List[Dict], generations: int = 100) -> Dict:
        """
        Optimize packing using genetic algorithm
        """
        try:
            # Initialize population
            population = self._initialize_population(container_data, items_data)
            
            best_solution = None
            
            for generation in range(generations):
                # Evaluate fitness
                for chromosome in population:
                    chromosome.fitness = self._calculate_fitness(chromosome, container_data)
                
                # Sort by fitness
                population.sort(key=lambda x: x.fitness, reverse=True)
                
                # Keep best solution
                if best_solution is None or population[0].fitness > best_solution.fitness:
                    best_solution = copy.deepcopy(population[0])
                
                # Create new generation
                new_population = [copy.deepcopy(population[0])]  # Elitism
                
                while len(new_population) < self.population_size:
                    # Selection
                    parent1 = self._tournament_selection(population)
                    parent2 = self._tournament_selection(population)
                    
                    # Crossover
                    child = self._crossover(parent1, parent2)
                    
                    # Mutation
                    if random.random() < self.mutation_rate:
                        child = self._mutate(child, container_data, items_data)
                    
                    new_population.append(child)
                
                population = new_population
            
            # Calculate final metrics
            metrics = self._calculate_metrics(best_solution, container_data)
            
            return {
                'placements': [
                    {
                        'item_id': p['item_id'],
                        'position': p['position'],
                        'dimensions': p['dimensions'],
                        'rotated': p.get('rotated', False)
                    }
                    for p in best_solution.placements
                ],
                'metrics': metrics,
                'algorithm': self.name,
                'generations': generations
            }
            
        except Exception as e:
            self.logger.error(f"Genetic algorithm optimization failed: {str(e)}")
            raise
    
    def _initialize_population(self, container: Dict, items: List[Dict]) -> List[Chromosome]:
        """Initialize random population"""
        population = []
        
        for _ in range(self.population_size):
            placements = []
            used_positions = set()
            
            # Shuffle items for random order
            shuffled_items = items.copy()
            random.shuffle(shuffled_items)
            
            for item in shuffled_items:
                for _ in range(item.get('quantity', 1)):
                    placement = self._create_random_placement(item, container, used_positions)
                    if placement:
                        placements.append(placement)
                        # Mark position as used (simplified)
                        pos_key = (placement['position'][0], placement['position'][1], placement['position'][2])
                        used_positions.add(pos_key)
            
            population.append(Chromosome(placements))
        
        return population
    
    def _create_random_placement(self, item: Dict, container: Dict, used_positions: set) -> Optional[Dict]:
        """Create a random valid placement for an item"""
        max_attempts = 10
        
        for _ in range(max_attempts):
            # Random position
            x = random.uniform(0, container['length'] - item['length'])
            y = random.uniform(0, container['width'] - item['width'])
            z = random.uniform(0, container['height'] - item['height'])
            
            # Check if position is available (simplified collision detection)
            pos_key = (round(x, 2), round(y, 2), round(z, 2))
            if pos_key not in used_positions:
                return {
                    'item_id': item['id'],
                    'position': [x, y, z],
                    'dimensions': [item['length'], item['width'], item['height']],
                    'rotated': False
                }
        
        return None
    
    def _calculate_fitness(self, chromosome: Chromosome, container: Dict) -> float:
        """Calculate fitness score for a chromosome"""
        if not chromosome.placements:
            return 0.0
        
        total_volume = container['length'] * container['width'] * container['height']
        used_volume = 0
        used_weight = 0
        
        for placement in chromosome.placements:
            dims = placement['dimensions']
            used_volume += dims[0] * dims[1] * dims[2]
            # Note: Weight would need to be tracked per item
        
        # Basic fitness: volume utilization
        volume_utilization = used_volume / total_volume if total_volume > 0 else 0
        
        # Penalize overlaps (simplified)
        overlap_penalty = self._calculate_overlap_penalty(chromosome.placements)
        
        fitness = volume_utilization * (1 - overlap_penalty)
        
        return max(0.0, fitness)
    
    def _calculate_overlap_penalty(self, placements: List[Dict]) -> float:
        """Calculate penalty for overlapping items (simplified)"""
        if len(placements) <= 1:
            return 0.0
        
        overlaps = 0
        total_pairs = len(placements) * (len(placements) - 1) / 2
        
        for i in range(len(placements)):
            for j in range(i + 1, len(placements)):
                if self._check_overlap(placements[i], placements[j]):
                    overlaps += 1
        
        return overlaps / total_pairs if total_pairs > 0 else 0.0
    
    def _check_overlap(self, item1: Dict, item2: Dict) -> bool:
        """Check if two items overlap"""
        pos1, dims1 = item1['position'], item1['dimensions']
        pos2, dims2 = item2['position'], item2['dimensions']
        
        # Check overlap in all dimensions
        overlap_x = (pos1[0] < pos2[0] + dims2[0]) and (pos1[0] + dims1[0] > pos2[0])
        overlap_y = (pos1[1] < pos2[1] + dims2[1]) and (pos1[1] + dims1[1] > pos2[1])
        overlap_z = (pos1[2] < pos2[2] + dims2[2]) and (pos1[2] + dims1[2] > pos2[2])
        
        return overlap_x and overlap_y and overlap_z
    
    def _tournament_selection(self, population: List[Chromosome], tournament_size: int = 3) -> Chromosome:
        """Select a chromosome using tournament selection"""
        tournament = random.sample(population, tournament_size)
        return max(tournament, key=lambda x: x.fitness)
    
    def _crossover(self, parent1: Chromosome, parent2: Chromosome) -> Chromosome:
        """Perform crossover between two parents"""
        # Simple one-point crossover
        crossover_point = random.randint(0, min(len(parent1.placements), len(parent2.placements)))
        
        child_placements = (
            parent1.placements[:crossover_point] + 
            parent2.placements[crossover_point:]
        )
        
        return Chromosome(child_placements)
    
    def _mutate(self, chromosome: Chromosome, container: Dict, items: List[Dict]) -> Chromosome:
        """Mutate a chromosome"""
        if not chromosome.placements:
            return chromosome
        
        mutated = copy.deepcopy(chromosome)
        
        # Randomly change position of one item
        mutation_index = random.randint(0, len(mutated.placements) - 1)
        item_to_mutate = mutated.placements[mutation_index]
        
        # Find corresponding item data
        item_data = next((item for item in items if item['id'] == item_to_mutate['item_id']), None)
        
        if item_data:
            # Create new random position
            new_x = random.uniform(0, container['length'] - item_data['length'])
            new_y = random.uniform(0, container['width'] - item_data['width'])
            new_z = random.uniform(0, container['height'] - item_data['height'])
            
            mutated.placements[mutation_index]['position'] = [new_x, new_y, new_z]
        
        return mutated
    
    def _calculate_metrics(self, chromosome: Chromosome, container: Dict) -> Dict:
        """Calculate final metrics for the solution"""
        total_volume = container['length'] * container['width'] * container['height']
        used_volume = 0
        
        for placement in chromosome.placements:
            dims = placement['dimensions']
            used_volume += dims[0] * dims[1] * dims[2]
        
        utilization_rate = used_volume / total_volume if total_volume > 0 else 0
        
        return {
            'utilization_rate': round(utilization_rate, 4),
            'total_items_packed': len(chromosome.placements),
            'total_volume_used': round(used_volume, 2),
            'container_volume': round(total_volume, 2),
            'container_max_weight': container.get('max_weight', 0)
        }