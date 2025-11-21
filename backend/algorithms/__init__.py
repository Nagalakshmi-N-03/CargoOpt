"""
CargoOpt Algorithms Package
Provides optimization algorithms for container packing.

This package includes:
- Genetic Algorithm: Population-based optimization for container packing
- Constraint Solver: Rule-based constraint programming approach
- Packing Algorithms: Core packing logic and heuristics
- Stowage Planning: Maritime container stowage optimization

Main Classes:
    - GeneticAlgorithm: GA-based optimization engine
    - ConstraintSolver: CP-based optimization engine
    - PackingEngine: Core packing algorithms
    - StowagePlanner: Container stowage planner
"""

from backend.algorithms.genetic_algorithm import GeneticAlgorithm, Individual, Population
from backend.algorithms.constraint_solver import ConstraintSolver, Constraint
from backend.algorithms.packing import PackingEngine, PackingHeuristic, Placement
from backend.algorithms.stowage import StowagePlanner, StowageRules

__all__ = [
    'GeneticAlgorithm',
    'Individual',
    'Population',
    'ConstraintSolver',
    'Constraint',
    'PackingEngine',
    'PackingHeuristic',
    'Placement',
    'StowagePlanner',
    'StowageRules'
]

__version__ = '1.0.0'