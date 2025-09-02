import mysql.connector
from mysql.connector import Error
import logging
from config import DB_CONFIG

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create a database connection."""
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        if connection.is_connected():
            logger.debug("Successfully connected to MySQL database")
            return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL database: {e}")
        raise

def execute_query(query, params=None, is_insert=False):
    """Execute a database query with proper error handling."""
    connection = get_db_connection()
    if not connection:
        logger.error("Failed to establish database connection.")
        return None

    cursor = connection.cursor()
    try:
        # Log the query and parameters
        logger.debug(f"Executing query: {query}")
        if params:
            logger.debug(f"With parameters: {params}")
        
        cursor.execute(query, params)
        
        if is_insert:
            connection.commit()
            last_id = cursor.lastrowid
            logger.debug(f"Insert successful. Last inserted ID: {last_id}")
            return last_id
        else:
            result = cursor.fetchall()
            logger.debug(f"Query result: {result}")
            return result
            
    except Error as e:
        if connection:
            connection.rollback()
        logger.error(f"Database error: {e}")
        return None
    finally:
        cursor.close()
        if connection and connection.is_connected():
            connection.close()
            logger.debug("Database connection closed")

def test_connection():
    """Test the database connection."""
    try:
        connection = get_db_connection()
        if connection.is_connected():
            db_info = connection.get_server_info()
            logger.info(f"Connected to MySQL Server version {db_info}")
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            logger.info(f"Connected to database: {record[0]}")
            return True
    except Error as e:
        logger.error(f"Error testing database connection: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            logger.debug("Database connection closed")

# Example usage (you can remove this or keep for testing)
if __name__ == '__main__':
    # Test connection
    connection = get_db_connection()
    if connection:
        connection.close()
        print("Test connection successful and closed.")
    
    # Example: Create a table (You should run this directly in MySQL or use a migration tool)
    # create_table_sql = """
    # CREATE TABLE IF NOT EXISTS test_table (
    #     id INT AUTO_INCREMENT PRIMARY KEY,
    #     name VARCHAR(255) NOT NULL,
    #     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    # );
    # """
    # print("Attempting to create test_table...")
    # execute_query(create_table_sql)
    # print("Finished attempting to create test_table.")
    
    # Example: Insert data
    # insert_sql = "INSERT INTO test_table (name) VALUES (%s)"
    # last_id = execute_query(insert_sql, params=("Test Name",), is_insert=True)
    # if last_id:
    #     print(f"Inserted data with ID: {last_id}")
        
    # Example: Select data
    # select_sql = "SELECT * FROM test_table"
    # records = execute_query(select_sql, fetch_all=True)
    # if records:
    #     print("Records found:", records) 