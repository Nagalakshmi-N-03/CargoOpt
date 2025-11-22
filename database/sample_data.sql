-- CargoOpt Sample Data
-- Sample data for development and testing

-- ============================================================================
-- Users
-- ============================================================================

INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active) VALUES
('admin', 'admin@cargoopt.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILSL.lCB6', 'Admin', 'User', 'admin', TRUE),
('captain_smith', 'smith@shipping.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILSL.lCB6', 'John', 'Smith', 'user', TRUE),
('planner_jane', 'jane@logistics.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILSL.lCB6', 'Jane', 'Doe', 'user', TRUE),
('viewer_bob', 'bob@cargoopt.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILSL.lCB6', 'Bob', 'Wilson', 'viewer', TRUE);

-- Note: Password for all users is 'password123' (hashed with bcrypt)

-- ============================================================================
-- Vessels
-- ============================================================================

INSERT INTO vessels (
    imo_number, name, call_sign, flag, vessel_type, classification_society,
    length_overall, breadth, depth, draft_design, draft_max,
    deadweight_tonnage, gross_tonnage, net_tonnage, teu_capacity, reefer_plugs,
    number_of_holds, number_of_hatches,
    service_speed, max_speed,
    gm_min, gm_max, trim_max,
    built_year, builder
) VALUES
(
    '9876543', 'MV Pacific Star', 'VRTP9', 'Panama', 'container_ship', 'Lloyds Register',
    294.0, 32.2, 19.0, 12.0, 13.5,
    50000, 40000, 25000, 4500, 300,
    7, 7,
    22.0, 24.5,
    1.5, 3.5, 1.0,
    2015, 'Hyundai Heavy Industries'
),
(
    '9123456', 'MV Atlantic Express', 'C6AB2', 'Liberia', 'container_ship', 'DNV GL',
    366.0, 48.2, 24.0, 14.5, 16.0,
    120000, 95000, 60000, 12000, 500,
    11, 11,
    24.0, 26.0,
    2.0, 4.0, 1.2,
    2018, 'Daewoo Shipbuilding'
),
(
    '9345678', 'MV Nordic Breeze', 'LABB7', 'Norway', 'container_ship', 'ABS',
    135.0, 23.0, 12.5, 8.0, 9.5,
    15000, 10000, 6000, 1000, 100,
    4, 4,
    18.0, 20.0,
    1.2, 2.8, 0.8,
    2012, 'Fincantieri'
);

-- ============================================================================
-- Vessel Compartments (Sample for first vessel)
-- ============================================================================

-- Generate compartments for MV Pacific Star (vessel_id = 1)
-- 20 bays, 13 rows, 6 tiers above deck, 8 tiers below deck

DO $$
DECLARE
    v_vessel_id INTEGER := 1;
    v_bay INTEGER;
    v_row INTEGER;
    v_tier INTEGER;
BEGIN
    -- Above deck compartments
    FOR v_bay IN 1..20 LOOP
        FOR v_row IN 1..13 LOOP
            FOR v_tier IN 1..6 LOOP
                INSERT INTO vessel_compartments (
                    vessel_id, bay_number, row_number, tier_number, is_above_deck,
                    length, width, height, max_weight,
                    can_accommodate_reefer, has_power_supply
                ) VALUES (
                    v_vessel_id, v_bay, v_row, v_tier, TRUE,
                    6.058, 2.438, 2.591, 30000,
                    (v_row <= 3), (v_row <= 3)
                );
            END LOOP;
        END LOOP;
    END LOOP;
    
    -- Below deck compartments
    FOR v_bay IN 1..20 LOOP
        FOR v_row IN 1..13 LOOP
            FOR v_tier IN 1..8 LOOP
                INSERT INTO vessel_compartments (
                    vessel_id, bay_number, row_number, tier_number, is_above_deck,
                    length, width, height, max_weight,
                    can_accommodate_reefer, has_power_supply
                ) VALUES (
                    v_vessel_id, v_bay, v_row, v_tier, FALSE,
                    6.058, 2.438, 2.591, 30000,
                    (v_row <= 3), (v_row <= 3)
                );
            END LOOP;
        END LOOP;
    END LOOP;
END $$;

-- ============================================================================
-- Containers
-- ============================================================================

