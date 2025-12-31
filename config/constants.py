"""System constants for Smart Pet Feeder.

This module contains all constant values used throughout the application.
These values should not change during runtime.
"""


class Constants:
    """System-wide constants."""

    # Application Information
    APP_NAME = "Smart Pet Feeder"
    APP_VERSION = "2.0.0"

    # Hardware Constants
    DEFAULT_FOOD_CAPACITY = 3000  # grams
    MIN_WEIGHT = 0  # grams
    MAX_WEIGHT = 300  # grams

    # Weight Thresholds
    WEIGHT_EMPTY = 0
    WEIGHT_MID = 1500
    WEIGHT_FULL = 3000

    # Servo Motor Positions
    SERVO_OPEN = 90  # degrees
    SERVO_CLOSE = 0  # degrees

    # MQTT Topics (default)
    TOPIC_CONTROL = "IoT/project/control"
    TOPIC_MONITORING = "IoT/project/monitoring"

    # MQTT Commands
    CMD_FEED_ON = "on"
    CMD_FEED_OFF = "off"
    CMD_RESET = "r"

    # MQTT Message Keys
    KEY_STATUS = "status"
    KEY_FOOD_WEIGHT = "food_weight"
    KEY_AMOUNT = "amount"
    KEY_STATUS_MOUNT = "status_mount"
    KEY_MOTOR = "motor"

    # Motor States
    MOTOR_OPEN = "open"
    MOTOR_CLOSE = "close"

    # Status Values
    STATUS_EMPTY = "empty"

    # Database
    TABLE_FEEDING_HISTORY = "feeding_history"
    COLUMN_ID = "id"
    COLUMN_FOOD_WEIGHT = "food_weight"
    COLUMN_STATUS_MOUNT = "status_mount"
    COLUMN_TIMESTAMP = "timestamp"

    # UI Update Intervals (milliseconds)
    DEFAULT_UPDATE_INTERVAL = 5000
    GRAPH_UPDATE_INTERVAL = 1000

    # Months Mapping
    MONTHS = {
        "January": "01",
        "February": "02",
        "March": "03",
        "April": "04",
        "May": "05",
        "June": "06",
        "July": "07",
        "August": "08",
        "September": "09",
        "October": "10",
        "November": "11",
        "December": "12"
    }

    # Simulator Constants
    SIMULATOR_UPDATE_INTERVAL = 1.0  # seconds (Faster for real-time feel)
    SIMULATOR_WEIGHT_CHANGE_MIN = -5  # grams (eating)
    SIMULATOR_WEIGHT_CHANGE_MAX = 5  # grams
    SIMULATOR_MAX_BOWL_WEIGHT = 90.0  # grams (Auto-stop threshold)
    SIMULATOR_FEED_RATE = 10.0  # grams per interval (feeding speed)
    SIMULATOR_NETWORK_DELAY_MIN = 0.1  # seconds
    SIMULATOR_NETWORK_DELAY_MAX = 0.5  # seconds

    # Logging
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
