-- CargoOpt Database Schema
-- Container Vessel Stowage Optimization System
-- PostgreSQL Database Schema

-- ============================================================================
-- Extensions
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- Enums and Custom Types
-- ============================================================================

-- Vessel types
CREATE TYPE vessel_type_enum AS ENUM (
    'container_ship',
    'bulk_carrier',
    'tanker',
    'roro',
    'general_cargo',
    'lng_carrier'
);

-- Container types
CREATE TYPE container_type_enum AS ENUM (
    'dry',
    'reefer',
    'tank',
    'flatrack',
    'open_top',
    'high_cube',
    'ventilated',
    'hazardous'
);

-- Container status
CREATE TYPE container_status_enum AS ENUM (
    'empty',
    'loaded',
    'in_transit',
    'delivered',
    'damaged'
);

-- Stowage plan status
CREATE TYPE stowage_plan_status_enum AS ENUM (
    'draft',
    'optimizing',
    'completed',
    'approved',
    'rejected'
);

-- Optimization status
CREATE TYPE optimization_status_enum AS ENUM (
    'pending',
    'running',
    'completed',
    'failed',
    'cancelled'
);

-- ============================================================================
-- Users and Authentication
-- ============================================================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'viewer')),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- ============================================================================
-- Vessels
-- ============================================================================

CREATE TABLE vessels (
    id SERIAL PRIMARY KEY,
    imo_number VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    call_sign VARCHAR(10),
    flag VARCHAR(50),
    vessel_type vessel_type_enum NOT NULL,
    classification_society VARCHAR(100),
    
    -- Physical dimensions (in meters)
    length_overall NUMERIC(8,2) NOT NULL,
    breadth NUMERIC(8,2) NOT NULL,
    depth NUMERIC(8,2) NOT NULL,
    draft_design NUMERIC(8,2) NOT NULL,
    draft_max NUMERIC(8,2) NOT NULL,
    
    -- Capacity information
    deadweight_tonnage NUMERIC(10,2) NOT NULL,
    gross_tonnage NUMERIC(10,2) NOT NULL,
    net_tonnage NUMERIC(10,2) NOT NULL,
    teu_capacity INTEGER NOT NULL,
    reefer_plugs INTEGER DEFAULT 0,
    
    -- Structure
    number_of_holds INTEGER,
    number_of_hatches INTEGER,
    
    -- Operational data
    service_speed NUMERIC(5,2),
    max_speed NUMERIC(5,2),
    fuel_consumption JSONB,
    
    -- Stability and safety
    gm_min NUMERIC(5,2),
    gm_max NUMERIC(5,2),
    trim_max NUMERIC(5,2),
    
    -- Metadata
    built_year INTEGER,
    builder VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    additional_properties JSONB,
    
    CONSTRAINT vessels_imo_unique UNIQUE (imo_number),
    CONSTRAINT vessels_valid_year CHECK (built_year >= 1900 AND built_year <= EXTRACT(YEAR FROM CURRENT_DATE) + 2)
);

CREATE INDEX idx_vessels_imo ON vessels(imo_number);
CREATE INDEX idx_vessels_type ON vessels(vessel_type);
CREATE INDEX idx_vessels_name ON vessels(name);

-- ============================================================================
-- Vessel Compartments
-- ============================================================================

CREATE TABLE vessel_compartments (
    id SERIAL PRIMARY KEY,
    vessel_id INTEGER NOT NULL REFERENCES vessels(id) ON DELETE CASCADE,
    
    -- Compartment identification
    bay_number INTEGER NOT NULL,
    row_number INTEGER NOT NULL,
    tier_number INTEGER NOT NULL,
    is_above_deck BOOLEAN DEFAULT FALSE,
    
    -- Physical properties (in meters)
    length NUMERIC(6,2) NOT NULL,
    width NUMERIC(6,2) NOT NULL,
    height NUMERIC(6,2) NOT NULL,
    max_weight NUMERIC(10,2) NOT NULL,
    
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
    
    UNIQUE(vessel_id, bay_number, row_number, tier_number, is_above_deck),
    CONSTRAINT valid_bay_number CHECK (bay_number > 0),
    CONSTRAINT valid_row_number CHECK (row_number > 0),
    CONSTRAINT valid_tier_number CHECK (tier_number > 0)
);

CREATE INDEX idx_compartments_vessel ON vessel_compartments(vessel_id);
CREATE INDEX idx_compartments_position ON vessel_compartments(bay_number, row_number, tier_number);
CREATE INDEX idx_compartments_occupied ON vessel_compartments(is_occupied);