INSERT INTO containers (
    container_number, iso_code, length, width, height, tare_weight, max_payload, cargo_weight,
    container_type, status, cargo_description, imdg_class, un_number,
    is_reefer, reefer_temperature, current_location, destination_port
) VALUES
-- Standard 20ft containers
('CSQU3054383', '22G1', 20, 8, 8.5, 2300, 28180, 15000, 'dry', 'loaded', 'Consumer Electronics', NULL, NULL, FALSE, NULL, 'Shanghai', 'Los Angeles'),
('TCLU7200987', '22G1', 20, 8, 8.5, 2300, 28180, 22000, 'dry', 'loaded', 'Automotive Parts', NULL, NULL, FALSE, NULL, 'Shanghai', 'Los Angeles'),
('CBHU1234567', '22G1', 20, 8, 8.5, 2300, 28180, 18500, 'dry', 'loaded', 'Textiles', NULL, NULL, FALSE, NULL, 'Shanghai', 'Los Angeles'),

-- Standard 40ft containers
('MSCU6543210', '42G1', 40, 8, 8.5, 3800, 26680, 20000, 'dry', 'loaded', 'Furniture', NULL, NULL, FALSE, NULL, 'Shanghai', 'Rotterdam'),
('HLXU9876543', '42G1', 40, 8, 8.5, 3800, 26680, 24000, 'dry', 'loaded', 'Machinery', NULL, NULL, FALSE, NULL, 'Shanghai', 'Rotterdam'),

-- High cube 40ft containers
('TRLU5678901', '45G1', 40, 8, 9.5, 3920, 26560, 19000, 'high_cube', 'loaded', 'Plastics', NULL, NULL, FALSE, NULL, 'Ningbo', 'Hamburg'),
('APZU4567890', '45G1', 40, 8, 9.5, 3920, 26560, 21000, 'high_cube', 'loaded', 'Paper Products', NULL, NULL, FALSE, NULL, 'Ningbo', 'Hamburg'),

-- Reefer containers
('MAEU8901234', '22R1', 20, 8, 8.5, 3080, 27400, 12000, 'reefer', 'loaded', 'Fresh Fruits', NULL, NULL, TRUE, 5.0, 'Bangkok', 'Dubai'),
('CMAU3456789', '42R1', 40, 8, 8.5, 4800, 26960, 18000, 'reefer', 'loaded', 'Frozen Seafood', NULL, NULL, TRUE, -18.0, 'Bangkok', 'Dubai'),
('GESU2345678', '22R1', 20, 8, 8.5, 3080, 27400, 14000, 'reefer', 'loaded', 'Pharmaceuticals', NULL, NULL, TRUE, 2.0, 'Singapore', 'London'),

-- Hazardous containers
('TEMU9012345', '22G1', 20, 8, 8.5, 2300, 28180, 16000, 'hazardous', 'loaded', 'Chemicals - Class 8', '8', '1830', FALSE, NULL, 'Busan', 'Vancouver'),
('OOLU7890123', '22G1', 20, 8, 8.5, 2300, 28180, 17000, 'hazardous', 'loaded', 'Flammable Liquids', '3', '1263', FALSE, NULL, 'Busan', 'Vancouver'),

-- Open top containers
('MSCU1122334', '22U1', 20, 8, 8.5, 2360, 28120, 20000, 'open_top', 'loaded', 'Construction Materials', NULL, NULL, FALSE, NULL, 'Mumbai', 'Jeddah'),

-- Empty containers
('TCKU4455667', '22G1', 20, 8, 8.5, 2300, 28180, 0, 'dry', 'empty', NULL, NULL, NULL, FALSE, NULL, 'Singapore', NULL),
('CSNU7788990', '42G1', 40, 8, 8.5, 3800, 26680, 0, 'dry', 'empty', NULL, NULL, NULL, FALSE, NULL, 'Hong Kong', NULL);

-- ============================================================================
-- Items (for container packing optimization)
-- ============================================================================

INSERT INTO items (
    item_id, name, length, width, height, weight,
    item_type, storage_condition, is_fragile, is_stackable, max_stack_weight,
    rotation_allowed, keep_upright, priority, color, description
) VALUES
-- Electronics
('ITEM001', 'Laptop Box', 400, 300, 50, 2.5, 'electronics', 'standard', TRUE, TRUE, 50, TRUE, FALSE, 1, '#4169E1', 'Packaged laptop computers'),
('ITEM002', 'TV Set Large', 1200, 800, 150, 25.0, 'electronics', 'standard', TRUE, FALSE, 0, FALSE, TRUE, 1, '#4169E1', '55 inch television'),
('ITEM003', 'Mobile Phone Case', 200, 150, 100, 0.5, 'electronics', 'standard', TRUE, TRUE, 100, TRUE, FALSE, 2, '#4169E1', 'Smartphone shipping box'),

