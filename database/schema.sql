-- CargoOpt Database Schema
-- Container Vessel Stowage Optimization System

-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Vessels table
CREATE TABLE vessels (
    id SERIAL PRIMARY KEY,
    imo_number VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    call_sign VARCHAR(10),
    flag VARCHAR(50),
    vessel_type VARCHAR(20) NOT NULL CHECK (vessel_type IN (
        'container_ship', 'bulk_carrier', 'tanker', 'roro', 
        'general_cargo', 'lng_carrier'
    )),
    classification_society VARCHAR(100),
    
    -- Physical dimensions (in meters)
    length_overall DECIMAL(8,2) NOT NULL,
    breadth DECIMAL(8,2) NOT NULL,
    depth DECIMAL(8,2) NOT NULL,
    draft_design DECIMAL(8,2) NOT NULL,
    draft_max DECIMAL(8,2) NOT NULL,
    
    -- Capacity information
    deadweight_tonnage DECIMAL(10,2) NOT NULL,  -- in tons
    gross_tonnage DECIMAL(10,2) NOT NULL,       -- in tons
    net_tonnage DECIMAL(10,2) NOT NULL,         -- in tons
    teu_capacity INTEGER NOT NULL,
    reefer_plugs INTEGER,
    
    -- Structure
    number_of_holds INTEGER,
    number_of_hatches INTEGER,
    
    -- Operational data
    service_speed DECIMAL(5,2),  -- in knots
    max_speed DECIMAL(5,2),      -- in knots
    fuel_consumption JSONB,      -- Fuel consumption at different speeds
    
    -- Stability and safety
    gm_min DECIMAL(5,2),    -- Minimum metacentric height
    gm_max DECIMAL(5,2),    -- Maximum metacentric height
    trim_max DECIMAL(5,2),  -- Maximum trim in meters
    
    -- Metadata
    built_year INTEGER,
    builder VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    additional_properties JSONB,
    
    -- Indexes
    CONSTRAINT vessels_imo_unique UNIQUE (imo_number)
);

-- Vessel compartments table
CREATE TABLE vessel_compartments (
    id SERIAL PRIMARY KEY,
    vessel_id INTEGER NOT NULL REFERENCES vessels(id) ON DELETE CASCADE,
    
    -- Compartment identification
    bay_number INTEGER NOT NULL,      -- Longitudinal position
    row_number INTEGER NOT NULL,      -- Transverse position
    tier_number INTEGER NOT NULL,     -- Vertical position
    
    -- Physical properties (in meters)
    length DECIMAL(6,2) NOT NULL,
    width DECIMAL(6,2) NOT NULL,
    height DECIMAL(6,2) NOT NULL,
    max_weight DECIMAL(10,2) NOT NULL,  -- in kg
    
    -- Special capabilities
    can_accommodate_reefer BOOLEAN DEFAULT FALSE,
    can_accommodate_hazardous BOOLEAN DEFAULT FALSE,
    can_accommodate_oversized BOOLEAN DEFAULT FALSE,
    has_power_supply BOOLEAN DEFAULT FALSE,
    
    -- Operational constraints
    is_occupied BOOLEAN DEFAULT FALSE,
    is_blocked BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints and indexes
    UNIQUE(vessel_id, bay_number, row_number, tier_number),
    CONSTRAINT valid_bay_number CHECK (bay_number > 0),
    CONSTRAINT valid_row_number CHECK (row_number > 0),
    CONSTRAINT valid_tier_number CHECK (tier_number > 0)
);

