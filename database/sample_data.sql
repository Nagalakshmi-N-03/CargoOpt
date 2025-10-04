-- CargoOpt Sample Data
-- Sample data for development and testing

-- Insert sample vessels
INSERT INTO vessels (
    imo_number, name, call_sign, flag, vessel_type,
    length_overall, breadth, depth, draft_design, draft_max,
    deadweight_tonnage, gross_tonnage, net_tonnage, teu_capacity, reefer_plugs,
    number_of_holds, number_of_hatches, service_speed, max_speed,
    gm_min, gm_max, trim_max, built_year, builder
) VALUES 
(
    '9876543', 'MV Sea Explorer', 'SEXP7', 'Panama', 'container_ship',
    300.00, 40.00, 24.50, 12.00, 14.50,
    85000.00, 75000.00, 45000.00, 8000, 1200,
    8, 16, 22.5, 24.8,
    1.2, 3.5, 2.0, 2018, 'Hyundai Heavy Industries'
),
(
    '9876544', 'MV Ocean Carrier', 'OCAR5', 'Liberia', 'container_ship',
    250.00, 32.40, 19.80, 10.50, 12.80,
    45000.00, 38000.00, 22000.00, 4500, 600,
    6, 12, 20.0, 22.5,
    0.8, 2.8, 1.8, 2015, 'Samsung Heavy Industries'
);

-- Insert sample vessel compartments for MV Sea Explorer
INSERT INTO vessel_compartments (
    vessel_id, bay_number, row_number, tier_number,
    length, width, height, max_weight,
    can_accommodate_reefer, can_accommodate_hazardous, has_power_supply
)
SELECT 
    v.id, 
    bays.bay, 
    rows.row, 
    tiers.tier,
    6.10, 2.44, 2.59, 30000.00,  -- Standard container slot dimensions
    (rows.row IN (1, 8)),         -- Reefer plugs on sides
    TRUE,                         -- All compartments can handle hazardous
    (rows.row IN (1, 8))          -- Power on sides for reefers
FROM vessels v,
     generate_series(1, 20) as bays(bay),
     generate_series(1, 8) as rows(row),
     generate_series(1, 6) as tiers(tier)
WHERE v.imo_number = '9876543'
  AND tiers.tier <= 6;  -- Only 6 tiers high

-- Insert sample containers
INSERT INTO containers (
    container_number, iso_code, length, width, height,
    tare_weight, max_payload, container_type, status,
    cargo_description, cargo_weight, imdg_class, un_number,
    is_reefer, reefer_temperature, is_oversized
) VALUES
-- Standard 20ft dry containers
('MSKU1234567', '22G1', 20.0, 8.0, 8.5, 2200.00, 28200.00, 'dry', 'loaded', 'Electronics', 15000.00, NULL, NULL, FALSE, NULL, FALSE),
('MSKU1234568', '22G1', 20.0, 8.0, 8.5, 2250.00, 28150.00, 'dry', 'loaded', 'Textiles', 12000.00, NULL, NULL, FALSE, NULL, FALSE),
('MSKU1234569', '22G1', 20.0, 8.0, 8.5, 2300.00, 28100.00, 'dry', 'loaded', 'Furniture', 18000.00, NULL, NULL, FALSE, NULL, FALSE),

-- Standard 40ft dry containers
('MSKU1234570', '42G1', 40.0, 8.0, 8.5, 3700.00, 28400.00, 'dry', 'loaded', 'Automotive Parts', 20000.00, NULL, NULL, FALSE, NULL, FALSE),
('MSKU1234571', '42G1', 40.0, 8.0, 8.5, 3750.00, 28350.00, 'dry', 'loaded', 'Machinery', 22000.00, NULL, NULL, FALSE, NULL, FALSE),

