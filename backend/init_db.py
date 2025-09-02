import mysql.connector
from mysql.connector import Error
import logging
from config import DB_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database and create all necessary tables."""
    try:
        # First, connect without database to create it if it doesn't exist
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            cursor.execute(f"USE {DB_CONFIG['database']}")
            logger.info(f"Database {DB_CONFIG['database']} created or already exists")
            
            # Create waste_sources table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS waste_sources (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    source_name VARCHAR(100) NOT NULL,
                    waste_type VARCHAR(50) NOT NULL,
                    quantity DECIMAL(10,2) NOT NULL,
                    collection_date DATE NOT NULL,
                    collection_method VARCHAR(50) NOT NULL,
                    location VARCHAR(100) NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create waste_storage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS waste_storage (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    storage_date DATE NOT NULL,
                    storage_method VARCHAR(50) NOT NULL,
                    storage_conditions VARCHAR(100) NOT NULL,
                    storage_duration INT NOT NULL,
                    planned_utilization VARCHAR(100) NOT NULL,
                    person_responsible VARCHAR(100) NOT NULL,
                    observations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create waste_processing table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS waste_processing (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    processing_date DATE NOT NULL,
                    processing_type VARCHAR(50) NOT NULL,
                    processing_method VARCHAR(50) NOT NULL,
                    waste_processed DECIMAL(10,2) NOT NULL,
                    by_products TEXT,
                    waste_reduction DECIMAL(5,2),
                    remarks TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create all necessary tables
            create_tables(cursor)
            
            connection.commit()
            logger.info("Database initialization completed successfully")
            
    except Error as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("Database connection closed")

def create_tables(cursor):
    """Create all necessary tables in the database."""
    # Create waste_sources table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS waste_sources (
            id INT AUTO_INCREMENT PRIMARY KEY,
            collection_date DATE NOT NULL,
            collection_time TIME NOT NULL,
            source_type ENUM('restaurant', 'market', 'brewery', 'food_industry', 'household', 'farm', 'other') NOT NULL,
            source_name VARCHAR(100) NOT NULL,
            waste_type ENUM('fruit', 'vegetable', 'brewers_grain', 'potato', 'food_leftovers', 'mixed_organic', 'other') NOT NULL,
            waste_weight DECIMAL(10,2) NOT NULL,
            segregation_status ENUM('organic', 'inorganic', 'mixed') NOT NULL,
            collection_personnel VARCHAR(100) NOT NULL,
            contaminants_found JSON,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_collection_date (collection_date)
        )
    """)
    
    # Create waste_storage table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS waste_storage (
            id INT AUTO_INCREMENT PRIMARY KEY,
            storage_date DATE NOT NULL,
            storage_method ENUM('plastic_bin', 'metal_bin', 'compost_pit', 'tank', 'other') NOT NULL,
            storage_conditions ENUM('good', 'fair', 'poor', 'contaminated') NOT NULL,
            storage_duration INT NOT NULL,
            planned_utilization ENUM('feed', 'fertilizer', 'energy', 'other') NOT NULL,
            person_responsible VARCHAR(100) NOT NULL,
            observations TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_storage_date (storage_date)
        )
    """)
    
    # Create waste_processing table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS waste_processing (
            id INT AUTO_INCREMENT PRIMARY KEY,
            processing_date DATE NOT NULL,
            processing_type ENUM('composting', 'drying', 'fermentation', 'grinding', 'mixing', 'other') NOT NULL,
            processing_method VARCHAR(100) NOT NULL,
            waste_processed DECIMAL(10,2) NOT NULL,
            by_products VARCHAR(255),
            waste_reduction DECIMAL(5,2),
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_processing_date (processing_date)
        )
    """)
    
    # Create environmental_monitoring table
    cursor.execute("""
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
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_monitoring_date (monitoring_date)
        )
    """)
    
    # Create environmental_monitoring_larvaefeeding table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS environmental_monitoring_larvaefeeding (
            id INT AUTO_INCREMENT PRIMARY KEY,
            monitoring_date DATE NOT NULL,
            monitoring_time TIME NOT NULL,
            tray_facility_id VARCHAR(50) NOT NULL,
            temperature DECIMAL(5,2) NOT NULL,
            humidity DECIMAL(5,2) NOT NULL,
            ammonia_odor ENUM('yes', 'no') NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_monitoring_date (monitoring_date)
        )
    """)
    
    # Create substrate_preparation table
    cursor.execute("""
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
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_prep_date (prep_date)
        )
    """)
    
    # Create health_intervention table
    cursor.execute("""
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
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_health_date (health_date)
        )
    """)
    
    # Create harvest_yield table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS harvest_yield (
            id INT AUTO_INCREMENT PRIMARY KEY,
            harvest_date DATE NOT NULL,
            tray_batch_id VARCHAR(50) NOT NULL,
            instar_stage ENUM('1', '2', '3', '4', '5') NOT NULL,
            larvae_collected DECIMAL(10,2) NOT NULL,
            processing_method ENUM('sieving', 'self_harvesting', 'manual', 'other') NOT NULL,
            storage_temp DECIMAL(5,2),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_harvest_date (harvest_date)
        )
    """)
    
    # Create feeding_schedule table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feeding_schedule (
            id INT AUTO_INCREMENT PRIMARY KEY,
            feeding_date DATE NOT NULL,
            tray_batch_id VARCHAR(50) NOT NULL,
            larvae_age_days INT NOT NULL,
            larvae_weight DECIMAL(10,2) NOT NULL,
            feed_type ENUM('fruit', 'vegetable', 'brewers_grain', 'mixed', 'other') NOT NULL,
            feed_quantity DECIMAL(10,2) NOT NULL,
            start_weight DECIMAL(10,2),
            end_weight DECIMAL(10,2),
            consumption DECIMAL(10,2),
            operator VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_feeding_date (feeding_date)
        )
    """)
    
    # Create cage_monitoring table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cage_monitoring (
            id INT AUTO_INCREMENT PRIMARY KEY,
            monitoring_date DATE NOT NULL,
            cage_id VARCHAR(50) NOT NULL,
            temperature DECIMAL(5,2) NOT NULL,
            humidity DECIMAL(5,2) NOT NULL,
            lighting_hours DECIMAL(4,1) NOT NULL,
            ventilation_ok ENUM('yes', 'no') NOT NULL,
            cage_cleaned ENUM('yes', 'no') NOT NULL,
            dead_flies_removed ENUM('yes', 'no') NOT NULL,
            cage_damage ENUM('no', 'minor', 'major') NOT NULL,
            damage_notes TEXT,
            additional_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_monitoring_date (monitoring_date),
            INDEX idx_cage_id (cage_id)
        )
    """)
    
    # Create facility_maintenance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facility_maintenance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            maintenance_date DATE NOT NULL,
            moat_check ENUM('full', 'low', 'empty') NOT NULL,
            ants_present ENUM('no', 'few', 'many') NOT NULL,
            rodents_present ENUM('no', 'yes') NOT NULL,
            bird_net_ok ENUM('yes', 'damaged') NOT NULL,
            trench_refilled ENUM('yes', 'no') NOT NULL,
            maintenance_notes TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_maintenance_date (maintenance_date)
        )
    """)
    
    # Create pupae_transition table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pupae_transition (
            id INT AUTO_INCREMENT PRIMARY KEY,
            transition_date DATE NOT NULL,
            love_cage_id VARCHAR(50) NOT NULL,
            pupae_weight_added DECIMAL(10,2) NOT NULL,
            old_pupae_removed DECIMAL(10,2) NOT NULL,
            dead_flies_removed ENUM('none', 'few', 'many') NOT NULL,
            water_points_checked ENUM('yes', 'some', 'no') NOT NULL,
            new_egg_crates_installed ENUM('yes', 'no') NOT NULL,
            number_of_crates INT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_transition_date (transition_date),
            INDEX idx_love_cage_id (love_cage_id)
        )
    """)
    
    # Create egg_collection table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS egg_collection (
            id INT AUTO_INCREMENT PRIMARY KEY,
            collection_date DATE NOT NULL,
            collection_time ENUM('early_morning', 'late_evening', 'other') NOT NULL,
            cage_id VARCHAR(50) NOT NULL,
            eggs_collected DECIMAL(10,2) NOT NULL,
            bait_replaced ENUM('yes', 'no') NOT NULL,
            eggs_intact ENUM('yes', 'some', 'many') NOT NULL,
            collector_name VARCHAR(100) NOT NULL,
            collection_method ENUM('razor', 'specialized', 'manual') NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_collection_date (collection_date),
            INDEX idx_cage_id (cage_id)
        )
    """)
    
    # Create bait_preparation table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bait_preparation (
            id INT AUTO_INCREMENT PRIMARY KEY,
            barrel_id VARCHAR(50) NOT NULL,
            bait_type ENUM('frass_mix', 'blood', 'combined') NOT NULL,
            ingredients_added TEXT NOT NULL,
            start_date DATE NOT NULL,
            ready_date DATE NOT NULL,
            used_in_cage_ids TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_barrel_id (barrel_id),
            INDEX idx_start_date (start_date),
            INDEX idx_ready_date (ready_date)
        )
    """)

if __name__ == "__main__":
    init_database() 