-- Containers table
CREATE TABLE containers (
    id SERIAL PRIMARY KEY,
    container_number VARCHAR(20) UNIQUE NOT NULL,
    iso_code VARCHAR(4) NOT NULL,
    
    -- Physical properties (in feet and kg)
    length DECIMAL(5,2) NOT NULL,
    width DECIMAL(5,2) NOT NULL,
    height DECIMAL(5,2) NOT NULL,
    tare_weight DECIMAL(8,2) NOT NULL,
    max_payload DECIMAL(8,2) NOT NULL,
    gross_weight DECIMAL(8,2) GENERATED ALWAYS AS (tare_weight + COALESCE(cargo_weight, 0)) STORED,
    
    -- Container type and category
    container_type VARCHAR(20) NOT NULL CHECK (container_type IN (
        'dry', 'reefer', 'tank', 'flatrack', 'open_top', 
        'high_cube', 'ventilated', 'hazardous'
    )),
    status VARCHAR(20) DEFAULT 'empty' CHECK (status IN (
        'empty', 'loaded', 'in_transit', 'delivered', 'damaged'
    )),
    
    -- Cargo information
    cargo_description TEXT,
    cargo_weight DECIMAL(8,2),
    imdg_class VARCHAR(10),
    un_number VARCHAR(4),
    
    -- Special requirements
    is_reefer BOOLEAN DEFAULT FALSE,
    reefer_temperature DECIMAL(4,1),
    is_oversized BOOLEAN DEFAULT FALSE,
    requires_power BOOLEAN DEFAULT FALSE,
    
    -- Location and tracking
    current_location VARCHAR(100),
    destination_port VARCHAR(100),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    additional_properties JSONB,
    
    -- Indexes
    CONSTRAINT containers_number_unique UNIQUE (container_number)
);

-- Stowage plans table
CREATE TABLE stowage_plans (
    id SERIAL PRIMARY KEY,
    plan_name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- References
    vessel_id INTEGER NOT NULL REFERENCES vessels(id),
    
    -- Plan status
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN (
        'draft', 'optimizing', 'completed', 'approved', 'rejected'
    )),
    
    -- Optimization metrics
    total_containers INTEGER DEFAULT 0,
    total_weight DECIMAL(12,2) DEFAULT 0,
    teu_utilization DECIMAL(5,2) DEFAULT 0,  -- Percentage
    stability_score DECIMAL(5,2) DEFAULT 0,  -- 0-100 scale
    efficiency_score DECIMAL(5,2) DEFAULT 0, -- 0-100 scale
    
    -- Safety metrics
    gm_actual DECIMAL(5,2),      -- Actual metacentric height
    trim_actual DECIMAL(5,2),    -- Actual trim
    list_actual DECIMAL(5,2),    -- Actual list
    
    -- Optimization parameters
    optimization_parameters JSONB,
    
    -- Metadata
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Stowage positions table (container placements)
CREATE TABLE stowage_positions (
    id SERIAL PRIMARY KEY,
    stowage_plan_id INTEGER NOT NULL REFERENCES stowage_plans(id) ON DELETE CASCADE,
    container_id INTEGER NOT NULL REFERENCES containers(id),
    vessel_compartment_id INTEGER NOT NULL REFERENCES vessel_compartments(id),
    
    -- Position coordinates
    bay_number INTEGER NOT NULL,
    row_number INTEGER NOT NULL,
    tier_number INTEGER NOT NULL,
    
    -- Orientation
    orientation VARCHAR(10) DEFAULT 'normal' CHECK (orientation IN ('normal', 'rotated')),
    
    -- Safety and constraints
    is_secured BOOLEAN DEFAULT FALSE,
    has_power_connected BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    placed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(stowage_plan_id, container_id),
    UNIQUE(stowage_plan_id, vessel_compartment_id),
    CONSTRAINT valid_position CHECK (bay_number > 0 AND row_number > 0 AND tier_number > 0)
);

