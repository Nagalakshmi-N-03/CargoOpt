"""
Algorithm Tests
Tests for optimization algorithms (Genetic Algorithm, Constraint Solver, Packing)
"""

import pytest
from backend.algorithms.genetic_algorithm import GeneticAlgorithm, Individual, Population
from backend.algorithms.constraint_solver import ConstraintSolver, Constraint
from backend.algorithms.packing import PackingEngine, Placement, PackingHeuristic


# ============================================================================
# Genetic Algorithm Tests
# ============================================================================

@pytest.mark.algorithms
@pytest.mark.unit
class TestGeneticAlgorithm:
    """Test genetic algorithm optimization."""
    
    def test_ga_initialization(self, genetic_algorithm):
        """Test GA initialization."""
        assert genetic_algorithm.population_size > 0
        assert genetic_algorithm.generations > 0
        assert 0 < genetic_algorithm.mutation_rate < 1
        assert 0 < genetic_algorithm.crossover_rate < 1
    
    def test_create_individual(self, genetic_algorithm):
        """Test individual creation."""
        n_items = len(genetic_algorithm.items)
        individual = Individual(
            sequence=list(range(n_items)),
            orientations=[0] * n_items
        )
        
        assert len(individual.sequence) == n_items
        assert len(individual.orientations) == n_items
        assert individual.fitness == 0.0
    
    def test_initialize_population(self, genetic_algorithm):
        """Test population initialization."""
        population = genetic_algorithm._initialize_population()
        
        assert len(population.individuals) == genetic_algorithm.population_size
        assert population.generation == 0
        
        # Check diversity - sequences should be different
        sequences = [tuple(ind.sequence) for ind in population.individuals]
        assert len(set(sequences)) > 1
    
    def test_evaluate_individual(self, genetic_algorithm):
        """Test individual fitness evaluation."""
        individual = Individual(
            sequence=list(range(len(genetic_algorithm.items))),
            orientations=[0] * len(genetic_algorithm.items)
        )
        
        genetic_algorithm._evaluate_individual(individual)
        
        assert 0 <= individual.fitness <= 1
        assert len(individual.placements) >= 0
    
    def test_crossover(self, genetic_algorithm):
        """Test crossover operation."""
        n_items = len(genetic_algorithm.items)
        parent1 = Individual(
            sequence=list(range(n_items)),
            orientations=[0] * n_items
        )
        parent2 = Individual(
            sequence=list(reversed(range(n_items))),
            orientations=[1] * n_items
        )
        
        child1, child2 = genetic_algorithm._crossover(parent1, parent2)
        
        # Children should have valid sequences
        assert len(child1.sequence) == n_items
        assert len(child2.sequence) == n_items
        assert set(child1.sequence) == set(range(n_items))
        assert set(child2.sequence) == set(range(n_items))
    
    def test_mutation(self, genetic_algorithm):
        """Test mutation operation."""
        n_items = len(genetic_algorithm.items)
        individual = Individual(
            sequence=list(range(n_items)),
            orientations=[0] * n_items
        )
        original_sequence = individual.sequence.copy()
        
        genetic_algorithm._mutate(individual)
        
        # Sequence should still be valid
        assert len(individual.sequence) == n_items
        assert set(individual.sequence) == set(range(n_items))
    
    @pytest.mark.slow
    def test_ga_optimization_run(self, genetic_algorithm):
        """Test complete GA optimization run."""
        result = genetic_algorithm.run(max_time=10)
        
        assert result['status'] == 'completed'
        assert 'utilization' in result
        assert 'placements' in result
        assert result['items_packed'] <= result['items_unpacked'] + len(genetic_algorithm.items)


# ============================================================================
# Constraint Solver Tests
# ============================================================================

@pytest.mark.algorithms
@pytest.mark.unit
class TestConstraintSolver:
    """Test constraint programming solver."""
    
    def test_cs_initialization(self, constraint_solver):
        """Test constraint solver initialization."""
        assert len(constraint_solver.hard_constraints) > 0
        assert len(constraint_solver.soft_constraints) >= 0
        assert len(constraint_solver.items) > 0
    
    def test_within_container_constraint(self, constraint_solver):
        """Test within container constraint."""
        placement = Placement(
            item_index=0,
            x=0,
            y=0,
            z=0,
            length=1000,
            width=800,
            height=600,
            weight=50
        )
        
        result = constraint_solver._check_within_container(placement, [])
        assert result is True
        
        # Test invalid placement
        invalid_placement = Placement(
            item_index=0,
            x=constraint_solver.container['length'],  # Outside
            y=0,
            z=0,
            length=1000,
            width=800,
            height=600,
            weight=50
        )
        
        result = constraint_solver._check_within_container(invalid_placement, [])
        assert result is False
    
    def test_no_overlap_constraint(self, constraint_solver):
        """Test no overlap constraint."""
        placement1 = Placement(
            item_index=0,
            x=0,
            y=0,
            z=0,
            length=1000,
            width=800,
            height=600,
            weight=50
        )
        
        # Non-overlapping placement
        placement2 = Placement(
            item_index=1,
            x=1500,
            y=0,
            z=0,
            length=1000,
            width=800,
            height=600,
            weight=50
        )
        
        result = constraint_solver._check_no_overlap(placement2, [placement1])
        assert result is True
        
        # Overlapping placement
        placement3 = Placement(
            item_index=2,
            x=500,  # Overlaps with placement1
            y=0,
            z=0,
            length=1000,
            width=800,
            height=600,
            weight=50
        )
        
        result = constraint_solver._check_no_overlap(placement3, [placement1])
        assert result is False
    
    def test_weight_limit_constraint(self, constraint_solver):
        """Test weight limit constraint."""
        placement = Placement(
            item_index=0,
            x=0,
            y=0,
            z=0,
            length=1000,
            width=800,
            height=600,
            weight=constraint_solver.container['max_weight'] - 100
        )
        
        result = constraint_solver._check_weight_limit(placement, [])
        assert result is True
        
        # Exceed weight limit
        heavy_placement = Placement(
            item_index=1,
            x=0,
            y=0,
            z=0,
            length=1000,
            width=800,
            height=600,
            weight=constraint_solver.container['max_weight']
        )
        
        result = constraint_solver._check_weight_limit(heavy_placement, [placement])
        assert result is False
    
    @pytest.mark.slow
    def test_solver_optimization(self, constraint_solver):
        """Test constraint solver optimization."""
        result = constraint_solver.solve(max_time=10)
        
        assert result['status'] == 'completed'
        assert 'utilization' in result
        assert 'placements' in result


