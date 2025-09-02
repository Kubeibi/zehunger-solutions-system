USE bsf_farm;

DROP TABLE IF EXISTS environmental_monitoring;

CREATE TABLE environmental_monitoring (
    id INT AUTO_INCREMENT PRIMARY KEY,
    monitoring_date DATE NOT NULL,
    monitoring_time TIME NOT NULL,
    temperature DECIMAL(5,2) NOT NULL,
    humidity DECIMAL(5,2) NOT NULL,
    odor_level ENUM('none', 'slight', 'moderate', 'strong', 'very_strong') NOT NULL,
    pest_presence ENUM('none', 'slight', 'moderate', 'severe') NOT NULL,
    pest_details TEXT,
    mitigation_actions TEXT,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_monitoring_date (monitoring_date)
);

DROP TABLE IF EXISTS processing_records;

CREATE TABLE processing_records (
    processing_id INT AUTO_INCREMENT PRIMARY KEY,
    collection_id INT NOT NULL,
    processing_date DATE NOT NULL,
    processing_time TIME NOT NULL,
    processing_type ENUM('composting', 'drying', 'fermentation', 'grinding', 'mixing', 'other') NOT NULL,
    processing_method VARCHAR(100) NOT NULL,
    waste_processed_kg DECIMAL(10,2) NOT NULL,
    by_products VARCHAR(255),
    waste_reduction_percent DECIMAL(5,2),
    
    observations TEXT,
    recorded_by INT NOT NULL DEFAULT 1,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (collection_id) REFERENCES waste_collections(collection_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);

-- Drop the storageId and personResponsible columns from waste_storage table
ALTER TABLE waste_storage
DROP COLUMN storage_id,
DROP COLUMN person_responsible;

-- Update the processing_records table to reference collection_id instead of storage_id
ALTER TABLE processing_records
DROP FOREIGN KEY processing_records_ibfk_1,
DROP COLUMN storage_id,
ADD COLUMN collection_id INT NOT NULL AFTER processing_id,
ADD FOREIGN KEY (collection_id) REFERENCES waste_collections(collection_id); 