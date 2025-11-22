# CargoOpt Algorithm Details

## Table of Contents

1. [Overview](#overview)
2. [Genetic Algorithm](#genetic-algorithm)
3. [Constraint Programming](#constraint-programming)
4. [Packing Heuristics](#packing-heuristics)
5. [Stowage Planning](#stowage-planning)
6. [Fitness Evaluation](#fitness-evaluation)
7. [Constraint Validation](#constraint-validation)
8. [Performance Optimization](#performance-optimization)

---

## Overview

CargoOpt implements multiple optimization algorithms to solve the 3D bin packing problem with various constraints. This document provides technical details about the algorithms, their implementation, and when to use each approach.

### Problem Definition

**Input:**
- Container: Dimensions (L×W×H), maximum weight capacity
- Items: Set of N items, each with dimensions, weight, and constraints
- Constraints: Stacking rules, rotation limits, hazmat segregation, etc.

**Output:**
- Placement: Position (x, y, z) and orientation for each item
- Utilization: Percentage of space used
- Validation: All constraints satisfied

**Objective:**
Maximize space utilization while satisfying all constraints

### Algorithm Selection

| Criteria | Genetic | Constraint | Hybrid |
|----------|---------|-----------|--------|
| Problem Size | 20-1000 items | <20 items | Any |
| Constraints | Many soft | Many hard | Mixed |
| Time | 30-120s | 10-30s | 60-180s |
| Solution Quality | Near-optimal | Valid | Good |

---

## Genetic Algorithm

### Overview

The Genetic Algorithm (GA) uses evolutionary principles to optimize container packing. It maintains a population of solutions that evolve over generations through selection, crossover, and mutation.

### Implementation

#### Chromosome Representation

Each individual (solution) is represented by:
```python
Individual = {
    sequence: [item_indices],      # Order of packing
    orientations: [0-5],           # Rotation for each item
    fitness: float,                # Solution quality
    placements: [Placement],       # 3D positions
    utilization: float,            # Space utilization %
    is_valid: bool,               # All constraints satisfied
    violations: [str]              # Constraint violations
}
```

**Example:**
```python
{
    "sequence": [2, 0, 4, 1, 3],  # Pack item 2 first, then 0, etc.
    "orientations": [0, 2, 1, 0, 5],  # Rotation indices
    "fitness": 0.8234,
    "utilization": 78.5
}
```

#### Orientation Encoding

Six possible orientations for each item:
```python
0: (L, W, H)  # Original orientation
1: (L, H, W)  # Rotate around length axis
2: (W, L, H)  # Rotate around height axis
3: (W, H, L)  # 90° rotation
4: (H, L, W)  # Different rotation
5: (H, W, L)  # Different rotation
```

Constraints:
- `keep_upright=True`: Only orientation 0 allowed
- `rotation_allowed=False`: Only orientation 0 allowed

### Algorithm Steps

#### 1. Initialization

```python
def initialize_population(population_size, num_items):
    population = []
    for _ in range(population_size):
        sequence = shuffle([0...num_items-1])
        orientations = random_choice([0-5], num_items)
        individual = Individual(sequence, orientations)
        population.append(individual)
    return population
```

Parameters:
- Population Size: 50-150 (default: 100)
- Larger populations = more diversity, longer computation

#### 2. Fitness Evaluation

For each individual:
```python
def evaluate_individual(individual):
    # Pack items according to sequence and orientations
    result = pack_items(individual.sequence, individual.orientations)
    
    # Calculate fitness components
    util_score = result.utilization / 100.0
    stability_score = calculate_stability(result)
    constraint_score = calculate_constraints(result)
    access_score = calculate_accessibility(result)
    
    # Weighted fitness
    fitness = (
        0.4 * util_score +
        0.25 * stability_score +
        0.25 * constraint_score +
        0.1 * access_score
    )
    
    individual.fitness = fitness
    return fitness
```

**Utilization Score:**
```python
utilization = (used_volume / container_volume) * 100
util_score = utilization / 100.0
```

**Stability Score:**
```python
# Calculate center of gravity
cog_z = sum(weight_i * z_center_i) / total_weight

# Score based on COG height (lower is better)
stability_score = 1.0 - (cog_z / container_height)

# Penalty for high COG
if cog_z > container_height / 2:
    stability_score *= 0.8
```

**Constraint Score:**
```python
if all_constraints_satisfied:
    score = 1.0
else:
    score = 0.5 - (num_violations * 0.05)
    score = max(0, score)
```

**Accessibility Score:**
```python
# Count items not blocked from above
accessible = count_unblocked_items(placements)
access_score = accessible / total_items
```

#### 3. Selection

Tournament Selection:
```python
def tournament_selection(population, tournament_size=3):
    tournament = random_sample(population, tournament_size)
    winner = max(tournament, key=lambda x: x.fitness)
    return winner
```

Why Tournament Selection:
- Balances exploration and exploitation
- Computationally efficient
- Maintains diversity

#### 4. Crossover

Order Crossover (OX) for sequence:
```python
def order_crossover(parent1, parent2):
    n = len(parent1.sequence)
    point1, point2 = sorted(random_sample(range(n), 2))
    
    # Child 1: Copy segment from parent1
    child1_seq = [-1] * n
    child1_seq[point1:point2] = parent1.sequence[point1:point2]
    
    # Fill remaining from parent2 in order
    pos = point2
    for item in parent2.sequence[point2:] + parent2.sequence[:point2]:
        if item not in child1_seq:
            child1_seq[pos % n] = item
            pos += 1
    
    # Similar for child2 from parent2
    child2_seq = create_child2(parent1, parent2, point1, point2)
    
    return child1_seq, child2_seq
```

Uniform Crossover for orientations:
```python
def uniform_crossover(parent1, parent2):
    child1_orient = []
    child2_orient = []
    for o1, o2 in zip(parent1.orientations, parent2.orientations):
        if random() < 0.5:
            child1_orient.append(o1)
            child2_orient.append(o2)
        else:
            child1_orient.append(o2)
            child2_orient.append(o1)
    return child1_orient, child2_orient
```

Parameters:
- Crossover Rate: 0.7-0.95 (default: 0.85)
- Higher rate = more exploration

#### 5. Mutation

Two mutation operators:

**Swap Mutation (Sequence):**
```python
def swap_mutation(individual):
    i, j = random_sample(range(len(sequence)), 2)
    individual.sequence[i], individual.sequence[j] = \
        individual.sequence[j], individual.sequence[i]
```

**Flip Mutation (Orientations):**
```python
def flip_mutation(individual):
    i = random_int(0, len(orientations)-1)
    individual.orientations[i] = random_int(0, 5)
```

Parameters:
- Mutation Rate: 0.05-0.25 (default: 0.15)
- Higher rate = more exploration, slower convergence

#### 6. Elitism

Preserve best solutions:
```python
def create_next_generation(population, elite_size=5):
    # Keep best individuals
    elite = get_top_n(population, elite_size)
    
    # Create offspring for remaining slots
    offspring = []
    while len(offspring) < (population_size - elite_size):
        parent1 = tournament_selection(population)
        parent2 = tournament_selection(population)
        
        if random() < crossover_rate:
            child1, child2 = crossover(parent1, parent2)
        else:
            child1, child2 = copy(parent1), copy(parent2)
        
        if random() < mutation_rate:
            mutate(child1)
        if random() < mutation_rate:
            mutate(child2)
        
        offspring.extend([child1, child2])
    
    return elite + offspring[:population_size - elite_size]
```

#### 7. Termination

Algorithm stops when:
1. Maximum generations reached
2. Time limit exceeded
3. Convergence detected (fitness unchanged for 10 generations)

### Parameters Tuning

**Small Problems (<50 items):**
```python
population_size = 50
generations = 25
mutation_rate = 0.2
```

**Medium Problems (50-200 items):**
```python
population_size = 100
generations = 50
mutation_rate = 0.15
```

**Large Problems (200+ items):**
```python
population_size = 150
generations = 100
mutation_rate = 0.1
```

### Advantages
- ✓ Finds near-optimal solutions
- ✓ Handles complex constraints
- ✓ Scales well to large problems
- ✓ Balances multiple objectives

### Disadvantages
- ✗ Longer computation time
- ✗ No guarantee of optimality
- ✗ Sensitive to parameter tuning

---

## Constraint Programming

### Overview

Constraint Programming (CP) uses backtracking search with constraint propagation to find valid solutions that satisfy all hard constraints.

### Implementation

#### Constraint Types

**Hard Constraints (Must be satisfied):**
1. Within Container Bounds
2. No Overlaps
3. Weight Limit
4. Adequate Support
5. Stack Weight Limits

**Soft Constraints (Preferences):**
1. Fragile Items on Top
2. Heavy Items at Bottom
3. Preferred Orientations
4. Accessibility

#### Constraint Representation

```python
Constraint = {
    name: str,
    type: 'hard' | 'soft',
    description: str,
    check_function: callable,
    weight: float  # For soft constraints
}
```

### Algorithm Steps

#### 1. Variable Ordering

Sort items by priority:
```python
def sort_items_by_priority(items):
    return sorted(items, key=lambda x: (
        x.priority,                    # Lower number = higher priority
        -(x.length * x.width * x.height),  # Larger items first
        -x.weight                      # Heavier items first
    ))
```

#### 2. Value Ordering

Generate candidate positions:
```python
def generate_positions(item, container, current_placements):
    positions = []
    
    # Get corner points from existing placements
    corners = get_corner_points(current_placements)
    corners.append((0, 0, 0))  # Include origin
    
    # Try each corner with each orientation
    for corner in corners:
        for orientation in get_allowed_orientations(item):
            l, w, h = orientation
            
            # Check if fits at this position
            if fits_in_container(corner, (l, w, h), container):
                placement = create_placement(item, corner, (l, w, h))
                positions.append(placement)
    
    # Sort by preference (lower-left-back first)
    positions.sort(key=lambda p: (p.z, p.y, p.x))
    
    return positions
```

**Corner Points:**
Created by existing placements:
```python
def get_corner_points(placements):
    corners = set()
    
    for p in placements:
        # Top corners
        corners.add((p.x, p.y, p.z + p.height))
        corners.add((p.x + p.length, p.y, p.z + p.height))
        corners.add((p.x, p.y + p.width, p.z + p.height))
        
        # Side corners
        corners.add((p.x + p.length, p.y, p.z))
        corners.add((p.x, p.y + p.width, p.z))
    
    return list(corners)[:50]  # Limit for performance
```

#### 3. Backtracking Search

```python
def backtrack_search(items, container, placements=[], unpacked=[]):
    # Base case: all items placed or none can fit
    if not items:
        return evaluate_solution(placements), placements
    
    # Select next item
    item = items[0]
    remaining = items[1:]
    
    # Generate candidate positions
    positions = generate_positions(item, container, placements)
    
    # Try each position
    best_score = 0
    best_solution = placements
    
    for position in positions:
        if is_valid_placement(position, placements, container):
            # Recursive search
            score, solution = backtrack_search(
                remaining,
                container,
                placements + [position],
                unpacked
            )
            
            if score > best_score:
                best_score = score
                best_solution = solution
    
    # Try skipping this item
    score, solution = backtrack_search(
        remaining,
        container,
        placements,
        unpacked + [item]
    )
    
    if score > best_score:
        best_score = score
        best_solution = solution
    
    return best_score, best_solution
```

#### 4. Constraint Checking

**Within Container:**
```python
def check_within_container(placement, container):
    return (
        placement.x >= 0 and
        placement.y >= 0 and
        placement.z >= 0 and
        placement.x + placement.length <= container.length and
        placement.y + placement.width <= container.width and
        placement.z + placement.height <= container.height
    )
```

**No Overlap:**
```python
def check_no_overlap(placement, placements):
    for other in placements:
        if overlaps(placement, other):
            return False
    return True

def overlaps(p1, p2):
    return not (
        p1.x + p1.length <= p2.x or p2.x + p2.length <= p1.x or
        p1.y + p1.width <= p2.y or p2.y + p2.width <= p1.y or
        p1.z + p1.height <= p2.z or p2.z + p2.height <= p1.z
    )
```

**Adequate Support:**
```python
def check_support(placement, placements):
    if placement.z == 0:
        return True  # On floor
    
    # Calculate support from below
    support_area = 0
    item_area = placement.length * placement.width
    
    for other in placements:
        if abs(other.z + other.height - placement.z) < 1:
            overlap = calculate_overlap_area(placement, other)
            support_area += overlap
    
    # Require 60% support
    return support_area >= 0.6 * item_area
```

### Advantages
- ✓ Guaranteed valid solutions
- ✓ Fast for small problems
- ✓ Handles hard constraints well
- ✓ Deterministic results

### Disadvantages
- ✗ May not find optimal solution
- ✗ Slow for large problems
- ✗ Limited soft constraint handling

---

## Packing Heuristics

### Best Fit Decreasing

1. Sort items by volume (descending)
2. For each item, find space with minimum waste
3. Place item and update available spaces

```python
def best_fit_decreasing(items, container):
    items.sort(key=lambda x: x.volume, reverse=True)
    
    for item in items:
        best_space = None
        min_waste = inf
        
        for space in available_spaces:
            if space.fits(item):
                waste = space.volume - item.volume
                if waste < min_waste:
                    min_waste = waste
                    best_space = space
        
        if best_space:
            place_item(item, best_space)
            update_spaces(best_space, item)
```

### Bottom-Left-Back

Place items at lowest, leftmost, back-most position:

```python
def bottom_left_back(items, container):
    spaces.sort(key=lambda s: (s.z, s.y, s.x))
    
    for item in items:
        for space in spaces:
            if space.fits(item):
                place_item(item, space)
                update_spaces(space, item)
                break
```

### Guillotine Cut

Split spaces using straight cuts:

```python
def split_space(space, placement):
    splits = []
    
    # Right split
    if placement.x + placement.length < space.x + space.length:
        splits.append(Space(
            x=placement.x + placement.length,
            y=space.y,
            z=space.z,
            length=space.x + space.length - (placement.x + placement.length),
            width=space.width,
            height=space.height
        ))
    
    # Front split
    if placement.y + placement.width < space.y + space.width:
        splits.append(Space(
            x=space.x,
            y=placement.y + placement.width,
            z=space.z,
            length=space.length,
            width=space.y + space.width - (placement.y + placement.width),
            height=space.height
        ))
    
    # Top split
    if placement.z + placement.height < space.z + space.height:
        splits.append(Space(
            x=space.x,
            y=space.y,
            z=placement.z + placement.height,
            length=space.length,
            width=space.width,
            height=space.z + space.height - (placement.z + placement.height)
        ))
    
    return splits
```

---

## Stowage Planning

### IMDG Compliance

Automatic segregation of hazardous materials based on IMDG Code.

#### Segregation Requirements

```python
SEGREGATION_TABLE = {
    '1': {'2.1': 'segregated', '3': 'separated', ...},
    '2.1': {'3': 'separated', '4.1': 'separated', ...},
    '3': {'5.1': 'separated', '8': 'separated', ...},
    ...
}
```

**Segregation Levels:**
- **Compatible**: Can be adjacent
- **Separated**: Minimum one container length (6m)
- **Segregated**: Minimum two container lengths (12m)
- **Prohibited**: Cannot be on same vessel

#### Distance Calculation

```python
def calculate_segregation_distance(class1, class2):
    segregation = SEGREGATION_TABLE[class1][class2]
    
    if segregation == 'separated':
        return 6058  # One 20ft container length (mm)
    elif segregation == 'segregated':
        return 12116  # Two container lengths
    elif segregation == 'prohibited':
        return float('inf')
    else:
        return 0  # Compatible
```

### Stability Calculations

#### Center of Gravity

```python
def calculate_center_of_gravity(placements):
    total_weight = sum(p.weight for p in placements)
    
    if total_weight == 0:
        return (0, 0, 0)
    
    cog_x = sum(p.weight * (p.x + p.length/2) for p in placements) / total_weight
    cog_y = sum(p.weight * (p.y + p.width/2) for p in placements) / total_weight
    cog_z = sum(p.weight * (p.z + p.height/2) for p in placements) / total_weight
    
    return (cog_x, cog_y, cog_z)
```

#### Metacentric Height (GM)

```python
def calculate_gm(vessel, placements):
    # Simplified calculation
    cog_x, cog_y, cog_z = calculate_center_of_gravity(placements)
    
    # Vertical center of buoyancy
    vcb = vessel.draft / 2
    
    # Metacenter height above baseline
    bm = calculate_bm(vessel)
    km = vcb + bm
    
    # GM = KM - KG
    gm = km - cog_z
    
    return gm
```

---

## Fitness Evaluation

### Multi-Objective Fitness

```python
def calculate_fitness(solution, weights):
    scores = {
        'utilization': calculate_utilization(solution) / 100.0,
        'stability': calculate_stability_score(solution),
        'constraints': calculate_constraint_score(solution),
        'accessibility': calculate_accessibility_score(solution)
    }
    
    fitness = sum(
        weights[key] * scores[key]
        for key in scores
    )
    
    return fitness
```

### Default Weights

```python
WEIGHTS = {
    'utilization': 0.4,
    'stability': 0.25,
    'constraints': 0.25,
    'accessibility': 0.1
}
```

### Objective-Specific Weights

**Maximum Utilization:**
```python
{'utilization': 0.7, 'stability': 0.1, 'constraints': 0.15, 'accessibility': 0.05}
```

**Maximum Stability:**
```python
{'utilization': 0.2, 'stability': 0.6, 'constraints': 0.15, 'accessibility': 0.05}
```

**Balanced:**
```python
{'utilization': 0.4, 'stability': 0.25, 'constraints': 0.25, 'accessibility': 0.1}
```

---

## Constraint Validation

### Validation Pipeline

```python
def validate_solution(placements, container, items):
    violations = []
    
    for placement in placements:
        # Check each constraint
        if not within_container(placement, container):
            violations.append(f"Item {placement.item_index} outside container")
        
        if not has_support(placement, placements):
            violations.append(f"Item {placement.item_index} lacks support")
        
        if exceeds_stack_weight(placement, placements, items):
            violations.append(f"Item {placement.item_index} stack weight exceeded")
    
    # Check global constraints
    if exceeds_weight_limit(placements, container):
        violations.append("Total weight exceeds container capacity")
    
    # Check hazmat segregation
    hazmat_violations = check_hazmat_segregation(placements, items)
    violations.extend(hazmat_violations)
    
    return len(violations) == 0, violations
```

---

## Performance Optimization

### Computational Complexity

**Genetic Algorithm:**
- Time: O(P × G × N × log N)
- Space: O(P × N)
- P = Population size
- G = Generations
- N = Number of items

**Constraint Programming:**
- Time: O(N! × M) worst case
- Space: O(N × M)
- N = Number of items
- M = Number of positions per item

### Optimization Techniques

**1. Early Termination**
```python
if improvement < 0.001 for last 10 generations:
    terminate()
```

**2. Pruning**
```python
if current_best > upper_bound:
    prune_branch()
```

**3. Caching**
```python
@lru_cache(maxsize=10000)
def check_overlap(p1, p2):
    # Expensive calculation cached
    ...
```

**4. Parallel Evaluation**
```python
with ThreadPoolExecutor(max_workers=4) as executor:
    fitnesses = executor.map(evaluate_individual, population)
```

---

**CargoOpt Algorithm Details - Version 1.0.0**  
*Last Updated: November 2024*