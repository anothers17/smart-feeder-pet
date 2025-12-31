"""Main entry point for Smart Pet Feeder Application.

This module initializes the application based on configuration mode
(SIMULATOR or REAL) and starts the GUI.
"""

# pylint: disable=no-name-in-module

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# pylint: disable=wrong-import-position
from config.settings import get_settings
from src.utils.logger import setup_logging, get_logger
from src.mqtt.client import MQTTClient
from src.mqtt.simulator import MQTTSimulator
from src.database.handler import DatabaseHandler
from src.database.mock_db import MockDatabase
from src.ui.main_window import create_application


def initialize_mqtt(settings):
    """Initialize MQTT client based on mode.

    Args:
        settings: Application settings

    Returns:
        MQTT client instance (real or simulator)
    """
    logger = get_logger(__name__)

    if settings.is_simulator:
        logger.info("Initializing MQTT Simulator...")
        mqtt_client = MQTTSimulator(
            broker=settings.mqtt_broker,
            port=settings.mqtt_port,
            client_id=settings.mqtt_client_id,
            username=settings.mqtt_username,
            password=settings.mqtt_password
        )
    else:
        logger.info("Initializing MQTT Client...")
        mqtt_client = MQTTClient(
            broker=settings.mqtt_broker,
            port=settings.mqtt_port,
            client_id=settings.mqtt_client_id,
            username=settings.mqtt_username,
            password=settings.mqtt_password
        )

    # Connect to MQTT
    if not mqtt_client.connect():
        logger.error("Failed to connect to MQTT broker")
        sys.exit(1)

    # Subscribe to monitoring topic
    mqtt_client.subscribe(settings.mqtt_topic_monitoring)

    return mqtt_client


def initialize_database(settings):
    """Initialize database handler based on mode.

    Args:
        settings: Application settings

    Returns:
        Database handler instance (real or mock)
    """
    logger = get_logger(__name__)

    if settings.is_simulator:
        logger.info("Initializing Mock Database...")
        db = MockDatabase(persist_file="simulator/data/feeding_history.json")
    else:
        logger.info("Initializing Database Handler...")
        db = DatabaseHandler(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name
        )

        # Test connection
        if not db.test_connection():
            logger.error("Failed to connect to database")
            sys.exit(1)

        # Initialize schema (Auto-migration)
        if not db.initialize_database():
            logger.error("Failed to initialize database schema")
            sys.exit(1)

    return db


def main():
    """Main application entry point."""
    try:
        # Load settings
        settings = get_settings()

        # Setup logging
        setup_logging(log_level=settings.log_level, log_file=settings.log_file)
        logger = get_logger(__name__)

        logger.info("="*60)
        logger.info("Starting Smart Pet Feeder Application")
        logger.info(f"Mode: {settings.mode}")
        logger.info("="*60)

        # Initialize MQTT
        mqtt_client = initialize_mqtt(settings)

        # Initialize Database
        database = initialize_database(settings)

        # Create application
        logger.info("Creating GUI application...")
        # pylint: disable=unused-variable
        app, main_window, ui = create_application(mqtt_client, database, settings)

        # Show window
        main_window.show()

        logger.info("Application started successfully")

        if settings.is_simulator:
            logger.info("")
            logger.info("="*60)
            logger.info("SIMULATOR MODE ACTIVE")
            logger.info("="*60)
            logger.info("To simulate device data, run in another terminal:")
            logger.info("  python simulator/virtual_device.py")
            logger.info("="*60)
            logger.info("")

        # Run application
        exit_code = app.exec_()

        # Cleanup
        logger.info("Shutting down...")
        mqtt_client.disconnect()
        logger.info("Application closed")

        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