# ============================================================================
# Packing Engine Tests
# ============================================================================

@pytest.mark.algorithms
@pytest.mark.unit
class TestPackingEngine:
    """Test packing engine."""
    
    def test_packing_engine_initialization(self, packing_engine):
        """Test packing engine initialization."""
        assert packing_engine.container is not None
        assert len(packing_engine.items) > 0
        assert len(packing_engine.available_spaces) == 1
    
    def test_placement_creation(self, packing_engine):
        """Test placement object creation."""
        placement = Placement(
            item_index=0,
            x=0,
            y=0,
            z=0,
            length=1000,
            width=800,
            height=600,
            weight=50
        )
        
        assert placement.x == 0
        assert placement.volume == 1000 * 800 * 600
        
        # Test bounds
        min_bound, max_bound = placement.get_bounds()
        assert min_bound == (0, 0, 0)
        assert max_bound == (1000, 800, 600)
    
    def test_placement_overlap_detection(self, packing_engine):
        """Test overlap detection."""
        placement1 = Placement(
            item_index=0,
            x=0,
            y=0,
            z=0,
            length=1000,
            width=800,
            height=600,
            weight=50
        )
        
        # Non-overlapping
        placement2 = Placement(
            item_index=1,
            x=2000,
            y=0,
            z=0,
            length=1000,
            width=800,
            height=600,
            weight=50
        )
        assert not placement1.overlaps(placement2)
        
        # Overlapping
        placement3 = Placement(
            item_index=2,
            x=500,
            y=400,
            z=300,
            length=1000,
            width=800,
            height=600,
            weight=50
        )
        assert placement1.overlaps(placement3)
    
    def test_best_fit_heuristic(self, packing_engine):
        """Test best-fit packing heuristic."""
        sequence = list(range(len(packing_engine.items)))
        orientations = [0] * len(packing_engine.items)
        
        result = packing_engine.pack(
            sequence,
            orientations,
            heuristic=PackingHeuristic.BEST_FIT
        )
        
        assert 'placements' in result
        assert 'utilization' in result
        assert result['utilization'] >= 0
    
    def test_bottom_left_heuristic(self, packing_engine):
        """Test bottom-left packing heuristic."""
        sequence = list(range(len(packing_engine.items)))
        orientations = [0] * len(packing_engine.items)
        
        result = packing_engine.pack(
            sequence,
            orientations,
            heuristic=PackingHeuristic.BOTTOM_LEFT
        )
        
        assert 'placements' in result
        # Bottom-left should place items low
        if result['placements']:
            assert all(p.z == 0 for p in result['placements'][:3])  # First few on floor
    
    def test_utilization_calculation(self, packing_engine):
        """Test space utilization calculation."""
        sequence = list(range(len(packing_engine.items)))
        orientations = [0] * len(packing_engine.items)
        
        result = packing_engine.pack(sequence, orientations)
        
        utilization = result['utilization']
        assert 0 <= utilization <= 100
    
    def test_rotation_handling(self, packing_engine):
        """Test item rotation."""
        item = packing_engine.items[0]
        
        # Get dimensions for different orientations
        dims0 = packing_engine._get_rotated_dimensions(item, 0)
        dims1 = packing_engine._get_rotated_dimensions(item, 1)
        
        # Dimensions should change with rotation
        assert dims0 != dims1 or item.get('rotation_allowed') is False


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.algorithms
@pytest.mark.integration
class TestAlgorithmIntegration:
    """Integration tests for algorithms."""
    
    def test_ga_vs_cs_comparison(self, sample_container, sample_items, test_config):
        """Compare GA and CS results."""
        ga = GeneticAlgorithm(sample_container, sample_items, test_config)
        cs = ConstraintSolver(sample_container, sample_items, test_config)
        
        ga_result = ga.run(max_time=5)
        cs_result = cs.solve(max_time=5)
        
        # Both should produce valid results
        assert ga_result['status'] == 'completed'
        assert cs_result['status'] == 'completed'
        
        # Both should pack some items
        assert ga_result['items_packed'] > 0
        assert cs_result['items_packed'] > 0
    
    @pytest.mark.slow
    def test_heavy_load_optimization(self, sample_container, sample_heavy_items, test_config):
        """Test optimization with heavy items."""
        ga = GeneticAlgorithm(sample_container, sample_heavy_items, test_config)
        
        result = ga.run(max_time=10)
        
        # Should handle weight constraints
        assert result['is_valid'] or len(result['violations']) > 0
        
        # Heavy items should be placed low if packed
        if result['placements']:
            heavy_placements = [p for p in result['placements']]
            if heavy_placements:
                avg_z = sum(p.z for p in heavy_placements) / len(heavy_placements)
                container_height = sample_container['height']
                assert avg_z < container_height * 0.5  # Below mid-height