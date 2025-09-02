import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling
from config import DB_CONFIG
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._initialize_pool()
        return cls._instance

    @classmethod
    def _initialize_pool(cls):
        try:
            pool_config = {
                'pool_name': 'bsf_farm_pool',
                'pool_size': 5,
                **DB_CONFIG
            }
            cls._pool = mysql.connector.pooling.MySQLConnectionPool(**pool_config)
        except Error as e:
            print(f"Error creating connection pool: {e}")
            raise

    def get_connection(self):
        try:
            return self._pool.get_connection()
        except Error as e:
            print(f"Error getting connection from pool: {e}")
            raise

    def execute_query(self, query, params=None):
        conn = self.get_connection()
        cursor = None
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            last_id = cursor.lastrowid
            return last_id
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise e
        finally:
            if cursor:
                cursor.close()
            conn.close()

    def fetch_all(self, query, params=None):
        conn = self.get_connection()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            return results
        except Error as e:
            print(f"Error fetching data: {e}")
            raise e
        finally:
            if cursor:
                cursor.close()
            conn.close()

    def fetch_one(self, query, params=None):
        conn = self.get_connection()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Error fetching data: {e}")
            raise e
        finally:
            if cursor:
                cursor.close()
            conn.close()

# Example usage:
if __name__ == "__main__":
    try:
        db = DatabaseConnection()
        # Example SELECT query
        results = db.fetch_all("SELECT * FROM waste_sourcing LIMIT 5")
        print("Query results:", results)
        # Example INSERT query
        insert_query = """
        INSERT INTO waste_sourcing 
        (collection_date, source_type, waste_type, weight) 
        VALUES (%s, %s, %s, %s)
        """
        params = ('2024-03-20', 'Restaurant', 'Food Waste', 50.5)
        affected_rows = db.execute_query(insert_query, params)
        print(f"Inserted {affected_rows} rows")
    except Error as e:
        print(f"Database error: {e}") 