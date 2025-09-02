from database import DatabaseConnection
import sys

def check_database():
    db = DatabaseConnection()
    
    print("\n=== Checking Database Structure ===\n")
    
    # Check old tables
    print("Checking old tables...")
    old_tables = ['waste_storage', 'waste_collections', 'waste_sources', 'storage_units']
    for table in old_tables:
        try:
            result = db.execute_query(f"SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = 'bsf_farm' AND table_name = '{table}'")
            if result and result[0]['count'] > 0:
                print(f"WARNING: Old table '{table}' still exists!")
            else:
                print(f"✓ Old table '{table}' has been removed")
        except Exception as e:
            print(f"Error checking {table}: {str(e)}")
    
    print("\nChecking new tables...")
    new_tables = ['waste_sourcing', 'storage_records', 'processing_records', 'environmental_monitoring']
    for table in new_tables:
        try:
            result = db.execute_query(f"SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = 'bsf_farm' AND table_name = '{table}'")
            if result and result[0]['count'] > 0:
                print(f"✓ New table '{table}' exists")
            else:
                print(f"ERROR: New table '{table}' is missing!")
        except Exception as e:
            print(f"Error checking {table}: {str(e)}")
    
    # Check table structures
    print("\nChecking table structures...")
    for table in new_tables:
        print(f"\nStructure of {table} table:")
        try:
            result = db.execute_query(f"SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, EXTRA FROM information_schema.columns WHERE table_schema = 'bsf_farm' AND table_name = '{table}' ORDER BY ORDINAL_POSITION")
            if result:
                for row in result:
                    field = row['COLUMN_NAME']
                    type = row['COLUMN_TYPE']
                    null = row['IS_NULLABLE']
                    key = row['COLUMN_KEY']
                    default = row['COLUMN_DEFAULT']
                    extra = row['EXTRA']
                    print(f"  {field}: {type} {'NOT NULL' if null == 'NO' else 'NULL'} {key} {default or ''} {extra}")
            else:
                print(f"ERROR: Could not get structure for {table}")
        except Exception as e:
            print(f"Error getting structure for {table}: {str(e)}")

if __name__ == "__main__":
    try:
        check_database()
    except Exception as e:
        print(f"Error checking database: {str(e)}")
        sys.exit(1) 