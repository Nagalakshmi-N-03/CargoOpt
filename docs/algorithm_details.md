# CargoOpt Algorithm Details

## Overview

CargoOpt employs multiple optimization algorithms to solve the complex container stowage planning problem. This document details the algorithms, their implementations, and how they work together to produce optimal stowage plans.

## 🎯 Problem Definition

### Container Stowage Optimization Problem

The container stowage problem involves:
- **Input**: Vessel configuration, container specifications, voyage details
- **Constraints**: Physical, safety, operational, and regulatory constraints
- **Objectives**: Maximize utilization, ensure stability, minimize handling time
- **Output**: Optimal container positions within vessel compartments

### Key Constraints

1. **Physical Constraints**
   - Weight limits per compartment and overall vessel
   - Dimensional constraints (container size vs. slot size)
   - Stack weight limitations

2. **Safety Constraints**
   - Stability criteria (GM, trim, list)
   - Hazardous material segregation
   - Reefer container power requirements

3. **Operational Constraints**
   - Port rotation and unloading sequence
   - Crane operations and accessibility
   - Special container handling

## 🧠 Algorithm Architecture

### Multi-Algorithm Approach

CargoOpt uses a hybrid approach combining:


## 1. Genetic Algorithm (GA)

### Overview
Evolutionary algorithm that mimics natural selection to find near-optimal solutions.

### Implementation

```python
# Key Components
- Chromosome: Representation of container positions
- Population: Set of potential solutions
- Fitness Function: Evaluates solution quality
- Selection: Chooses parents for reproduction
- Crossover: Combines parent solutions
- Mutation: Introduces random changes


Fitness Function

def fitness_function(solution):
    stability_score = calculate_stability(solution)
    utilization_score = calculate_utilization(solution)
    safety_score = calculate_safety_compliance(solution)
    operational_score = calculate_operational_efficiency(solution)
    
    total_score = (
        w1 * stability_score +
        w2 * utilization_score + 
        w3 * safety_score +
        w4 * operational_score
    )
    return total_score

    2. Constraint Programming (CP)
Overview
Systematic approach that defines and solves constraint satisfaction problems.

Key Constraints Implementation
python
# Weight Constraints
def weight_constraint(compartment, containers):
    total_weight = sum(container.weight for container in containers)
    return total_weight <= compartment.max_weight

# Stability Constraints  
def stability_constraint(vessel, stowage_plan):
    gm = calculate_metacentric_height(vessel, stowage_plan)
    trim = calculate_trim(vessel, stowage_plan)
    return (gm_min <= gm <= gm_max) and (abs(trim) <= trim_max)

# Hazardous Material Constraints
def hazardous_constraint(container1, container2, distance):
    if both_hazardous(container1, container2):
        return distance >= required_segregation
    return True