"""Configuration settings loader for Smart Pet Feeder.

This module loads configuration from environment variables and .env file.
It provides a centralized Settings class for accessing all configuration values.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from .constants import Constants


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize settings by loading from .env file.
        
        Args:
            env_file: Path to .env file. If None, looks for .env in project root.
        """
        # Determine project root (parent of config directory)
        self.project_root = Path(__file__).parent.parent
        
        # Load environment variables
        if env_file is None:
            env_file = self.project_root / '.env'
        
        if Path(env_file).exists():
            load_dotenv(env_file)
        else:
            print(f"Warning: .env file not found at {env_file}")
            print("Using default values and environment variables")
        
        # Load all settings
        self._load_app_settings()
        self._load_mqtt_settings()
        self._load_database_settings()
        self._load_hardware_settings()
        self._load_ui_settings()
        self._load_logging_settings()
    
    def _load_app_settings(self):
        """Load application-level settings."""
        self.mode = os.getenv('MODE', 'SIMULATOR').upper()
        
        if self.mode not in ['SIMULATOR', 'REAL']:
            raise ValueError(f"Invalid MODE: {self.mode}. Must be 'SIMULATOR' or 'REAL'")
        
        self.is_simulator = self.mode == 'SIMULATOR'
        self.is_real = self.mode == 'REAL'
    
    def _load_mqtt_settings(self):
        """Load MQTT configuration."""
        self.mqtt_broker = os.getenv('MQTT_BROKER', '119.59.99.155')
        self.mqtt_port = int(os.getenv('MQTT_PORT', '8883'))
        self.mqtt_username = os.getenv('MQTT_USERNAME', '')
        self.mqtt_password = os.getenv('MQTT_PASSWORD', '')
        self.mqtt_client_id = os.getenv('MQTT_CLIENT_ID', 'smart_pet_feeder_app')
        
        # MQTT Topics
        self.mqtt_topic_control = os.getenv('MQTT_TOPIC_CONTROL', Constants.TOPIC_CONTROL)
        self.mqtt_topic_monitoring = os.getenv('MQTT_TOPIC_MONITORING', Constants.TOPIC_MONITORING)
    
    def _load_database_settings(self):
        """Load database configuration."""
        self.db_host = os.getenv('DB_HOST', '119.59.99.155')
        self.db_port = int(os.getenv('DB_PORT', '3306'))
        self.db_user = os.getenv('DB_USER', 'std_elect3')
        self.db_password = os.getenv('DB_PASSWORD', 'std_elect3')
        self.db_name = os.getenv('DB_NAME', 'std_final8')
        
        # Validate database settings in REAL mode
        if self.is_real:
            if not all([self.db_host, self.db_user, self.db_password, self.db_name]):
                raise ValueError("Database configuration incomplete for REAL mode")
    
    def _load_hardware_settings(self):
        """Load hardware-related settings."""
        self.food_capacity = int(os.getenv('FOOD_CAPACITY', str(Constants.DEFAULT_FOOD_CAPACITY)))
        self.weight_threshold_empty = int(os.getenv('WEIGHT_THRESHOLD_EMPTY', str(Constants.WEIGHT_EMPTY)))
        self.weight_threshold_mid = int(os.getenv('WEIGHT_THRESHOLD_MID', str(Constants.WEIGHT_MID)))
        self.weight_threshold_full = int(os.getenv('WEIGHT_THRESHOLD_FULL', str(Constants.WEIGHT_FULL)))
    
    def _load_ui_settings(self):
        """Load UI-related settings."""
        self.ui_update_interval = int(os.getenv('UI_UPDATE_INTERVAL', str(Constants.DEFAULT_UPDATE_INTERVAL)))
        
        # Icon paths (optional)
        self.icon_food_empty = os.getenv('ICON_PATH_FOOD_EMPTY', '')
        self.icon_food_full = os.getenv('ICON_PATH_FOOD_FULL', '')
        self.icon_feeder_empty = os.getenv('ICON_PATH_FEEDER_EMPTY', '')
        self.icon_feeder_mid = os.getenv('ICON_PATH_FEEDER_MID', '')
        self.icon_feeder_full = os.getenv('ICON_PATH_FEEDER_FULL', '')
    
    def _load_logging_settings(self):
        """Load logging configuration."""
        self.log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.log_file = os.getenv('LOG_FILE', 'smart_pet_feeder.log')
    
    def __repr__(self):
        """String representation of settings (without sensitive data)."""
        return (
            f"Settings(mode={self.mode}, "
            f"mqtt_broker={self.mqtt_broker}:{self.mqtt_port}, "
            f"db_host={self.db_host if self.is_real else 'N/A'})"
        )


# Global settings instance (lazy loaded)
_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create global settings instance.
    
    Returns:
        Settings: Global settings instance
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