-- Optimization results table
CREATE TABLE optimization_results (
    id SERIAL PRIMARY KEY,
    stowage_plan_id INTEGER NOT NULL REFERENCES stowage_plans(id) ON DELETE CASCADE,
    
    -- Algorithm information
    algorithm_used VARCHAR(50) NOT NULL,
    algorithm_parameters JSONB,
    
    -- Performance metrics
    iterations INTEGER DEFAULT 0,
    computation_time DECIMAL(8,2) DEFAULT 0,  -- in seconds
    fitness_score DECIMAL(8,4) DEFAULT 0,
    
    -- Results
    best_solution JSONB,
    convergence_data JSONB,  -- For tracking algorithm convergence
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Hazardous materials constraints table
CREATE TABLE hazardous_constraints (
    id SERIAL PRIMARY KEY,
    imdg_class VARCHAR(10) NOT NULL,
    un_number VARCHAR(4),
    description TEXT NOT NULL,
    
    -- Segregation rules
    requires_segregation_from JSONB,  -- List of IMDG classes that require segregation
    minimum_distance INTEGER,         -- Minimum distance in bays
    cannot_be_under BOOLEAN DEFAULT FALSE,
    cannot_be_over BOOLEAN DEFAULT FALSE,
    
    -- Special handling
    requires_special_ventilation BOOLEAN DEFAULT FALSE,
    requires_temperature_control BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX idx_vessels_imo ON vessels(imo_number);
CREATE INDEX idx_vessels_type ON vessels(vessel_type);
CREATE INDEX idx_containers_number ON containers(container_number);
CREATE INDEX idx_containers_type ON containers(container_type);
CREATE INDEX idx_containers_status ON containers(status);
CREATE INDEX idx_containers_hazardous ON containers(imdg_class) WHERE imdg_class IS NOT NULL;
CREATE INDEX idx_compartments_vessel ON vessel_compartments(vessel_id);
CREATE INDEX idx_compartments_position ON vessel_compartments(bay_number, row_number, tier_number);
CREATE INDEX idx_stowage_plans_vessel ON stowage_plans(vessel_id);
CREATE INDEX idx_stowage_plans_status ON stowage_plans(status);
CREATE INDEX idx_stowage_positions_plan ON stowage_positions(stowage_plan_id);
CREATE INDEX idx_stowage_positions_container ON stowage_positions(container_id);
CREATE INDEX idx_stowage_positions_compartment ON stowage_positions(vessel_compartment_id);
CREATE INDEX idx_optimization_results_plan ON optimization_results(stowage_plan_id);

-- Functions
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_vessels_updated_at BEFORE UPDATE ON vessels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_containers_updated_at BEFORE UPDATE ON containers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stowage_plans_updated_at BEFORE UPDATE ON stowage_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hazardous_constraints_updated_at BEFORE UPDATE ON hazardous_constraints
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate vessel utilization
CREATE OR REPLACE FUNCTION calculate_vessel_utilization(vessel_id INTEGER)
RETURNS TABLE(
    teu_used INTEGER,
    teu_capacity INTEGER,
    utilization_percentage DECIMAL(5,2),
    weight_used DECIMAL(12,2),
    weight_capacity DECIMAL(12,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(sp.id)::INTEGER as teu_used,
        v.teu_capacity,
        ROUND((COUNT(sp.id)::DECIMAL / v.teu_capacity * 100), 2) as utilization_percentage,
        COALESCE(SUM(c.gross_weight), 0) as weight_used,
        v.deadweight_tonnage * 1000 as weight_capacity  -- Convert tons to kg
    FROM vessels v
    LEFT JOIN stowage_positions sp ON v.id = sp.vessel_compartment_id
    LEFT JOIN containers c ON sp.container_id = c.id
    WHERE v.id = vessel_id
    GROUP BY v.id, v.teu_capacity, v.deadweight_tonnage;
END;
$$ LANGUAGE plpgsql;

-- Comments
COMMENT ON TABLE vessels IS 'Vessel specifications and characteristics';
COMMENT ON TABLE vessel_compartments IS 'Vessel compartments for container stowage';
COMMENT ON TABLE containers IS 'Container specifications and cargo information';
COMMENT ON TABLE stowage_plans IS 'Container stowage plans and optimization results';
COMMENT ON TABLE stowage_positions IS 'Individual container positions within stowage plans';
COMMENT ON TABLE optimization_results IS 'Optimization algorithm performance and results';
COMMENT ON TABLE hazardous_constraints IS 'Hazardous materials handling constraints and segregation rules';