-- Furniture
('ITEM004', 'Dining Chair', 500, 500, 1000, 8.0, 'wood', 'standard', FALSE, TRUE, 80, FALSE, TRUE, 3, '#8B4513', 'Wooden dining chair'),
('ITEM005', 'Table Top', 1500, 800, 50, 30.0, 'wood', 'standard', FALSE, TRUE, 200, TRUE, FALSE, 3, '#8B4513', 'Wooden table top'),
('ITEM006', 'Office Desk', 1400, 700, 750, 45.0, 'wood', 'standard', FALSE, FALSE, 0, FALSE, TRUE, 4, '#8B4513', 'Office desk assembly'),

-- Textiles
('ITEM007', 'Fabric Roll', 1000, 400, 400, 15.0, 'textiles', 'standard', FALSE, TRUE, 150, TRUE, FALSE, 5, '#DDA0DD', 'Rolled fabric material'),
('ITEM008', 'Clothing Box', 600, 400, 300, 5.0, 'textiles', 'standard', FALSE, TRUE, 100, TRUE, FALSE, 5, '#DDA0DD', 'Packaged clothing'),
('ITEM009', 'Bedding Set', 800, 600, 200, 3.0, 'textiles', 'standard', FALSE, TRUE, 120, TRUE, FALSE, 5, '#DDA0DD', 'Bed linens and covers'),

-- Food items
('ITEM010', 'Canned Goods Case', 400, 300, 250, 12.0, 'food', 'standard', FALSE, TRUE, 200, TRUE, FALSE, 4, '#FFA500', 'Case of canned food'),
('ITEM011', 'Rice Bag', 800, 500, 150, 25.0, 'food', 'standard', FALSE, TRUE, 150, TRUE, FALSE, 4, '#FFA500', '25kg rice bag'),
('ITEM012', 'Frozen Food Box', 500, 400, 300, 10.0, 'food', 'frozen', FALSE, TRUE, 100, TRUE, FALSE, 2, '#FFA500', 'Frozen food products'),

-- Chemicals
('ITEM013', 'Chemical Drum', 600, 600, 900, 200.0, 'chemicals', 'hazardous', FALSE, TRUE, 400, FALSE, TRUE, 1, '#FF4500', 'Industrial chemical container'),
('ITEM014', 'Paint Can Large', 400, 400, 500, 20.0, 'chemicals', 'standard', FALSE, TRUE, 150, FALSE, TRUE, 3, '#FF4500', 'Paint can 20L'),

-- Glass items
('ITEM015', 'Glass Sheets', 1200, 900, 50, 40.0, 'glass', 'standard', TRUE, FALSE, 0, FALSE, TRUE, 1, '#87CEEB', 'Tempered glass sheets'),
('ITEM016', 'Wine Bottles Case', 300, 300, 350, 15.0, 'glass', 'standard', TRUE, TRUE, 60, FALSE, TRUE, 2, '#87CEEB', 'Case of wine bottles'),

-- Metal parts
('ITEM017', 'Steel Pipe', 3000, 200, 200, 50.0, 'metal', 'standard', FALSE, TRUE, 500, TRUE, FALSE, 5, '#708090', 'Steel pipe section'),
('ITEM018', 'Metal Sheet', 2000, 1000, 10, 80.0, 'metal', 'standard', FALSE, TRUE, 600, TRUE, FALSE, 5, '#708090', 'Flat metal sheet'),
('ITEM019', 'Machinery Part', 800, 600, 400, 120.0, 'metal', 'standard', FALSE, FALSE, 0, FALSE, FALSE, 3, '#708090', 'Heavy machinery component'),

-- Plastic items
('ITEM020', 'Plastic Crate', 600, 400, 300, 2.0, 'plastic', 'standard', FALSE, TRUE, 150, TRUE, FALSE, 5, '#FFB6C1', 'Stackable plastic crate'),
('ITEM021', 'PVC Pipes Bundle', 2500, 300, 300, 25.0, 'plastic', 'standard', FALSE, TRUE, 200, TRUE, FALSE, 4, '#FFB6C1', 'Bundle of PVC pipes'),

-- Refrigerated items
('ITEM022', 'Fresh Produce Box', 500, 400, 300, 20.0, 'food', 'refrigerated', FALSE, TRUE, 100, TRUE, FALSE, 1, '#FFA500', 'Fresh fruits and vegetables'),
('ITEM023', 'Dairy Products', 400, 300, 300, 15.0, 'food', 'refrigerated', FALSE, TRUE, 80, FALSE, TRUE, 1, '#FFA500', 'Milk and dairy products'),

