"""
Genetic Algorithm for Container Optimization
Implements a genetic algorithm to optimize 3D container packing.
"""

import random
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import copy

from backend.config.settings import Config
from backend.utils.logger import get_logger
from backend.algorithms.packing import PackingEngine, Placement

logger = get_logger(__name__)


@dataclass
class Individual:
    """
    Represents an individual solution in the genetic algorithm.
    An individual is a sequence of items and their orientations.
    """
    sequence: List[int]  # Item indices in packing order
    orientations: List[int]  # Orientation for each item (0-5 for 6 possible rotations)
    fitness: float = 0.0
    placements: List[Placement] = field(default_factory=list)
    utilization: float = 0.0
    is_valid: bool = True
    violations: List[str] = field(default_factory=list)
    
    def __lt__(self, other):
        """Compare individuals by fitness."""
        return self.fitness < other.fitness
    
    def copy(self):
        """Create a deep copy of this individual."""
        return Individual(
            sequence=self.sequence.copy(),
            orientations=self.orientations.copy(),
            fitness=self.fitness,
            placements=copy.deepcopy(self.placements),
            utilization=self.utilization,
            is_valid=self.is_valid,
            violations=self.violations.copy()
        )


class Population:
    """
    Manages a population of individuals for the genetic algorithm.
    """
    
    def __init__(self, size: int):
        """
        Initialize population.
        
        Args:
            size: Number of individuals in population
        """
        self.size = size
        self.individuals: List[Individual] = []
        self.generation = 0
        self.best_fitness = 0.0
        self.average_fitness = 0.0
        self.best_individual: Optional[Individual] = None
    
    def add(self, individual: Individual):
        """Add an individual to the population."""
        self.individuals.append(individual)
    
    def sort_by_fitness(self):
        """Sort population by fitness (descending)."""
        self.individuals.sort(key=lambda x: x.fitness, reverse=True)
        self.best_individual = self.individuals[0]
        self.best_fitness = self.best_individual.fitness
    
    def calculate_statistics(self):
        """Calculate population statistics."""
        if not self.individuals:
            return
        
        fitnesses = [ind.fitness for ind in self.individuals]
        self.average_fitness = sum(fitnesses) / len(fitnesses)
        self.best_fitness = max(fitnesses)
        
        # Update best individual
        for ind in self.individuals:
            if ind.fitness >= self.best_fitness:
                self.best_individual = ind
                break
    
    def get_elite(self, n: int) -> List[Individual]:
        """Get top n individuals."""
        self.sort_by_fitness()
        return self.individuals[:n]
    
    def tournament_selection(self, tournament_size: int) -> Individual:
        """
        Select individual using tournament selection.
        
        Args:
            tournament_size: Number of individuals in tournament
            
        Returns:
            Selected individual
        """
        tournament = random.sample(self.individuals, tournament_size)
        return max(tournament, key=lambda x: x.fitness)