-- ============================================================================
-- Containers
-- ============================================================================

CREATE TABLE containers (
    id SERIAL PRIMARY KEY,
    container_number VARCHAR(20) UNIQUE NOT NULL,
    iso_code VARCHAR(4) NOT NULL,
    
    -- Physical properties (in feet and kg)
    length NUMERIC(5,2) NOT NULL,
    width NUMERIC(5,2) NOT NULL,
    height NUMERIC(5,2) NOT NULL,
    tare_weight NUMERIC(8,2) NOT NULL,
    max_payload NUMERIC(8,2) NOT NULL,
    cargo_weight NUMERIC(8,2) DEFAULT 0,
    gross_weight NUMERIC(8,2) GENERATED ALWAYS AS (tare_weight + COALESCE(cargo_weight, 0)) STORED,
    
    -- Container type and category
    container_type container_type_enum NOT NULL,
    status container_status_enum DEFAULT 'empty',
    
    -- Cargo information
    cargo_description TEXT,
    imdg_class VARCHAR(10),
    un_number VARCHAR(4),
    
    -- Special requirements
    is_reefer BOOLEAN DEFAULT FALSE,
    reefer_temperature NUMERIC(4,1),
    is_oversized BOOLEAN DEFAULT FALSE,
    requires_power BOOLEAN DEFAULT FALSE,
    
    -- Location and tracking
    current_location VARCHAR(100),
    destination_port VARCHAR(100),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    additional_properties JSONB,
    
    CONSTRAINT containers_number_unique UNIQUE (container_number),
    CONSTRAINT valid_dimensions CHECK (length > 0 AND width > 0 AND height > 0),
    CONSTRAINT valid_weights CHECK (tare_weight > 0 AND max_payload > 0)
);

CREATE INDEX idx_containers_number ON containers(container_number);
CREATE INDEX idx_containers_type ON containers(container_type);
CREATE INDEX idx_containers_status ON containers(status);
CREATE INDEX idx_containers_hazardous ON containers(imdg_class) WHERE imdg_class IS NOT NULL;
CREATE INDEX idx_containers_reefer ON containers(is_reefer) WHERE is_reefer = TRUE;

-- ============================================================================
-- Items (for container packing)
-- ============================================================================

CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    item_id VARCHAR(50) UNIQUE,
    name VARCHAR(200),
    
    -- Dimensions (in mm)
    length INTEGER NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    
    -- Weight (in kg)
    weight NUMERIC(10,2) NOT NULL,
    
    -- Properties
    item_type VARCHAR(50) DEFAULT 'other',
    storage_condition VARCHAR(50) DEFAULT 'standard',
    is_fragile BOOLEAN DEFAULT FALSE,
    is_stackable BOOLEAN DEFAULT TRUE,
    max_stack_weight NUMERIC(10,2),
    
    -- Rotation constraints
    rotation_allowed BOOLEAN DEFAULT TRUE,
    keep_upright BOOLEAN DEFAULT FALSE,
    
    -- Hazardous materials
    hazard_class VARCHAR(10),
    un_number VARCHAR(4),
    
    -- Temperature requirements
    temperature_min NUMERIC(5,1),
    temperature_max NUMERIC(5,1),
    
    -- Priority (1 = highest)
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    
    -- Visual
    color VARCHAR(7),
    
    -- Metadata
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_item_dimensions CHECK (length > 0 AND width > 0 AND height > 0),
    CONSTRAINT valid_item_weight CHECK (weight > 0),
    CONSTRAINT valid_temperature_range CHECK (
        (temperature_min IS NULL AND temperature_max IS NULL) OR
        (temperature_min < temperature_max)
    )
);

CREATE INDEX idx_items_item_id ON items(item_id);
CREATE INDEX idx_items_type ON items(item_type);
CREATE INDEX idx_items_hazard ON items(hazard_class) WHERE hazard_class IS NOT NULL;

-- ============================================================================
-- Stowage Plans
-- ============================================================================