-- Other/Miscellaneous
('ITEM024', 'Cardboard Boxes', 500, 400, 400, 1.0, 'other', 'standard', FALSE, TRUE, 200, TRUE, FALSE, 5, '#A9A9A9', 'Empty cardboard boxes'),
('ITEM025', 'Industrial Equipment', 1500, 1000, 1200, 350.0, 'other', 'standard', FALSE, FALSE, 0, FALSE, TRUE, 2, '#A9A9A9', 'Heavy industrial equipment');

-- ============================================================================
-- Hazardous Constraints
-- ============================================================================

INSERT INTO hazardous_constraints (
    imdg_class, description, requires_segregation_from, minimum_distance,
    cannot_be_under, cannot_be_over,
    requires_special_ventilation, requires_temperature_control
) VALUES
('1', 'Explosives', '["1", "2.1", "3", "4.1", "4.2", "4.3", "5.1", "5.2", "8"]', 2, TRUE, FALSE, TRUE, FALSE),
('2.1', 'Flammable Gas', '["1", "3", "4.1", "4.2", "4.3", "5.1", "5.2"]', 1, FALSE, FALSE, TRUE, FALSE),
('2.2', 'Non-Flammable Gas', '[]', 0, FALSE, FALSE, TRUE, FALSE),
('2.3', 'Toxic Gas', '["3", "4.1", "6.1", "8"]', 1, FALSE, FALSE, TRUE, FALSE),
('3', 'Flammable Liquid', '["1", "2.1", "4.1", "5.1", "8"]', 1, FALSE, FALSE, TRUE, FALSE),
('4.1', 'Flammable Solid', '["1", "2.1", "3", "5.1", "5.2"]', 1, FALSE, FALSE, FALSE, FALSE),
('4.2', 'Spontaneous Combustion', '["1", "2.1", "5.1", "5.2", "8"]', 2, FALSE, FALSE, TRUE, FALSE),
('4.3', 'Dangerous When Wet', '["3", "5.1", "8"]', 1, FALSE, FALSE, FALSE, FALSE),
('5.1', 'Oxidizer', '["1", "3", "4.1", "4.2", "4.3"]', 1, FALSE, FALSE, FALSE, FALSE),
('5.2', 'Organic Peroxide', '["1", "2.1", "4.1", "4.2"]', 2, FALSE, FALSE, TRUE, TRUE),
('6.1', 'Toxic', '["2.3", "3", "8"]', 1, FALSE, FALSE, FALSE, FALSE),
('6.2', 'Infectious', '[]', 1, TRUE, FALSE, TRUE, TRUE),
('7', 'Radioactive', '[]', 2, TRUE, FALSE, TRUE, FALSE),
('8', 'Corrosive', '["1", "2.3", "3", "4.2", "4.3"]', 1, FALSE, FALSE, TRUE, FALSE),
('9', 'Miscellaneous', '[]', 0, FALSE, FALSE, FALSE, FALSE);

-- ============================================================================
-- Configurations
-- ============================================================================

INSERT INTO configurations (config_key, config_value, data_type, description, is_public) VALUES
('ga_population_size', '100', 'integer', 'Genetic algorithm population size', TRUE),
('ga_generations', '50', 'integer', 'Genetic algorithm number of generations', TRUE),
('ga_mutation_rate', '0.15', 'float', 'Genetic algorithm mutation rate', TRUE),
('ga_crossover_rate', '0.85', 'float', 'Genetic algorithm crossover rate', TRUE),
('max_computation_time', '300', 'integer', 'Maximum optimization computation time in seconds', TRUE),
('weight_utilization', '0.4', 'float', 'Weight for utilization in fitness function', TRUE),
('weight_stability', '0.25', 'float', 'Weight for stability in fitness function', TRUE),
('weight_constraints', '0.25', 'float', 'Weight for constraints in fitness function', TRUE),
('weight_accessibility', '0.1', 'float', 'Weight for accessibility in fitness function', TRUE),
('min_support_percentage', '0.6', 'float', 'Minimum support percentage required from below', TRUE),
('system_name', 'CargoOpt', 'string', 'System name', TRUE),
('system_version', '1.0.0', 'string', 'System version', TRUE),
('enable_parallel_processing', 'true', 'boolean', 'Enable parallel processing for optimizations', TRUE),
('default_algorithm', 'genetic', 'string', 'Default optimization algorithm', TRUE);