class GeneticAlgorithm:
    """
    Genetic Algorithm implementation for 3D container packing optimization.
    """
    
    def __init__(self, container: Dict, items: List[Dict], config: Config = None):
        """
        Initialize genetic algorithm.
        
        Args:
            container: Container specifications
            items: List of items to pack
            config: Configuration object
        """
        self.container = container
        self.items = items
        self.config = config or Config()
        
        # GA parameters
        self.population_size = self.config.GA_POPULATION_SIZE
        self.generations = self.config.GA_GENERATIONS
        self.mutation_rate = self.config.GA_MUTATION_RATE
        self.crossover_rate = self.config.GA_CROSSOVER_RATE
        self.tournament_size = self.config.GA_TOURNAMENT_SIZE
        self.elite_size = self.config.GA_ELITE_SIZE
        
        # Initialize packing engine
        self.packing_engine = PackingEngine(container, items)
        
        # Statistics
        self.start_time = None
        self.end_time = None
        self.best_solution = None
        self.fitness_history = []
        
        logger.info(f"GA initialized with {len(items)} items, "
                   f"population={self.population_size}, generations={self.generations}")
    
    def run(self, max_time: int = None) -> Dict[str, Any]:
        """
        Run the genetic algorithm.
        
        Args:
            max_time: Maximum computation time in seconds
            
        Returns:
            Dictionary with optimization results
        """
        self.start_time = datetime.utcnow()
        max_time = max_time or self.config.MAX_COMPUTATION_TIME
        
        logger.info("Starting genetic algorithm optimization")
        
        # Initialize population
        population = self._initialize_population()
        
        # Evolution loop
        for generation in range(self.generations):
            # Check time limit
            if (datetime.utcnow() - self.start_time).total_seconds() > max_time:
                logger.warning(f"Time limit reached at generation {generation}")
                break
            
            # Evaluate fitness
            self._evaluate_population(population)
            
            # Update statistics
            population.calculate_statistics()
            self.fitness_history.append(population.best_fitness)
            
            logger.debug(f"Generation {generation}: "
                        f"Best={population.best_fitness:.4f}, "
                        f"Avg={population.average_fitness:.4f}")
            
            # Check convergence
            if self._check_convergence(generation):
                logger.info(f"Converged at generation {generation}")
                break
            
            # Create next generation
            population = self._evolve_population(population)
            population.generation = generation + 1
        
        # Final evaluation
        self._evaluate_population(population)
        population.sort_by_fitness()
        
        self.end_time = datetime.utcnow()
        self.best_solution = population.best_individual
        
        return self._format_results(population)
    
    def _initialize_population(self) -> Population:
        """
        Create initial population with random solutions.
        
        Returns:
            Initial population
        """
        population = Population(self.population_size)
        n_items = len(self.items)
        
        for _ in range(self.population_size):
            # Random sequence of item indices
            sequence = list(range(n_items))
            random.shuffle(sequence)
            
            # Random orientations (0-5 for 6 possible rotations)
            orientations = [random.randint(0, 5) for _ in range(n_items)]
            
            individual = Individual(sequence=sequence, orientations=orientations)
            population.add(individual)
        
        logger.info(f"Initialized population with {self.population_size} individuals")
        return population
    
    def _evaluate_population(self, population: Population):
        """
        Evaluate fitness for all individuals in population.
        
        Args:
            population: Population to evaluate
        """
        for individual in population.individuals:
            if individual.fitness == 0.0:  # Not yet evaluated
                self._evaluate_individual(individual)
    
    def _evaluate_individual(self, individual: Individual):
        """
        Evaluate fitness of an individual.
        
        Args:
            individual: Individual to evaluate
        """
        # Pack items according to sequence and orientations
        result = self.packing_engine.pack(
            sequence=individual.sequence,
            orientations=individual.orientations
        )
        
        # Store results
        individual.placements = result['placements']
        individual.utilization = result['utilization']
        individual.is_valid = result['is_valid']
        individual.violations = result['violations']
        
        # Calculate fitness
        individual.fitness = self._calculate_fitness(individual, result)
    
    def _calculate_fitness(self, individual: Individual, result: Dict) -> float:
        """
        Calculate fitness score for an individual.
        
        Args:
            individual: Individual to score
            result: Packing result dictionary
            
        Returns:
            Fitness score (0-1, higher is better)
        """
        # Weight components
        w_util = self.config.WEIGHT_UTILIZATION
        w_stab = self.config.WEIGHT_STABILITY
        w_cons = self.config.WEIGHT_CONSTRAINTS
        w_acc = self.config.WEIGHT_ACCESSIBILITY
        
        # Utilization score (0-1)
        utilization_score = result['utilization'] / 100.0
        
        # Stability score (center of gravity, weight distribution)
        stability_score = self._calculate_stability_score(result)
        
        # Constraint satisfaction score
        constraint_score = 1.0 if result['is_valid'] else 0.5
        constraint_score -= len(result['violations']) * 0.05
        constraint_score = max(0, constraint_score)
        
        # Accessibility score (items easy to unload)
        accessibility_score = self._calculate_accessibility_score(result)
        
        # Combined fitness
        fitness = (
            w_util * utilization_score +
            w_stab * stability_score +
            w_cons * constraint_score +
            w_acc * accessibility_score
        )
        
        return max(0, min(1, fitness))
    
    def _calculate_stability_score(self, result: Dict) -> float:
        """
        Calculate stability score based on center of gravity.
        
        Args:
            result: Packing result
            
        Returns:
            Stability score (0-1)
        """
        if not result['placements']:
            return 0.0
        
        container_center_z = self.container['height'] / 2
        
        # Calculate weighted center of gravity
        total_weight = 0
        weighted_z = 0
        
        for placement in result['placements']:
            item = self.items[placement.item_index]
            weight = item['weight']
            z_center = placement.z + placement.height / 2
            
            total_weight += weight
            weighted_z += weight * z_center
        
        if total_weight == 0:
            return 0.0
        
        cog_z = weighted_z / total_weight
        
        # Score: closer to bottom is better
        score = 1.0 - (cog_z / self.container['height'])
        
        # Penalty for high COG
        if cog_z > container_center_z:
            score *= 0.8
        
        return max(0, min(1, score))
    
    def _calculate_accessibility_score(self, result: Dict) -> float:
        """
        Calculate accessibility score (ease of unloading).
        
        Args:
            result: Packing result
            
        Returns:
            Accessibility score (0-1)
        """
        if not result['placements']:
            return 0.0
        
        # Count items that are not blocked
        accessible = 0
        total = len(result['placements'])
        
        for i, placement in enumerate(result['placements']):
            # Check if any other item is directly on top
            blocked = False
            for j, other in enumerate(result['placements']):
                if i != j and self._is_on_top(other, placement):
                    blocked = True
                    break
            
            if not blocked:
                accessible += 1
        
        return accessible / total if total > 0 else 0.0
    
    def _is_on_top(self, top: Placement, bottom: Placement) -> bool:
        """Check if top placement is directly on top of bottom placement."""
        # Check if bottom of top is at top of bottom
        if abs(top.z - (bottom.z + bottom.height)) > 1:
            return False
        
        # Check horizontal overlap
        x_overlap = (top.x < bottom.x + bottom.length and 
                    top.x + top.length > bottom.x)
        y_overlap = (top.y < bottom.y + bottom.width and 
                    top.y + top.width > bottom.y)
        
        return x_overlap and y_overlap
    
    def _evolve_population(self, population: Population) -> Population:
        """
        Create next generation through selection, crossover, and mutation.
        
        Args:
            population: Current population
            
        Returns:
            New population
        """
        new_population = Population(self.population_size)
        
        # Elitism: keep best individuals
        elite = population.get_elite(self.elite_size)
        for individual in elite:
            new_population.add(individual.copy())
        
        # Fill rest of population
        while len(new_population.individuals) < self.population_size:
            # Selection
            parent1 = population.tournament_selection(self.tournament_size)
            parent2 = population.tournament_selection(self.tournament_size)
            
            # Crossover
            if random.random() < self.crossover_rate:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()
            
            # Mutation
            if random.random() < self.mutation_rate:
                self._mutate(child1)
            if random.random() < self.mutation_rate:
                self._mutate(child2)
            
            # Add children
            new_population.add(child1)
            if len(new_population.individuals) < self.population_size:
                new_population.add(child2)
        
        return new_population
    
    def _crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """
        Perform order crossover (OX) for sequences.
        
        Args:
            parent1: First parent
            parent2: Second parent
            
        Returns:
            Two offspring
        """
        n = len(parent1.sequence)
        
        # Order crossover for sequence
        point1, point2 = sorted(random.sample(range(n), 2))
        
        # Child 1
        child1_seq = [-1] * n
        child1_seq[point1:point2] = parent1.sequence[point1:point2]
        
        pos = point2
        for item in parent2.sequence[point2:] + parent2.sequence[:point2]:
            if item not in child1_seq:
                if pos >= n:
                    pos = 0
                child1_seq[pos] = item
                pos += 1
        
        # Child 2
        child2_seq = [-1] * n
        child2_seq[point1:point2] = parent2.sequence[point1:point2]
        
        pos = point2
        for item in parent1.sequence[point2:] + parent1.sequence[:point2]:
            if item not in child2_seq:
                if pos >= n:
                    pos = 0
                child2_seq[pos] = item
                pos += 1
        
        # Uniform crossover for orientations
        child1_orient = []
        child2_orient = []
        for o1, o2 in zip(parent1.orientations, parent2.orientations):
            if random.random() < 0.5:
                child1_orient.append(o1)
                child2_orient.append(o2)
            else:
                child1_orient.append(o2)
                child2_orient.append(o1)
        
        child1 = Individual(sequence=child1_seq, orientations=child1_orient)
        child2 = Individual(sequence=child2_seq, orientations=child2_orient)
        
        return child1, child2
    
    def _mutate(self, individual: Individual):
        """
        Apply mutation operators to an individual.
        
        Args:
            individual: Individual to mutate
        """
        n = len(individual.sequence)
        
        # Swap mutation for sequence
        if random.random() < 0.5:
            i, j = random.sample(range(n), 2)
            individual.sequence[i], individual.sequence[j] = \
                individual.sequence[j], individual.sequence[i]
        
        # Flip mutation for orientations
        if random.random() < 0.5:
            i = random.randint(0, n - 1)
            individual.orientations[i] = random.randint(0, 5)
        
        # Reset fitness
        individual.fitness = 0.0
    
    def _check_convergence(self, generation: int) -> bool:
        """
        Check if algorithm has converged.
        
        Args:
            generation: Current generation number
            
        Returns:
            True if converged
        """
        if generation < 10:
            return False
        
        # Check if fitness hasn't improved in last 10 generations
        recent_fitness = self.fitness_history[-10:]
        if len(set(recent_fitness)) == 1:
            return True
        
        # Check if improvement is very small
        if abs(recent_fitness[-1] - recent_fitness[0]) < 0.001:
            return True
        
        return False
    
    def _format_results(self, population: Population) -> Dict[str, Any]:
        """
        Format optimization results.
        
        Args:
            population: Final population
            
        Returns:
            Results dictionary
        """
        best = population.best_individual
        
        computation_time = (self.end_time - self.start_time).total_seconds()
        
        return {
            'status': 'completed',
            'algorithm': 'genetic_algorithm',
            'best_fitness': best.fitness,
            'utilization': best.utilization,
            'placements': best.placements,
            'is_valid': best.is_valid,
            'violations': best.violations,
            'generations': population.generation,
            'computation_time': computation_time,
            'fitness_history': self.fitness_history,
            'population_size': self.population_size,
            'items_packed': len(best.placements),
            'items_unpacked': len(self.items) - len(best.placements)
        }