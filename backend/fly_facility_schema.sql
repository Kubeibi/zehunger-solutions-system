-- Cage Monitoring Table
CREATE TABLE IF NOT EXISTS cage_monitoring (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    cage_id VARCHAR(50) NOT NULL,
    temperature DECIMAL(4,1) NOT NULL,
    humidity INT NOT NULL,
    lighting_hours DECIMAL(3,1) NOT NULL,
    ventilation_ok ENUM('yes', 'no') NOT NULL,
    cage_cleaned ENUM('yes', 'no') NOT NULL,
    dead_flies_removed ENUM('yes', 'no') NOT NULL,
    cage_damage ENUM('no', 'minor', 'major') NOT NULL,
    damage_notes TEXT,
    additional_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Facility Maintenance Table
CREATE TABLE IF NOT EXISTS facility_maintenance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    moat_check ENUM('full', 'low', 'empty') NOT NULL,
    ants_present ENUM('no', 'few', 'many') NOT NULL,
    rodents_present ENUM('no', 'yes') NOT NULL,
    bird_net_ok ENUM('yes', 'damaged') NOT NULL,
    trench_refilled ENUM('yes', 'no') NOT NULL,
    maintenance_notes TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pupae Transition Table
CREATE TABLE IF NOT EXISTS pupae_transition (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    love_cage_id VARCHAR(50) NOT NULL,
    pupae_weight_added DECIMAL(5,1) NOT NULL,
    old_pupae_removed DECIMAL(5,1) NOT NULL,
    dead_flies_removed ENUM('none', 'few', 'many') NOT NULL,
    water_points_checked ENUM('yes', 'some', 'no') NOT NULL,
    new_egg_crates_installed ENUM('yes', 'no') NOT NULL,
    number_of_crates INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Egg Collection Table
CREATE TABLE IF NOT EXISTS egg_collection (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    time ENUM('early_morning', 'late_evening', 'other') NOT NULL,
    cage_id VARCHAR(50) NOT NULL,
    eggs_collected DECIMAL(5,1) NOT NULL,
    bait_replaced ENUM('yes', 'no') NOT NULL,
    eggs_intact ENUM('yes', 'some', 'many') NOT NULL,
    collector_name VARCHAR(100) NOT NULL,
    collection_method ENUM('razor', 'specialized', 'manual') NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bait Preparation Table
CREATE TABLE IF NOT EXISTS bait_preparation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    barrel_id VARCHAR(50) NOT NULL,
    bait_type ENUM('frass_mix', 'blood', 'combined') NOT NULL,
    ingredients_added TEXT NOT NULL,
    start_date DATE NOT NULL,
    ready_date DATE NOT NULL,
    used_in_cage_ids VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 