-- Reefer containers
('MSKU1234572', '22R1', 20.0, 8.0, 8.5, 2800.00, 27600.00, 'reefer', 'loaded', 'Frozen Food', 15000.00, NULL, NULL, TRUE, -18.0, FALSE),
('MSKU1234573', '42R1', 40.0, 8.0, 8.5, 4200.00, 27800.00, 'reefer', 'loaded', 'Pharmaceuticals', 18000.00, NULL, NULL, TRUE, 2.0, FALSE),

-- Hazardous containers
('MSKU1234574', '22G1', 20.0, 8.0, 8.5, 2400.00, 28000.00, 'hazardous', 'loaded', 'Flammable Liquids', 12000.00, '3', '1263', FALSE, NULL, FALSE),
('MSKU1234575', '22G1', 20.0, 8.0, 8.5, 2450.00, 27950.00, 'hazardous', 'loaded', 'Corrosive Materials', 10000.00, '8', '1760', FALSE, NULL, FALSE),

-- High cube containers
('MSKU1234576', '45G1', 40.0, 8.0, 9.5, 3850.00, 28150.00, 'high_cube', 'loaded', 'Light Goods', 8000.00, NULL, NULL, FALSE, NULL, FALSE),

-- Open top containers
('MSKU1234577', '22U1', 20.0, 8.0, 8.5, 2500.00, 27900.00, 'open_top', 'loaded', 'Oversized Machinery', 15000.00, NULL, NULL, FALSE, NULL, TRUE),

-- Empty containers
('MSKU1234578', '22G1', 20.0, 8.0, 8.5, 2200.00, 28200.00, 'dry', 'empty', NULL, NULL, NULL, NULL, FALSE, NULL, FALSE),
('MSKU1234579', '42G1', 40.0, 8.0, 8.5, 3700.00, 28400.00, 'dry', 'empty', NULL, NULL, NULL, NULL, FALSE, NULL, FALSE);

-- Insert hazardous constraints
INSERT INTO hazardous_constraints (
    imdg_class, un_number, description, requires_segregation_from,
    minimum_distance, cannot_be_under, cannot_be_over,
    requires_special_ventilation, requires_temperature_control
) VALUES
('1', NULL, 'Explosives', '["3", "5", "8"]', 5, TRUE, TRUE, TRUE, FALSE),
('2', NULL, 'Gases', '["5", "8"]', 3, FALSE, TRUE, TRUE, TRUE),
('3', NULL, 'Flammable Liquids', '["1", "5", "6", "7"]', 2, FALSE, FALSE, TRUE, FALSE),
('4', NULL, 'Flammable Solids', '["5", "6", "7"]', 2, FALSE, FALSE, FALSE, FALSE),
('5', NULL, 'Oxidizing Substances', '["1", "3", "4", "6", "7", "8"]', 3, FALSE, FALSE, FALSE, FALSE),
('6', NULL, 'Toxic Substances', '["3", "4", "5", "7", "8"]', 2, FALSE, FALSE, TRUE, FALSE),
('7', NULL, 'Radioactive Materials', '["1", "3", "4", "5", "6", "8"]', 4, TRUE, TRUE, FALSE, FALSE),
('8', NULL, 'Corrosive Substances', '["1", "3", "5", "6", "7"]', 2, FALSE, FALSE, TRUE, FALSE),
('9', NULL, 'Miscellaneous Dangerous Goods', '[]', 1, FALSE, FALSE, FALSE, FALSE);

-- Insert sample stowage plan
INSERT INTO stowage_plans (
    plan_name, description, vessel_id, status,
    total_containers, total_weight, teu_utilization,
    stability_score, efficiency_score,
    gm_actual, trim_actual, list_actual,
    created_by
) VALUES (
    'Voyage-2024-001',
    'Sample stowage plan for MV Sea Explorer - Singapore to Rotterdam',
    (SELECT id FROM vessels WHERE imo_number = '9876543'),
    'completed',
    Get-Content database\sample_data.sql | Select-Object -Index 108,109,110,111,112,113