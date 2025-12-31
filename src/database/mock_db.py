"""Mock database for Smart Pet Feeder simulator mode.

Provides an in-memory database that mimics the real database interface
for testing and demonstration without requiring a real MySQL database.
"""

import json
import random
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
from src.utils.logger import get_logger
from config.constants import Constants


class MockDatabase:
    """Mock database for simulator mode."""
    
    def __init__(self, persist_file: Optional[str] = None):
        """Initialize mock database.
        
        Args:
            persist_file: Optional file path to persist data (JSON format)
        """
        self.logger = get_logger(__name__)
        self.persist_file = persist_file
        self.data: List[Dict[str, Any]] = []
        self.next_id = 1
        
        # Load persisted data if file exists
        if persist_file and Path(persist_file).exists():
            self._load_from_file()
        else:
            # Generate some initial mock data
            self._generate_mock_data()
        
        self.logger.info("Mock database initialized")
    
    def _generate_mock_data(self, days: int = 365):
        """Generate mock feeding history data.
        
        Args:
            days: Number of days of historical data to generate
        """
        self.logger.info(f"Generating {days} days of mock data...")
        
        now = datetime.now()
        
        for day in range(days):
            # Generate 3-5 records per day
            records_per_day = random.randint(3, 5)
            
            for record in range(records_per_day):
                timestamp = now - timedelta(
                    days=days - day,
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                food_weight = random.randint(10, 100)
                amount = random.randint(500, 3000)
                status_mount = str(amount) if amount > 0 else Constants.STATUS_EMPTY
                motor = random.choice([Constants.MOTOR_OPEN, Constants.MOTOR_CLOSE])
                
                self.data.append({
                    Constants.COLUMN_ID: self.next_id,
                    Constants.COLUMN_FOOD_WEIGHT: food_weight,
                    'amount': amount,
                    Constants.COLUMN_STATUS_MOUNT: status_mount,
                    'motor': motor,
                    Constants.COLUMN_TIMESTAMP: timestamp
                })
                
                self.next_id += 1
        
        # Sort by timestamp
        self.data.sort(key=lambda x: x[Constants.COLUMN_TIMESTAMP])
        
        self.logger.info(f"Generated {len(self.data)} mock records")
        
        # Determine current persistence state and save if configured
        if self.persist_file:
            self._save_to_file()
    
    def _load_from_file(self):
        """Load data from persistence file."""
        try:
            with open(self.persist_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Convert timestamp strings back to datetime
                for record in data:
                    record[Constants.COLUMN_TIMESTAMP] = datetime.fromisoformat(
                        record[Constants.COLUMN_TIMESTAMP]
                    )
                
                self.data = data
                self.next_id = max([r[Constants.COLUMN_ID] for r in self.data], default=0) + 1
                
                self.logger.info(f"Loaded {len(self.data)} records from {self.persist_file}")
        
        except Exception as e:
            self.logger.error(f"Error loading from file: {e}")
            self._generate_mock_data()
    
    def _save_to_file(self):
        """Save data to persistence file."""
        if not self.persist_file:
            return
        
        try:
            # Create directory if it doesn't exist
            Path(self.persist_file).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert datetime to ISO format for JSON serialization
            data_to_save = []
            for record in self.data:
                record_copy = record.copy()
                record_copy[Constants.COLUMN_TIMESTAMP] = record[Constants.COLUMN_TIMESTAMP].isoformat()
                data_to_save.append(record_copy)
            
            with open(self.persist_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Saved {len(self.data)} records to {self.persist_file}")
        
        except Exception as e:
            self.logger.error(f"Error saving to file: {e}")
    
    def test_connection(self) -> bool:
        """Test database connection (always succeeds for mock).
        
        Returns:
            bool: Always True
        """
        self.logger.info("Mock database connection test successful")
        return True
    
    def get_latest_food_weight(self) -> Optional[float]:
        """Get the latest food weight.
        
        Returns:
            Optional[float]: Latest food weight in grams
        """
        if not self.data:
            return None
        
        latest = max(self.data, key=lambda x: x[Constants.COLUMN_TIMESTAMP])
        weight = float(latest[Constants.COLUMN_FOOD_WEIGHT])
        self.logger.debug(f"Latest food weight (mock): {weight}g")
        return weight
    
    def get_latest_status_mount(self) -> Optional[str]:
        """Get the latest status mount.
        
        Returns:
            Optional[str]: Latest status mount
        """
        if not self.data:
            return None
        
        latest = max(self.data, key=lambda x: x[Constants.COLUMN_TIMESTAMP])
        status = str(latest[Constants.COLUMN_STATUS_MOUNT])
        self.logger.debug(f"Latest status mount (mock): {status}")
        return status
    
    def get_monthly_data(self, month: str) -> List[Tuple[float, datetime]]:
        """Get feeding history data for a specific month.
        
        Args:
            month: Month number as string (01-12)
        
        Returns:
            List[Tuple[float, datetime]]: List of (food_weight, timestamp) tuples
        """
        month_int = int(month)
        
        filtered_data = [
            (
                float(record[Constants.COLUMN_FOOD_WEIGHT]),
                record[Constants.COLUMN_TIMESTAMP]
            )
            for record in self.data
            if record[Constants.COLUMN_TIMESTAMP].month == month_int
        ]
        
        # Sort by timestamp
        filtered_data.sort(key=lambda x: x[1])
        
        self.logger.debug(f"Retrieved {len(filtered_data)} records for month {month} (mock)")
        return filtered_data
    
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
            motor: Motor state
        
        Returns:
            bool: Always True
        """
        record = {
            Constants.COLUMN_ID: self.next_id,
            Constants.COLUMN_FOOD_WEIGHT: food_weight,
            'amount': amount,
            Constants.COLUMN_STATUS_MOUNT: status_mount,
            'motor': motor,
            Constants.COLUMN_TIMESTAMP: datetime.now()
        }
        
        self.data.append(record)
        self.next_id += 1
        
        self.logger.debug(f"Inserted feeding record (mock): weight={food_weight}g, amount={amount}g")
        
        # Persist if configured
        self._save_to_file()
        
        return True
    
    def get_all_records(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all feeding records with optional limit.
        
        Args:
            limit: Maximum number of records to retrieve
        
        Returns:
            List[Dict[str, Any]]: List of feeding records
        """
        # Sort by ID descending and limit
        sorted_data = sorted(self.data, key=lambda x: x[Constants.COLUMN_ID], reverse=True)
        limited_data = sorted_data[:limit]
        
        self.logger.debug(f"Retrieved {len(limited_data)} records (mock)")
        return limited_data
