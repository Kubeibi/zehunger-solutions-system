-- Create the database
CREATE DATABASE IF NOT EXISTS bsf_farm;
USE bsf_farm;

-- Users table for system access
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    role ENUM('admin', 'manager', 'technician', 'viewer') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Waste Sources
CREATE TABLE waste_sources (
    source_id INT AUTO_INCREMENT PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    source_type ENUM('restaurant', 'market', 'brewery', 'food_industry', 'household', 'farm', 'other') NOT NULL,
    contact_person VARCHAR(100),
    contact_phone VARCHAR(20),
    address TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP
);

-- Waste Collections
CREATE TABLE waste_collections (
    collection_id INT AUTO_INCREMENT PRIMARY KEY,
    source_id INT NOT NULL,
    collection_date DATE NOT NULL,
    collection_time TIME NOT NULL,
    waste_type ENUM('fruit', 'vegetable', 'brewers_grain', 'potato', 'food_leftovers', 'mixed_organic', 'other') NOT NULL,
    weight_kg DECIMAL(10,2) NOT NULL,
    segregation_status ENUM('organic', 'inorganic', 'mixed') NOT NULL,
    collection_personnel VARCHAR(100) NOT NULL,
    contaminants JSON, -- Array of contaminants
    notes TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES waste_sources(source_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Storage Units
CREATE TABLE storage_units (
    unit_id INT AUTO_INCREMENT PRIMARY KEY,
    unit_name VARCHAR(50) NOT NULL,
    unit_type ENUM('plastic_bin', 'metal_bin', 'compost_pit', 'tank', 'other') NOT NULL,
    capacity_kg DECIMAL(10,2),
    location VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Waste Storage
CREATE TABLE waste_storage (
    storage_id INT AUTO_INCREMENT PRIMARY KEY,
    collection_id INT NOT NULL,
    unit_id INT NOT NULL,
    storage_date DATE NOT NULL,
    storage_time TIME NOT NULL,
    storage_conditions ENUM('good', 'fair', 'poor', 'contaminated') NOT NULL,
    duration_days INT NOT NULL,
    planned_utilization ENUM('feed', 'fertilizer', 'energy', 'other') NOT NULL,
    person_responsible VARCHAR(100) NOT NULL,
    observations TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (collection_id) REFERENCES waste_collections(collection_id),
    FOREIGN KEY (unit_id) REFERENCES storage_units(unit_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Processing Records
CREATE TABLE processing_records (
    processing_id INT AUTO_INCREMENT PRIMARY KEY,
    storage_id INT NOT NULL,
    processing_date DATE NOT NULL,
    processing_time TIME NOT NULL,
    processing_type ENUM('composting', 'drying', 'fermentation', 'grinding', 'mixing', 'other') NOT NULL,
    processing_method VARCHAR(100) NOT NULL,
    waste_processed_kg DECIMAL(10,2) NOT NULL,
    by_products VARCHAR(255),
    waste_reduction_percent DECIMAL(5,2),
    person_responsible VARCHAR(100) NOT NULL,
    observations TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (storage_id) REFERENCES waste_storage(storage_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Environmental Monitoring (Waste)
CREATE TABLE environmental_monitoring_waste (
    monitoring_id INT AUTO_INCREMENT PRIMARY KEY,
    monitoring_date DATE NOT NULL,
    monitoring_time TIME NOT NULL,
    location VARCHAR(100) NOT NULL,
    temperature_c DECIMAL(5,2) NOT NULL,
    humidity_percent DECIMAL(5,2) NOT NULL,
    odor_level ENUM('none', 'slight', 'moderate', 'strong', 'very_strong') NOT NULL,
    pest_presence ENUM('none', 'slight', 'moderate', 'severe') NOT NULL,
    pest_details TEXT,
    mitigation_actions TEXT,
    remarks TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Substrate Batches
CREATE TABLE substrate_batches (
    batch_id INT AUTO_INCREMENT PRIMARY KEY,
    batch_number VARCHAR(50) NOT NULL UNIQUE,
    preparation_date DATE NOT NULL,
    organic_waste_source VARCHAR(100) NOT NULL,
    moisture_percent DECIMAL(5,2) NOT NULL,
    waste_particle_size ENUM('fine', 'medium', 'coarse') NOT NULL,
    foreign_matter ENUM('none', 'low', 'medium', 'high') NOT NULL,
    handler_operator VARCHAR(100) NOT NULL,
    notes TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Larval Feeding
CREATE TABLE larval_feeding (
    feeding_id INT AUTO_INCREMENT PRIMARY KEY,
    substrate_batch_id INT NOT NULL,
    feeding_date DATE NOT NULL,
    feeding_time TIME NOT NULL,
    feed_type ENUM('bsf_feed', 'other') NOT NULL,
    feed_quantity_kg DECIMAL(10,2) NOT NULL,
    larvae_age_days INT NOT NULL,
    larvae_weight_g DECIMAL(10,2) NOT NULL,
    consumption_rate_percent DECIMAL(5,2) NOT NULL,
    operator VARCHAR(100) NOT NULL,
    notes TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (substrate_batch_id) REFERENCES substrate_batches(batch_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Growth Monitoring
CREATE TABLE growth_monitoring (
    monitoring_id INT AUTO_INCREMENT PRIMARY KEY,
    substrate_batch_id INT NOT NULL,
    monitoring_date DATE NOT NULL,
    larvae_count INT,
    average_weight_g DECIMAL(10,2),
    development_stage ENUM('egg', 'instar1', 'instar2', 'instar3', 'instar4', 'instar5', 'prepupa', 'pupa', 'adult') NOT NULL,
    mortality_rate_percent DECIMAL(5,2),
    observations TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (substrate_batch_id) REFERENCES substrate_batches(batch_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Health & Intervention
CREATE TABLE health_intervention (
    intervention_id INT AUTO_INCREMENT PRIMARY KEY,
    substrate_batch_id INT NOT NULL,
    health_date DATE NOT NULL,
    tray_batch_id VARCHAR(50) NOT NULL,
    observed_issue VARCHAR(255) NOT NULL,
    severity ENUM('low', 'medium', 'high') NOT NULL,
    follow_up_date DATE,
    resolved ENUM('yes', 'no'),
    action_taken TEXT NOT NULL,
    comments TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (substrate_batch_id) REFERENCES substrate_batches(batch_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Harvest & Yield
CREATE TABLE harvest_yield (
    harvest_id INT AUTO_INCREMENT PRIMARY KEY,
    substrate_batch_id INT NOT NULL,
    harvest_date DATE NOT NULL,
    tray_batch_id VARCHAR(50) NOT NULL,
    instar_stage ENUM('1', '2', '3', '4', '5') NOT NULL,
    larvae_collected_kg DECIMAL(10,2) NOT NULL,
    processing_method ENUM('sieving', 'self_harvesting', 'manual', 'other') NOT NULL,
    storage_temp_c DECIMAL(5,2),
    notes TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (substrate_batch_id) REFERENCES substrate_batches(batch_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Feeding Schedule
CREATE TABLE feeding_schedule (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    substrate_batch_id INT NOT NULL,
    feeding_date DATE NOT NULL,
    tray_batch_id VARCHAR(50) NOT NULL,
    larvae_age_days INT NOT NULL,
    larvae_weight_g DECIMAL(10,2) NOT NULL,
    feed_type ENUM('fruit', 'vegetable', 'brewers_grain', 'mixed', 'other') NOT NULL,
    feed_quantity_kg DECIMAL(10,2) NOT NULL,
    start_weight_g DECIMAL(10,2),
    end_weight_kg DECIMAL(10,2),
    consumption_g DECIMAL(10,2),
    operator VARCHAR(100) NOT NULL,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (substrate_batch_id) REFERENCES substrate_batches(batch_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Breeding Units
CREATE TABLE breeding_units (
    unit_id INT AUTO_INCREMENT PRIMARY KEY,
    unit_name VARCHAR(50) NOT NULL UNIQUE,
    unit_type ENUM('cage', 'net', 'room') NOT NULL,
    dimensions VARCHAR(50),
    capacity INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Breeding Records
CREATE TABLE breeding_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    unit_id INT NOT NULL,
    record_date DATE NOT NULL,
    adult_count INT NOT NULL,
    sex_ratio VARCHAR(20),
    egg_production_count INT,
    feeding_details TEXT,
    temperature_c DECIMAL(5,2),
    humidity_percent DECIMAL(5,2),
    light_hours DECIMAL(4,2),
    observations TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (unit_id) REFERENCES breeding_units(unit_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Facility Checks
CREATE TABLE facility_checks (
    check_id INT AUTO_INCREMENT PRIMARY KEY,
    check_date DATE NOT NULL,
    check_type ENUM('routine', 'maintenance', 'inspection') NOT NULL,
    area VARCHAR(100) NOT NULL,
    status ENUM('ok', 'needs_attention', 'critical') NOT NULL,
    issues_found TEXT,
    actions_taken TEXT,
    personnel VARCHAR(100) NOT NULL,
    next_check_date DATE,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Hatchery Batches
CREATE TABLE hatchery_batches (
    batch_id INT AUTO_INCREMENT PRIMARY KEY,
    batch_number VARCHAR(50) NOT NULL UNIQUE,
    batch_date DATE NOT NULL,
    egg_incubation_date DATE NOT NULL,
    total_eggs_grams DECIMAL(10,2) NOT NULL,
    expected_hatch_date DATE NOT NULL,
    actual_hatch_date DATE,
    hatch_days INT,
    supervisor_name VARCHAR(100) NOT NULL,
    notes TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Hatchery Feeding Records
CREATE TABLE hatchery_feeding (
    feeding_id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id INT NOT NULL,
    feeding_date DATE NOT NULL,
    feed_per_5g_eggs_grams DECIMAL(10,2) NOT NULL,
    total_feed_used_grams DECIMAL(10,2) NOT NULL,
    days_to_utilize INT NOT NULL,
    feed_type ENUM('brewery_waste', 'wheat_bran', 'potatoes', 'mixed', 'other') NOT NULL,
    feed_source VARCHAR(100),
    distribution_method VARCHAR(100) NOT NULL,
    notes TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES hatchery_batches(batch_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Hatchery Environmental Monitoring
CREATE TABLE hatchery_monitoring (
    monitoring_id INT AUTO_INCREMENT PRIMARY KEY,
    monitoring_date DATE NOT NULL,
    monitoring_time TIME NOT NULL,
    temperature_c DECIMAL(5,2) NOT NULL,
    humidity_percent DECIMAL(5,2) NOT NULL,
    remarks TEXT,
    action_taken TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Hatchery Cleaning & Sanitation
CREATE TABLE hatchery_cleaning (
    cleaning_id INT AUTO_INCREMENT PRIMARY KEY,
    cleaning_date DATE NOT NULL,
    areas_cleaned VARCHAR(255) NOT NULL,
    cleaning_materials VARCHAR(255) NOT NULL,
    cleaning_personnel VARCHAR(100) NOT NULL,
    remarks TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Hatchery Problems & Solutions
CREATE TABLE hatchery_problems (
    problem_id INT AUTO_INCREMENT PRIMARY KEY,
    problem_date DATE NOT NULL,
    problem_identified ENUM('larvae_escaping', 'high_temperature', 'dry_feed', 'feed_not_utilized', 'mites', 'ants', 'rodents', 'other') NOT NULL,
    proposed_solution TEXT NOT NULL,
    responsible_person VARCHAR(100) NOT NULL,
    days_to_implement INT,
    resolution_status ENUM('pending', 'in_progress', 'resolved', 'failed'),
    additional_comments TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Fly Facility Cage Monitoring
CREATE TABLE cage_monitoring (
    monitoring_id INT AUTO_INCREMENT PRIMARY KEY,
    monitoring_date DATE NOT NULL,
    cage_id VARCHAR(50) NOT NULL,
    temperature_c DECIMAL(5,2) NOT NULL,
    humidity_percent DECIMAL(5,2) NOT NULL,
    lighting_hours DECIMAL(4,2) NOT NULL,
    ventilation_ok ENUM('yes', 'no') NOT NULL,
    cage_cleaned ENUM('yes', 'no') NOT NULL,
    dead_flies_removed ENUM('yes', 'no') NOT NULL,
    cage_damage ENUM('no', 'minor', 'major') NOT NULL,
    damage_notes TEXT,
    additional_notes TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Fly Facility Maintenance
CREATE TABLE facility_maintenance (
    maintenance_id INT AUTO_INCREMENT PRIMARY KEY,
    maintenance_date DATE NOT NULL,
    moat_check ENUM('full', 'low', 'empty') NOT NULL,
    ants_present ENUM('no', 'few', 'many') NOT NULL,
    rodents_present ENUM('no', 'yes') NOT NULL,
    bird_net_ok ENUM('yes', 'damaged') NOT NULL,
    trench_refilled ENUM('yes', 'no') NOT NULL,
    maintenance_notes TEXT NOT NULL,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Pupae Transition
CREATE TABLE pupae_transition (
    transition_id INT AUTO_INCREMENT PRIMARY KEY,
    transition_date DATE NOT NULL,
    love_cage_id VARCHAR(50) NOT NULL,
    pupae_weight_added_kg DECIMAL(10,2) NOT NULL,
    old_pupae_removed_kg DECIMAL(10,2) NOT NULL,
    dead_flies_removed ENUM('none', 'few', 'many') NOT NULL,
    water_points_checked ENUM('yes', 'some', 'no') NOT NULL,
    new_egg_crates_installed ENUM('yes', 'no') NOT NULL,
    number_of_crates INT,
    transition_notes TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Egg Collection
CREATE TABLE egg_collection (
    collection_id INT AUTO_INCREMENT PRIMARY KEY,
    collection_date DATE NOT NULL,
    collection_time ENUM('early_morning', 'late_evening', 'other') NOT NULL,
    cage_id VARCHAR(50) NOT NULL,
    eggs_collected_grams DECIMAL(10,2) NOT NULL,
    bait_replaced ENUM('yes', 'no') NOT NULL,
    eggs_intact ENUM('yes', 'some', 'many') NOT NULL,
    collector_name VARCHAR(100) NOT NULL,
    collection_method ENUM('razor', 'specialized', 'manual') NOT NULL,
    collection_notes TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Bait Preparation
CREATE TABLE bait_preparation (
    preparation_id INT AUTO_INCREMENT PRIMARY KEY,
    barrel_id VARCHAR(50) NOT NULL,
    bait_type ENUM('frass_mix', 'blood', 'combined') NOT NULL,
    ingredients_added TEXT NOT NULL,
    fermentation_start_date DATE NOT NULL,
    fermentation_ready_date DATE NOT NULL,
    used_in_cage_ids VARCHAR(255),
    preparation_notes TEXT,
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Reports
CREATE TABLE saved_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    report_name VARCHAR(100) NOT NULL,
    report_type ENUM('waste', 'hatchery', 'feeding', 'growth', 'breeding', 'facility', 'custom') NOT NULL,
    date_range_start DATE,
    date_range_end DATE,
    filters JSON,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP NULL,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- Customers Table
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(50),
    email VARCHAR(100),
    address VARCHAR(255)
);

-- Sales Table
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    customer_id INT NOT NULL,
    product VARCHAR(100),
    quantity INT,
    amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- Deliveries Table
CREATE TABLE IF NOT EXISTS deliveries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    customer_id INT NOT NULL,
    product VARCHAR(100),
    quantity INT,
    status ENUM('Pending', 'Delivered', 'Cancelled') NOT NULL,
    notes TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- Customer Feedback Table
CREATE TABLE IF NOT EXISTS customer_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    customer_id INT NOT NULL,
    feedback TEXT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
); 