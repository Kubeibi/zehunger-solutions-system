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
    notes TEXT
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
    FOREIGN KEY (batch_id) REFERENCES hatchery_batches(batch_id)
);

-- Hatchery Environmental Monitoring (Simplified)
CREATE TABLE hatchery_monitoring (
    monitoring_id INT AUTO_INCREMENT PRIMARY KEY,
    monitoring_date DATE NOT NULL,
    temperature_c DECIMAL(5,2) NOT NULL,
    humidity_percent DECIMAL(5,2) NOT NULL,
    adjustments_made TEXT
);

-- Hatchery Cleaning & Sanitation
CREATE TABLE hatchery_cleaning (
    cleaning_id INT AUTO_INCREMENT PRIMARY KEY,
    cleaning_date DATE NOT NULL,
    areas_cleaned VARCHAR(255) NOT NULL,
    cleaning_materials VARCHAR(255) NOT NULL,
    cleaning_personnel VARCHAR(100) NOT NULL,
    remarks TEXT
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
    additional_comments TEXT
); 