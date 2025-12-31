"""Application settings configuration.

Handles loading settings from environment variables and provides a
centralized Settings object for the application.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

from config.constants import Constants


@dataclass
class Settings:
    """Application settings data class."""

    # Mode
    mode: str
    is_simulator: bool

    # MQTT
    mqtt_broker: str
    mqtt_port: int
    mqtt_client_id: str
    mqtt_username: str
    mqtt_password: str
    mqtt_topic_control: str
    mqtt_topic_monitoring: str

    # Database
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    # UI
    ui_update_interval: int
    weight_threshold_empty: int
    weight_threshold_mid: int
    weight_threshold_full: int

    # Icons (Optional paths)
    icon_food_empty: Optional[str] = None
    icon_food_full: Optional[str] = None
    icon_feeder_empty: Optional[str] = None
    icon_feeder_mid: Optional[str] = None
    icon_feeder_full: Optional[str] = None

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None

    def __init__(self):
        """Initialize settings from environment variables."""
        # Load .env file
        load_dotenv()

        # Mode
        self.mode = os.getenv("MODE", "SIMULATOR").upper()
        self.is_simulator = self.mode == "SIMULATOR"

        # MQTT
        self.mqtt_broker = os.getenv("MQTT_BROKER", "localhost")
        self.mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
        self.mqtt_client_id = os.getenv(
            "MQTT_CLIENT_ID", f"pet_feeder_{self.mode.lower()}"
        )
        self.mqtt_username = os.getenv("MQTT_USERNAME", "")
        self.mqtt_password = os.getenv("MQTT_PASSWORD", "")
        self.mqtt_topic_control = os.getenv(
            "MQTT_TOPIC_CONTROL", Constants.TOPIC_CONTROL
        )
        self.mqtt_topic_monitoring = os.getenv(
            "MQTT_TOPIC_MONITORING", Constants.TOPIC_MONITORING
        )

        # Database
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = int(os.getenv("DB_PORT", "3306"))
        self.db_user = os.getenv("DB_USER", "root")
        self.db_password = os.getenv("DB_PASSWORD", "")
        self.db_name = os.getenv("DB_NAME", "smart_pet_feeder")

        # UI
        self.ui_update_interval = int(
            os.getenv("UI_UPDATE_INTERVAL", str(Constants.DEFAULT_UPDATE_INTERVAL))
        )
        self.weight_threshold_empty = int(
            os.getenv("WEIGHT_THRESHOLD_EMPTY", str(Constants.WEIGHT_EMPTY))
        )
        self.weight_threshold_mid = int(
            os.getenv("WEIGHT_THRESHOLD_MID", str(Constants.WEIGHT_MID))
        )
        self.weight_threshold_full = int(
            os.getenv("WEIGHT_THRESHOLD_FULL", str(Constants.WEIGHT_FULL))
        )

        # Icons
        self.icon_food_empty = os.getenv("ICON_FOOD_EMPTY")
        self.icon_food_full = os.getenv("ICON_FOOD_FULL")
        self.icon_feeder_empty = os.getenv("ICON_FEEDER_EMPTY")
        self.icon_feeder_mid = os.getenv("ICON_FEEDER_MID")
        self.icon_feeder_full = os.getenv("ICON_FEEDER_FULL")

        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE")


# Global settings instance (lazy loaded)
# pylint: disable=invalid-name
_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create global settings instance.

    Returns:
        Settings: Global settings instance
    """
    # pylint: disable=global-statement
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