CREATE TABLE stowage_plans (
    id SERIAL PRIMARY KEY,
    plan_number VARCHAR(50) UNIQUE NOT NULL,
    plan_name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- References
    vessel_id INTEGER NOT NULL REFERENCES vessels(id),
    created_by INTEGER REFERENCES users(id),
    
    -- Port information
    loading_port VARCHAR(100),
    discharge_port VARCHAR(100),
    voyage_number VARCHAR(50),
    estimated_departure TIMESTAMP WITH TIME ZONE,
    estimated_arrival TIMESTAMP WITH TIME ZONE,
    
    -- Plan status
    status stowage_plan_status_enum DEFAULT 'draft',
    
    -- Optimization metrics
    total_containers INTEGER DEFAULT 0,
    total_weight NUMERIC(12,2) DEFAULT 0,
    total_volume NUMERIC(12,2) DEFAULT 0,
    teu_utilization NUMERIC(5,2) DEFAULT 0,
    stability_score NUMERIC(5,2) DEFAULT 0,
    efficiency_score NUMERIC(5,2) DEFAULT 0,
    
    -- Safety metrics
    gm_actual NUMERIC(5,2),
    trim_actual NUMERIC(5,2),
    list_actual NUMERIC(5,2),
    is_stable BOOLEAN DEFAULT TRUE,
    
    -- Optimization parameters
    algorithm_used VARCHAR(50),
    optimization_time NUMERIC(8,2),
    iterations_count INTEGER,
    optimization_parameters JSONB,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    approved_at TIMESTAMP WITH TIME ZONE,
    approved_by INTEGER REFERENCES users(id)
);

CREATE INDEX idx_stowage_plans_vessel ON stowage_plans(vessel_id);
CREATE INDEX idx_stowage_plans_status ON stowage_plans(status);
CREATE INDEX idx_stowage_plans_number ON stowage_plans(plan_number);
CREATE INDEX idx_stowage_plans_created_by ON stowage_plans(created_by);

-- ============================================================================
-- Stowage Positions
-- ============================================================================

CREATE TABLE stowage_positions (
    id SERIAL PRIMARY KEY,
    stowage_plan_id INTEGER NOT NULL REFERENCES stowage_plans(id) ON DELETE CASCADE,
    container_id INTEGER NOT NULL REFERENCES containers(id),
    vessel_compartment_id INTEGER NOT NULL REFERENCES vessel_compartments(id),
    
    -- Position coordinates
    bay_number INTEGER NOT NULL,
    row_number INTEGER NOT NULL,
    tier_number INTEGER NOT NULL,
    is_above_deck BOOLEAN DEFAULT FALSE,
    
    -- 3D position (in mm from origin)
    position_x NUMERIC(10,2),
    position_y NUMERIC(10,2),
    position_z NUMERIC(10,2),
    
    -- Orientation
    rotation INTEGER DEFAULT 0 CHECK (rotation IN (0, 90, 180, 270)),
    
    -- Loading sequence
    load_sequence INTEGER,
    discharge_sequence INTEGER,
    
    -- Safety and constraints
    is_secured BOOLEAN DEFAULT FALSE,
    has_power_connected BOOLEAN DEFAULT FALSE,
    
    -- Status
    is_loaded BOOLEAN DEFAULT FALSE,
    is_discharged BOOLEAN DEFAULT FALSE,
    loaded_at TIMESTAMP WITH TIME ZONE,
    discharged_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(stowage_plan_id, container_id),
    UNIQUE(stowage_plan_id, vessel_compartment_id),
    CONSTRAINT valid_position CHECK (bay_number > 0 AND row_number > 0 AND tier_number > 0)
);

CREATE INDEX idx_stowage_positions_plan ON stowage_positions(stowage_plan_id);
CREATE INDEX idx_stowage_positions_container ON stowage_positions(container_id);
CREATE INDEX idx_stowage_positions_compartment ON stowage_positions(vessel_compartment_id);
CREATE INDEX idx_stowage_positions_coords ON stowage_positions(bay_number, row_number, tier_number);

-- ============================================================================
-- Optimizations (Container Packing)
-- ============================================================================

CREATE TABLE optimizations (
    id SERIAL PRIMARY KEY,
    optimization_id UUID UNIQUE DEFAULT uuid_generate_v4(),
    
    -- Request data
    container_data JSONB NOT NULL,
    items_data JSONB NOT NULL,
    items_count INTEGER NOT NULL,
    
    -- Algorithm and parameters
    algorithm VARCHAR(50) NOT NULL,
    parameters JSONB,
    
    -- Status
    status optimization_status_enum DEFAULT 'pending',
    error_message TEXT,
    
    -- Results
    result_data JSONB,
    utilization_percentage NUMERIC(5,2),
    items_packed INTEGER,
    items_unpacked INTEGER,
    
    -- Performance
    computation_time_seconds NUMERIC(8,3),
    iterations INTEGER,
    fitness_score NUMERIC(8,4),
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- User reference
    created_by INTEGER REFERENCES users(id)
);