-- ============================================================================
-- Sample Stowage Plan
-- ============================================================================

INSERT INTO stowage_plans (
    plan_number, plan_name, description, vessel_id, created_by,
    loading_port, discharge_port, voyage_number,
    estimated_departure, estimated_arrival,
    status, algorithm_used
) VALUES
('SP2024001', 'Shanghai to LA - January 2024', 'Regular route cargo', 1, 2,
'Shanghai', 'Los Angeles', 'VOY-2024-01',
'2024-01-15 08:00:00+00', '2024-01-28 16:00:00+00',
'draft', 'genetic_algorithm');

-- Add some sample positions for the stowage plan
INSERT INTO stowage_positions (
    stowage_plan_id, container_id, vessel_compartment_id,
    bay_number, row_number, tier_number, is_above_deck,
    position_x, position_y, position_z, rotation, load_sequence
)
SELECT 
    1, -- stowage_plan_id
    c.id,
    vc.id,
    vc.bay_number,
    vc.row_number,
    vc.tier_number,
    vc.is_above_deck,
    (vc.bay_number - 1) * 6058, -- position_x in mm
    (vc.row_number - 1) * 2438, -- position_y in mm
    CASE WHEN vc.is_above_deck THEN (vc.tier_number - 1) * 2591 ELSE -((vc.tier_number) * 2591) END, -- position_z
    0, -- rotation
    ROW_NUMBER() OVER (ORDER BY vc.bay_number, vc.row_number, vc.tier_number)
FROM containers c
CROSS JOIN LATERAL (
    SELECT * FROM vessel_compartments 
    WHERE vessel_id = 1 AND is_occupied = FALSE
    LIMIT 1 OFFSET (c.id - 1)
) vc
WHERE c.status = 'loaded'
LIMIT 10;

-- Update stowage plan statistics
UPDATE stowage_plans SET
    total_containers = (SELECT COUNT(*) FROM stowage_positions WHERE stowage_plan_id = 1),
    total_weight = (SELECT SUM(c.gross_weight) FROM stowage_positions sp JOIN containers c ON sp.container_id = c.id WHERE sp.stowage_plan_id = 1)
WHERE id = 1;

-- ============================================================================
-- Sample Optimization Records
-- ============================================================================

INSERT INTO optimizations (
    optimization_id, container_data, items_data, items_count,
    algorithm, status, utilization_percentage, items_packed, items_unpacked,
    computation_time_seconds, iterations, fitness_score,
    started_at, completed_at, created_by
) VALUES
(
    uuid_generate_v4(),
    '{"length": 12032, "width": 2352, "height": 2393, "max_weight": 26680, "container_type": "40ft"}',
    '[{"item_id": "TEST001", "length": 1000, "width": 800, "height": 600, "weight": 50}]',
    1,
    'genetic',
    'completed',
    78.5,
    1,
    0,
    45.234,
    50,
    0.8234,
    NOW() - INTERVAL '2 days',
    NOW() - INTERVAL '2 days' + INTERVAL '45 seconds',
    2
);

-- ============================================================================
-- Sample Audit Log Entries
-- ============================================================================

INSERT INTO audit_log (user_id, action, table_name, record_id, ip_address) VALUES
(1, 'LOGIN', NULL, NULL, '192.168.1.100'),
(2, 'CREATE', 'stowage_plans', 1, '192.168.1.101'),
(2, 'UPDATE', 'stowage_plans', 1, '192.168.1.101'),
(3, 'CREATE', 'optimizations', 1, '192.168.1.102');

-- ============================================================================
-- Verify Data
-- ============================================================================

-- Show summary of inserted data
DO $$
DECLARE
    v_users INTEGER;
    v_vessels INTEGER;
    v_containers INTEGER;
    v_items INTEGER;
    v_plans INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_users FROM users;
    SELECT COUNT(*) INTO v_vessels FROM vessels;
    SELECT COUNT(*) INTO v_containers FROM containers;
    SELECT COUNT(*) INTO v_items FROM items;
    SELECT COUNT(*) INTO v_plans FROM stowage_plans;
    
    RAISE NOTICE 'Sample data inserted successfully:';
    RAISE NOTICE '  Users: %', v_users;
    RAISE NOTICE '  Vessels: %', v_vessels;
    RAISE NOTICE '  Containers: %', v_containers;
    RAISE NOTICE '  Items: %', v_items;
    RAISE NOTICE '  Stowage Plans: %', v_plans;
END $$;