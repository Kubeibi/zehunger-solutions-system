-- Check if old tables exist
SELECT 'Checking old tables...' as '';
SHOW TABLES LIKE 'waste_storage';
SHOW TABLES LIKE 'waste_collections';
SHOW TABLES LIKE 'waste_sources';
SHOW TABLES LIKE 'storage_units';

-- Check if new tables exist
SELECT 'Checking new tables...' as '';
SHOW TABLES LIKE 'waste_sourcing';
SHOW TABLES LIKE 'storage_records';
SHOW TABLES LIKE 'processing_records';
SHOW TABLES LIKE 'environmental_monitoring';

-- Show structure of new tables
SELECT 'Structure of waste_sourcing table:' as '';
DESCRIBE waste_sourcing;

SELECT 'Structure of storage_records table:' as '';
DESCRIBE storage_records;

SELECT 'Structure of processing_records table:' as '';
DESCRIBE processing_records;

SELECT 'Structure of environmental_monitoring table:' as '';
DESCRIBE environmental_monitoring; 