CREATE INDEX idx_optimizations_id ON optimizations(optimization_id);
CREATE INDEX idx_optimizations_status ON optimizations(status);
CREATE INDEX idx_optimizations_created_at ON optimizations(created_at DESC);
CREATE INDEX idx_optimizations_created_by ON optimizations(created_by);

-- ============================================================================
-- Placements (Optimization Results)
-- ============================================================================

CREATE TABLE placements (
    id SERIAL PRIMARY KEY,
    optimization_id UUID NOT NULL REFERENCES optimizations(optimization_id) ON DELETE CASCADE,
    
    -- Item reference
    item_index INTEGER NOT NULL,
    item_name VARCHAR(200),
    
    -- Position (in mm from origin)
    position_x NUMERIC(10,2) NOT NULL,
    position_y NUMERIC(10,2) NOT NULL,
    position_z NUMERIC(10,2) NOT NULL,
    
    -- Dimensions after rotation (in mm)
    length NUMERIC(10,2) NOT NULL,
    width NUMERIC(10,2) NOT NULL,
    height NUMERIC(10,2) NOT NULL,
    
    -- Orientation
    rotation INTEGER DEFAULT 0,
    
    -- Properties
    weight NUMERIC(10,2) NOT NULL,
    color VARCHAR(7),
    
    -- Stacking
    stacked_on INTEGER,
    weight_above NUMERIC(10,2) DEFAULT 0,
    
    -- Validation
    is_valid BOOLEAN DEFAULT TRUE,
    violations JSONB,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_placements_optimization ON placements(optimization_id);
CREATE INDEX idx_placements_item ON placements(item_index);

-- ============================================================================
-- Optimization Results History
-- ============================================================================

CREATE TABLE optimization_results (
    id SERIAL PRIMARY KEY,
    optimization_id UUID NOT NULL REFERENCES optimizations(optimization_id) ON DELETE CASCADE,
    stowage_plan_id INTEGER REFERENCES stowage_plans(id),
    
    -- Algorithm information
    algorithm_used VARCHAR(50) NOT NULL,
    algorithm_parameters JSONB,
    
    -- Performance metrics
    iterations INTEGER DEFAULT 0,
    computation_time NUMERIC(8,2) DEFAULT 0,
    fitness_score NUMERIC(8,4) DEFAULT 0,
    
    -- Results
    best_solution JSONB,
    convergence_data JSONB,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_optimization_results_optimization ON optimization_results(optimization_id);
CREATE INDEX idx_optimization_results_plan ON optimization_results(stowage_plan_id);

-- ============================================================================
-- Hazardous Materials Constraints
-- ============================================================================

CREATE TABLE hazardous_constraints (
    id SERIAL PRIMARY KEY,
    imdg_class VARCHAR(10) NOT NULL,
    un_number VARCHAR(4),
    description TEXT NOT NULL,
    
    -- Segregation rules
    requires_segregation_from JSONB,
    minimum_distance INTEGER,
    cannot_be_under BOOLEAN DEFAULT FALSE,
    cannot_be_over BOOLEAN DEFAULT FALSE,
    
    -- Special handling
    requires_special_ventilation BOOLEAN DEFAULT FALSE,
    requires_temperature_control BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_hazardous_imdg ON hazardous_constraints(imdg_class);
CREATE INDEX idx_hazardous_un ON hazardous_constraints(un_number);

-- ============================================================================
-- Configurations
-- ============================================================================

CREATE TABLE configurations (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    data_type VARCHAR(20) DEFAULT 'string' CHECK (data_type IN ('string', 'integer', 'float', 'boolean', 'json')),
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_configurations_key ON configurations(config_key);

-- ============================================================================
-- Audit Log
-- ============================================================================

CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(100),
    record_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_table ON audit_log(table_name);
CREATE INDEX idx_audit_created ON audit_log(created_at DESC);

-- ============================================================================
-- Functions and Triggers
-- ============================================================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vessels_updated_at BEFORE UPDATE ON vessels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_containers_updated_at BEFORE UPDATE ON containers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_items_updated_at BEFORE UPDATE ON items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stowage_plans_updated_at BEFORE UPDATE ON stowage_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_optimizations_updated_at BEFORE UPDATE ON optimizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hazardous_updated_at BEFORE UPDATE ON hazardous_constraints
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_configurations_updated_at BEFORE UPDATE ON configurations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Calculate vessel utilization
CREATE OR REPLACE FUNCTION calculate_vessel_utilization(p_vessel_id INTEGER)
RETURNS TABLE(
    teu_used INTEGER,
    teu_capacity INTEGER,
    utilization_percentage NUMERIC(5,2),
    weight_used NUMERIC(12,2),
    weight_capacity NUMERIC(12,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(sp.id)::INTEGER as teu_used,
        v.teu_capacity,
        ROUND((COUNT(sp.id)::NUMERIC / v.teu_capacity * 100), 2) as utilization_percentage,
        COALESCE(SUM(c.gross_weight), 0) as weight_used,
        v.deadweight_tonnage * 1000 as weight_capacity
    FROM vessels v
    LEFT JOIN stowage_positions sp ON v.id = (
        SELECT vessel_id FROM stowage_plans WHERE id = sp.stowage_plan_id LIMIT 1
    )
    LEFT JOIN containers c ON sp.container_id = c.id
    WHERE v.id = p_vessel_id
    GROUP BY v.id, v.teu_capacity, v.deadweight_tonnage;
END;
$$ LANGUAGE plpgsql;

-- Generate stowage position code
CREATE OR REPLACE FUNCTION get_position_code(
    p_bay INTEGER,
    p_row INTEGER,
    p_tier INTEGER,
    p_above_deck BOOLEAN
)
RETURNS VARCHAR(6) AS $$
BEGIN
    RETURN LPAD(p_bay::TEXT, 2, '0') || 
           LPAD(p_row::TEXT, 2, '0') || 
           LPAD(CASE WHEN p_above_deck THEN p_tier ELSE p_tier + 80 END::TEXT, 2, '0');
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Views
-- ============================================================================

-- Active stowage plans view
CREATE OR REPLACE VIEW v_active_stowage_plans AS
SELECT 
    sp.*,
    v.name as vessel_name,
    v.imo_number,
    u.username as created_by_username,
    COUNT(spos.id) as positions_count
FROM stowage_plans sp
JOIN vessels v ON sp.vessel_id = v.id
LEFT JOIN users u ON sp.created_by = u.id
LEFT JOIN stowage_positions spos ON sp.id = spos.stowage_plan_id
WHERE sp.status IN ('draft', 'optimizing', 'completed')
GROUP BY sp.id, v.name, v.imo_number, u.username;

-- Container inventory view
CREATE OR REPLACE VIEW v_container_inventory AS
SELECT 
    c.*,
    sp.plan_number,
    sp.vessel_id,
    v.name as vessel_name,
    spos.bay_number,
    spos.row_number,
    spos.tier_number,
    spos.is_above_deck
FROM containers c
LEFT JOIN stowage_positions spos ON c.id = spos.container_id AND spos.is_loaded = TRUE
LEFT JOIN stowage_plans sp ON spos.stowage_plan_id = sp.id
LEFT JOIN vessels v ON sp.vessel_id = v.id;

-- Optimization statistics view
CREATE OR REPLACE VIEW v_optimization_statistics AS
SELECT 
    DATE_TRUNC('day', started_at) as date,
    COUNT(*) as total_optimizations,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
    AVG(CASE WHEN status = 'completed' THEN utilization_percentage END) as avg_utilization,
    AVG(CASE WHEN status = 'completed' THEN computation_time_seconds END) as avg_computation_time
FROM optimizations
GROUP BY DATE_TRUNC('day', started_at)
ORDER BY date DESC;

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE vessels IS 'Vessel specifications and characteristics';
COMMENT ON TABLE vessel_compartments IS 'Vessel compartments for container stowage';
COMMENT ON TABLE containers IS 'Container specifications and cargo information';
COMMENT ON TABLE items IS 'Items for container packing optimization';
COMMENT ON TABLE stowage_plans IS 'Container stowage plans and optimization results';
COMMENT ON TABLE stowage_positions IS 'Individual container positions within stowage plans';
COMMENT ON TABLE optimizations IS 'Container packing optimization requests and results';
COMMENT ON TABLE placements IS 'Item placements from optimization results';
COMMENT ON TABLE optimization_results IS 'Optimization algorithm performance and results';
COMMENT ON TABLE hazardous_constraints IS 'Hazardous materials handling constraints and segregation rules';
COMMENT ON TABLE configurations IS 'System configuration parameters';
COMMENT ON TABLE audit_log IS 'Audit trail of system actions';

-- ============================================================================
-- Grants (adjust as needed for your security requirements)
-- ============================================================================

-- Grant basic permissions to application role
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO cargoopt_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO cargoopt_app;

-- Grant read-only access to reporting role
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO cargoopt_readonly;