-- Create waste_sources table
CREATE TABLE IF NOT EXISTS waste_sources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    collection_date DATE NOT NULL,
    collection_time TIME NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    source_name VARCHAR(100) NOT NULL,
    waste_type VARCHAR(50) NOT NULL,
    waste_weight DECIMAL(10,2) NOT NULL,
    segregation_status VARCHAR(50) NOT NULL,
    collection_personnel VARCHAR(100) NOT NULL,
    contaminants_found JSON,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create waste_storage table
CREATE TABLE IF NOT EXISTS waste_storage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    storage_date DATE NOT NULL,
    storage_method VARCHAR(50) NOT NULL,
    storage_conditions VARCHAR(50) NOT NULL,
    storage_duration INT NOT NULL,
    planned_utilization VARCHAR(50) NOT NULL,
    person_responsible VARCHAR(100) NOT NULL,
    observations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create waste_processing table
CREATE TABLE IF NOT EXISTS waste_processing (
    id INT AUTO_INCREMENT PRIMARY KEY,
    processing_date DATE NOT NULL,
    processing_type VARCHAR(50) NOT NULL,
    processing_method VARCHAR(100) NOT NULL,
    waste_processed DECIMAL(10,2) NOT NULL,
    by_products VARCHAR(255),
    waste_reduction DECIMAL(5,2),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create environmental_monitoring table
CREATE TABLE IF NOT EXISTS environmental_monitoring (
    id INT AUTO_INCREMENT PRIMARY KEY,
    monitoring_date DATE NOT NULL,
    monitoring_time TIME NOT NULL,
    tray_facility_id VARCHAR(50) NOT NULL,
    temperature DECIMAL(5,2) NOT NULL,
    humidity DECIMAL(5,2) NOT NULL,
    ammonia_odor ENUM('yes', 'no') NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create substrate_preparation table
CREATE TABLE IF NOT EXISTS substrate_preparation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    batch_no VARCHAR(50) NOT NULL,
    prep_date DATE NOT NULL,
    organic_waste_source VARCHAR(100) NOT NULL,
    moisture_percentage DECIMAL(5,2) NOT NULL,
    waste_particle_size ENUM('fine', 'medium', 'coarse') NOT NULL,
    foreign_matter ENUM('yes', 'no') NOT NULL,
    handler_operator VARCHAR(100) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create health_intervention table
CREATE TABLE IF NOT EXISTS health_intervention (
    id INT AUTO_INCREMENT PRIMARY KEY,
    health_date DATE NOT NULL,
    tray_batch_id VARCHAR(50) NOT NULL,
    observed_issue VARCHAR(255) NOT NULL,
    severity ENUM('low', 'medium', 'high') NOT NULL,
    follow_up_date DATE,
    resolved ENUM('yes', 'no'),
    action_taken TEXT NOT NULL,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create harvest_yield table
CREATE TABLE IF NOT EXISTS harvest_yield (
    id INT AUTO_INCREMENT PRIMARY KEY,
    harvest_date DATE NOT NULL,
    tray_batch_id VARCHAR(50) NOT NULL,
    instar_stage INT NOT NULL,
    larvae_collected DECIMAL(10,2) NOT NULL,
    processing_method ENUM('sieving', 'self_harvesting', 'manual', 'other') NOT NULL,
    storage_temp DECIMAL(5,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create feeding_schedule table
CREATE TABLE IF NOT EXISTS feeding_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    feeding_date DATE NOT NULL,
    tray_batch_id VARCHAR(50) NOT NULL,
    larvae_age_days INT NOT NULL,
    larvae_weight DECIMAL(10,2) NOT NULL,
    feed_type VARCHAR(50) NOT NULL,
    feed_quantity DECIMAL(10,2) NOT NULL,
    start_weight DECIMAL(10,2),
    end_weight DECIMAL(10,2),
    consumption DECIMAL(10,2),
    operator VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Larvae Feeding Section Database Schema

-- Batch Information Table
CREATE TABLE IF NOT EXISTS hatchery_batches (
    batch_id SERIAL PRIMARY KEY,
    batch_number VARCHAR(50) NOT NULL UNIQUE,
    batch_date DATE NOT NULL,
    egg_incubation_date DATE NOT NULL,
    total_eggs_grams DECIMAL(10,2) NOT NULL CHECK (total_eggs_grams > 0),
    expected_hatch_date DATE NOT NULL,
    actual_hatch_date DATE,
    hatch_days INTEGER CHECK (hatch_days > 0),
    supervisor_name VARCHAR(100) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_dates CHECK (
        batch_date <= egg_incubation_date AND
        egg_incubation_date <= expected_hatch_date AND
        (actual_hatch_date IS NULL OR actual_hatch_date >= egg_incubation_date)
    )
);

-- Feeding Records Table
CREATE TABLE IF NOT EXISTS hatchery_feeding (
    feeding_id SERIAL PRIMARY KEY,
    batch_id INTEGER NOT NULL REFERENCES hatchery_batches(batch_id),
    feeding_date DATE NOT NULL,
    feed_per_5g_eggs_grams DECIMAL(10,2) NOT NULL CHECK (feed_per_5g_eggs_grams > 0),
    total_feed_used_grams DECIMAL(10,2) NOT NULL CHECK (total_feed_used_grams > 0),
    days_to_utilize INTEGER NOT NULL CHECK (days_to_utilize > 0),
    feed_type VARCHAR(50) NOT NULL CHECK (
        feed_type IN ('brewery_waste', 'wheat_bran', 'potatoes', 'mixed', 'other')
    ),
    feed_source VARCHAR(100),
    distribution_method VARCHAR(100) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_feeding_date CHECK (
        feeding_date >= (SELECT batch_date FROM hatchery_batches WHERE batch_id = hatchery_feeding.batch_id)
    )
);

-- Environmental Monitoring Table
CREATE TABLE IF NOT EXISTS hatchery_monitoring (
    monitoring_id SERIAL PRIMARY KEY,
    monitoring_date DATE NOT NULL,
    temperature_c DECIMAL(5,2) NOT NULL CHECK (temperature_c BETWEEN -50 AND 100),
    humidity_percent DECIMAL(5,2) NOT NULL CHECK (humidity_percent BETWEEN 0 AND 100),
    adjustments_made TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cleaning & Sanitation Table
CREATE TABLE IF NOT EXISTS hatchery_cleaning (
    cleaning_id SERIAL PRIMARY KEY,
    cleaning_date DATE NOT NULL,
    areas_cleaned TEXT NOT NULL,
    cleaning_materials TEXT NOT NULL,
    cleaning_personnel VARCHAR(100) NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Problems & Solutions Table
CREATE TABLE IF NOT EXISTS hatchery_problems (
    problem_id SERIAL PRIMARY KEY,
    problem_date DATE NOT NULL,
    problem_identified VARCHAR(50) NOT NULL CHECK (
        problem_identified IN (
            'larvae_escaping', 'high_temperature', 'dry_feed', 
            'feed_not_utilized', 'mites', 'ants', 'rodents', 'other'
        )
    ),
    proposed_solution TEXT NOT NULL,
    responsible_person VARCHAR(100) NOT NULL,
    days_to_implement INTEGER CHECK (days_to_implement >= 0),
    resolution_status VARCHAR(20) CHECK (
        resolution_status IN ('pending', 'in_progress', 'resolved', 'failed')
    ),
    additional_comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_hatchery_batches_batch_number ON hatchery_batches(batch_number);
CREATE INDEX idx_hatchery_batches_dates ON hatchery_batches(batch_date, egg_incubation_date, expected_hatch_date);
CREATE INDEX idx_hatchery_feeding_batch_id ON hatchery_feeding(batch_id);
CREATE INDEX idx_hatchery_feeding_dates ON hatchery_feeding(feeding_date);
CREATE INDEX idx_hatchery_monitoring_dates ON hatchery_monitoring(monitoring_date);
CREATE INDEX idx_hatchery_cleaning_dates ON hatchery_cleaning(cleaning_date);
CREATE INDEX idx_hatchery_problems_dates ON hatchery_problems(problem_date);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_hatchery_batches_updated_at
    BEFORE UPDATE ON hatchery_batches
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hatchery_feeding_updated_at
    BEFORE UPDATE ON hatchery_feeding
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hatchery_monitoring_updated_at
    BEFORE UPDATE ON hatchery_monitoring
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hatchery_cleaning_updated_at
    BEFORE UPDATE ON hatchery_cleaning
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hatchery_problems_updated_at
    BEFORE UPDATE ON hatchery_problems
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 