"""Database handler for Smart Pet Feeder.

Provides database operations for feeding history with connection management
and error handling.
"""

from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
import pymysql
from pymysql.cursors import DictCursor
from src.utils.logger import get_logger
from config.constants import Constants


class DatabaseHandler:
    """Database handler for feeding history operations."""
    
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str
    ):
        """Initialize database handler.
        
        Args:
            host: Database host address
            port: Database port
            user: Database username
            password: Database password
            database: Database name
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        
        self.logger = get_logger(__name__)
        self.logger.info(f"Database handler initialized: {host}:{port}/{database}")
    
    def _get_connection(self):
        """Create a new database connection.
        
        Returns:
            pymysql.Connection: Database connection
        """
        try:
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=DictCursor,
                connect_timeout=10
            )
            return connection
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test database connection.
        
        Returns:
            bool: True if connection successful
        """
        try:
            conn = self._get_connection()
            conn.close()
            self.logger.info("Database connection test successful")
            return True
        except Exception as e:
            self.logger.error(f"Database connection test failed: {e}")
            return False

    def initialize_database(self) -> bool:
        """Initialize database schema if it doesn't exist.
        
        Creates necessary tables if they are missing.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Create feeding_history table
                    query = f"""
                        CREATE TABLE IF NOT EXISTS {Constants.TABLE_FEEDING_HISTORY} (
                            {Constants.COLUMN_ID} INT AUTO_INCREMENT PRIMARY KEY,
                            {Constants.COLUMN_FOOD_WEIGHT} FLOAT NOT NULL,
                            amount FLOAT NOT NULL,
                            {Constants.COLUMN_STATUS_MOUNT} VARCHAR(50) NOT NULL,
                            motor VARCHAR(10) NOT NULL,
                            {Constants.COLUMN_TIMESTAMP} DATETIME DEFAULT CURRENT_TIMESTAMP,
                            INDEX idx_timestamp ({Constants.COLUMN_TIMESTAMP}),
                            INDEX idx_food_weight ({Constants.COLUMN_FOOD_WEIGHT})
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                    """
                    cursor.execute(query)
                    conn.commit()
                    self.logger.info("Database schema verification/initialization successful")
                    return True
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            return False
    
    def get_latest_food_weight(self) -> Optional[float]:
        """Get the latest food weight from feeding history.
        
        Returns:
            Optional[float]: Latest food weight in grams, or None if no data
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    query = f"""
                        SELECT {Constants.COLUMN_FOOD_WEIGHT} 
                        FROM {Constants.TABLE_FEEDING_HISTORY} 
                        ORDER BY {Constants.COLUMN_ID} DESC 
                        LIMIT 1
                    """
                    cursor.execute(query)
                    result = cursor.fetchone()
                    
                    if result:
                        weight = result[Constants.COLUMN_FOOD_WEIGHT]
                        self.logger.debug(f"Latest food weight: {weight}g")
                        return float(weight)
                    else:
                        self.logger.warning("No food weight data available")
                        return None
        
        except Exception as e:
            self.logger.error(f"Error fetching latest food weight: {e}")
            return None
    
    def get_latest_status_mount(self) -> Optional[str]:
        """Get the latest status mount (food amount) from feeding history.
        
        Returns:
            Optional[str]: Latest status mount, or None if no data
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    query = f"""
                        SELECT {Constants.COLUMN_STATUS_MOUNT} 
                        FROM {Constants.TABLE_FEEDING_HISTORY} 
                        ORDER BY {Constants.COLUMN_ID} DESC 
                        LIMIT 1
                    """
                    cursor.execute(query)
                    result = cursor.fetchone()
                    
                    if result:
                        status = result[Constants.COLUMN_STATUS_MOUNT]
                        self.logger.debug(f"Latest status mount: {status}")
                        return str(status)
                    else:
                        self.logger.warning("No status mount data available")
                        return None
        
        except Exception as e:
            self.logger.error(f"Error fetching latest status mount: {e}")
            return None
    
    def get_monthly_data(self, month: str) -> List[Tuple[float, datetime]]:
        """Get feeding history data for a specific month.
        
        Args:
            month: Month number as string (01-12)
        
        Returns:
            List[Tuple[float, datetime]]: List of (food_weight, timestamp) tuples
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    query = f"""
                        SELECT {Constants.COLUMN_FOOD_WEIGHT}, {Constants.COLUMN_TIMESTAMP}
                        FROM {Constants.TABLE_FEEDING_HISTORY}
                        WHERE MONTH({Constants.COLUMN_TIMESTAMP}) = %s
                        ORDER BY {Constants.COLUMN_TIMESTAMP} ASC
                    """
                    cursor.execute(query, (month,))
                    results = cursor.fetchall()
                    
                    data = [
                        (float(row[Constants.COLUMN_FOOD_WEIGHT]), row[Constants.COLUMN_TIMESTAMP])
                        for row in results
                    ]
                    
                    self.logger.debug(f"Retrieved {len(data)} records for month {month}")
                    return data
        
        except Exception as e:
            self.logger.error(f"Error fetching monthly data for month {month}: {e}")
            return []
    
    def insert_feeding_record(
        self,
        food_weight: float,
        amount: float,
        status_mount: str,
        motor: str
    ) -> bool:
        """Insert a new feeding record.
        
        Args:
            food_weight: Food weight in grams
            amount: Remaining food amount in grams
            status_mount: Status mount value
            motor: Motor state (open/close)
        
        Returns:
            bool: True if insert successful
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    query = f"""
                        INSERT INTO {Constants.TABLE_FEEDING_HISTORY}
                        ({Constants.COLUMN_FOOD_WEIGHT}, amount, {Constants.COLUMN_STATUS_MOUNT}, motor, {Constants.COLUMN_TIMESTAMP})
                        VALUES (%s, %s, %s, %s, NOW())
                    """
                    cursor.execute(query, (food_weight, amount, status_mount, motor))
                    conn.commit()
                    
                    self.logger.debug(f"Inserted feeding record: weight={food_weight}g, amount={amount}g")
                    return True
        
        except Exception as e:
            self.logger.error(f"Error inserting feeding record: {e}")
            return False
    
    def get_all_records(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all feeding records with optional limit.
        
        Args:
            limit: Maximum number of records to retrieve
        
        Returns:
            List[Dict[str, Any]]: List of feeding records
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    query = f"""
                        SELECT * FROM {Constants.TABLE_FEEDING_HISTORY}
                        ORDER BY {Constants.COLUMN_ID} DESC
                        LIMIT %s
                    """
                    cursor.execute(query, (limit,))
                    results = cursor.fetchall()
                    
                    self.logger.debug(f"Retrieved {len(results)} records")
                    return results
        
        except Exception as e:
            self.logger.error(f"Error fetching all records: {e}")
            return []
