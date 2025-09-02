-- Waste Sourcing Table
CREATE TABLE waste_sourcing (
    sourcing_id INT AUTO_INCREMENT PRIMARY KEY,
    collection_date DATE NOT NULL,
    collection_time TIME NOT NULL,
    source_type ENUM('restaurant', 'market', 'brewery', 'food_industry', 'household', 'farm', 'other') NOT NULL,
    source_name VARCHAR(100) NOT NULL,
    waste_type ENUM('fruit', 'vegetable', 'brewers_grain', 'potato', 'food_leftovers', 'mixed_organic', 'other') NOT NULL,
    waste_weight DECIMAL(10,2) NOT NULL,
    segregation_status ENUM('organic', 'inorganic', 'mixed') NOT NULL,
    collection_personnel VARCHAR(100) NOT NULL,
    contaminants JSON,
    collection_notes TEXT,
    recorded_by VARCHAR(100) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Storage Records Table
CREATE TABLE storage_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    storage_date DATE NOT NULL,
    storage_method ENUM('plastic_bin', 'metal_bin', 'compost_pit', 'tank', 'other') NOT NULL,
    storage_conditions ENUM('good', 'fair', 'poor', 'contaminated') NOT NULL,
    storage_duration INT NOT NULL,
    planned_utilization ENUM('feed', 'fertilizer', 'energy', 'other') NOT NULL,
    storage_observations TEXT
);

-- Processing Records Table
CREATE TABLE processing_records (
    processing_id INT AUTO_INCREMENT PRIMARY KEY,
    processing_date DATE NOT NULL,
    processing_type ENUM('composting', 'drying', 'fermentation', 'grinding', 'mixing', 'other') NOT NULL,
    processing_method VARCHAR(100) NOT NULL,
    waste_processed DECIMAL(10,2) NOT NULL,
    waste_reduction DECIMAL(5,2) NOT NULL,
    by_products VARCHAR(255),
    processing_remarks TEXT
);

-- Environmental Monitoring Table
CREATE TABLE environmental_monitoring (
    monitoring_id INT AUTO_INCREMENT PRIMARY KEY,
    monitoring_date DATE NOT NULL,
    monitoring_time TIME NOT NULL,
    temperature DECIMAL(5,2) NOT NULL,
    humidity DECIMAL(5,2) NOT NULL,
    odor_level ENUM('none', 'slight', 'moderate', 'strong', 'very_strong') NOT NULL,
    pest_presence ENUM('none', 'slight', 'moderate', 'severe') NOT NULL,
    pest_details TEXT,
    mitigation_actions TEXT,
    remarks TEXT
); 