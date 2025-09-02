-- Create the database
CREATE DATABASE IF NOT EXISTS waste_management;
USE waste_management;

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
    contaminants JSON,
    notes TEXT,
    recorded_by INT NOT NULL DEFAULT 1,
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
    recorded_by INT NOT NULL DEFAULT 1,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (collection_id) REFERENCES waste_collections(collection_id),
    FOREIGN KEY (unit_id) REFERENCES storage_units(unit_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Processing Records
CREATE TABLE processing_records (
    processing_id INT AUTO_INCREMENT PRIMARY KEY,
    storage_id INT NULL,
    processing_date DATE NOT NULL,
    processing_time TIME NOT NULL,
    processing_type ENUM('composting', 'drying', 'fermentation', 'grinding', 'mixing', 'other') NOT NULL,
    processing_method VARCHAR(100) NOT NULL,
    waste_processed_kg DECIMAL(10,2) NOT NULL,
    by_products VARCHAR(255),
    waste_reduction_percent DECIMAL(5,2),
    person_responsible VARCHAR(100) NOT NULL,
    observations TEXT,
    recorded_by INT NOT NULL DEFAULT 1,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (storage_id) REFERENCES waste_storage(storage_id) ON DELETE SET NULL,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Environmental Monitoring
CREATE TABLE environmental_monitoring (
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
    recorded_by INT NOT NULL DEFAULT 1,
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
    recorded_by INT NOT NULL DEFAULT 1,
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
    recorded_by INT NOT NULL DEFAULT 1,
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
    recorded_by INT NOT NULL DEFAULT 1,
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
    recorded_by INT NOT NULL DEFAULT 1,
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
    recorded_by INT NOT NULL DEFAULT 1,
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
    recorded_by INT NOT NULL DEFAULT 1,
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
    recorded_by INT NOT NULL DEFAULT 1,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (unit_id) REFERENCES breeding_units(unit_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Facility Checks
CREATE TABLE facility_checks (
    check_id INT AUTO_INCREMENT PRIMARY KEY,
    check_date DATE NOT NULL,
    check_time TIME NOT NULL,
    area_checked VARCHAR(100) NOT NULL,
    check_type ENUM('routine', 'maintenance', 'inspection', 'other') NOT NULL,
    findings TEXT NOT NULL,
    action_taken TEXT,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    recorded_by INT NOT NULL DEFAULT 1,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Hatchery Batches
CREATE TABLE hatchery_batches (
    batch_id INT AUTO_INCREMENT PRIMARY KEY,
    batch_number VARCHAR(50) NOT NULL UNIQUE,
    start_date DATE NOT NULL,
    expected_hatch_date DATE NOT NULL,
    egg_count INT NOT NULL,
    temperature_c DECIMAL(5,2) NOT NULL,
    humidity_percent DECIMAL(5,2) NOT NULL,
    notes TEXT,
    recorded_by INT NOT NULL DEFAULT 1,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Hatchery Feeding
CREATE TABLE hatchery_feeding (
    feeding_id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id INT NOT NULL,
    feeding_date DATE NOT NULL,
    feeding_time TIME NOT NULL,
    feed_type VARCHAR(50) NOT NULL,
    feed_quantity_g DECIMAL(10,2) NOT NULL,
    consumption_rate_percent DECIMAL(5,2),
    operator VARCHAR(100) NOT NULL,
    notes TEXT,
    recorded_by INT NOT NULL DEFAULT 1,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES hatchery_batches(batch_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Hatchery Monitoring
CREATE TABLE hatchery_monitoring (
    monitoring_id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id INT NOT NULL,
    monitoring_date DATE NOT NULL,
    monitoring_time TIME NOT NULL,
    temperature_c DECIMAL(5,2) NOT NULL,
    humidity_percent DECIMAL(5,2) NOT NULL,
    development_stage ENUM('egg', 'larva', 'prepupa', 'pupa', 'adult') NOT NULL,
    mortality_count INT,
    observations TEXT,
    recorded_by INT NOT NULL DEFAULT 1,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES hatchery_batches(batch_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Hatchery Cleaning
CREATE TABLE hatchery_cleaning (
    cleaning_id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id INT NOT NULL,
    cleaning_date DATE NOT NULL,
    cleaning_time TIME NOT NULL,
    cleaning_type ENUM('routine', 'deep', 'emergency') NOT NULL,
    cleaning_method VARCHAR(100) NOT NULL,
    cleaning_agent VARCHAR(100),
    operator VARCHAR(100) NOT NULL,
    notes TEXT,
    recorded_by INT NOT NULL DEFAULT 1,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES hatchery_batches(batch_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Hatchery Problems
CREATE TABLE hatchery_problems (
    problem_id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id INT NOT NULL,
    problem_date DATE NOT NULL,
    problem_type VARCHAR(100) NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    description TEXT NOT NULL,
    action_taken TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    resolution_date DATE,
    recorded_by INT NOT NULL DEFAULT 1,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES hatchery_batches(batch_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Cage Monitoring
CREATE TABLE cage_monitoring (
    monitoring_id INT AUTO_INCREMENT PRIMARY KEY,
    cage_id VARCHAR(50) NOT NULL,
    monitoring_date DATE NOT NULL,
    monitoring_time TIME NOT NULL,
    adult_count INT NOT NULL,
    egg_count INT,
    temperature_c DECIMAL(5,2) NOT NULL,
    humidity_percent DECIMAL(5,2) NOT NULL,
    light_hours DECIMAL(4,2) NOT NULL,
    feeding_status ENUM('fed', 'not_fed', 'partial') NOT NULL,
    water_status ENUM('full', 'partial', 'empty') NOT NULL,
    observations TEXT,
    recorded_by INT NOT NULL DEFAULT 1,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Facility Maintenance
CREATE TABLE facility_maintenance (
    maintenance_id INT AUTO_INCREMENT PRIMARY KEY,
    maintenance_date DATE NOT NULL,
    maintenance_time TIME NOT NULL,
    area_maintained VARCHAR(100) NOT NULL,
    maintenance_type ENUM('routine', 'repair', 'replacement', 'other') NOT NULL,
    description TEXT NOT NULL,
    cost DECIMAL(10,2),
    performed_by VARCHAR(100) NOT NULL,
    notes TEXT,
    recorded_by INT NOT NULL DEFAULT 1,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Pupae Transition
CREATE TABLE pupae_transition (
    transition_id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id INT NOT NULL,
    transition_date DATE NOT NULL,
    transition_time TIME NOT NULL,
    pupae_count INT NOT NULL,
    transition_method ENUM('manual', 'automatic', 'other') NOT NULL,
    temperature_c DECIMAL(5,2) NOT NULL,
    humidity_percent DECIMAL(5,2) NOT NULL,
    operator VARCHAR(100) NOT NULL,
    notes TEXT,
    recorded_by INT NOT NULL DEFAULT 1,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES hatchery_batches(batch_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Egg Collection
CREATE TABLE egg_collection (
    collection_id INT AUTO_INCREMENT PRIMARY KEY,
    collection_date DATE NOT NULL,
    collection_time TIME NOT NULL,
    cage_id VARCHAR(50) NOT NULL,
    egg_count INT NOT NULL,
    collection_method ENUM('manual', 'automatic', 'other') NOT NULL,
    storage_conditions TEXT NOT NULL,
    operator VARCHAR(100) NOT NULL,
    notes TEXT,
    recorded_by INT NOT NULL DEFAULT 1,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Bait Preparation
CREATE TABLE bait_preparation (
    preparation_id INT AUTO_INCREMENT PRIMARY KEY,
    preparation_date DATE NOT NULL,
    preparation_time TIME NOT NULL,
    bait_type VARCHAR(50) NOT NULL,
    ingredients TEXT NOT NULL,
    quantity_kg DECIMAL(10,2) NOT NULL,
    preparation_method TEXT NOT NULL,
    storage_conditions TEXT NOT NULL,
    expiry_date DATE NOT NULL,
    prepared_by VARCHAR(100) NOT NULL,
    notes TEXT,
    recorded_by INT NOT NULL DEFAULT 1,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Saved Reports
CREATE TABLE saved_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    report_name VARCHAR(100) NOT NULL,
    report_type ENUM('waste', 'environmental', 'growth', 'harvest', 'breeding', 'maintenance', 'other') NOT NULL,
    report_date DATE NOT NULL,
    report_data JSON NOT NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
); 