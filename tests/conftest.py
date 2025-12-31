import pytest
import os
from unittest.mock import MagicMock
from config.settings import Settings

@pytest.fixture
def mock_settings():
    """Fixture for settings with test values."""
    settings = Settings()
    settings.mode = "SIMULATOR"
    settings.mqtt_broker = "localhost"
    settings.db_host = "localhost"
    return settings

@pytest.fixture
def mock_mqtt():
    """Fixture for a mocked MQTT client."""
    client = MagicMock()
    client.connect.return_value = True
    return client

@pytest.fixture
def mock_db():
    """Fixture for a mocked Database handler."""
    db = MagicMock()
    db.test_connection.return_value = True
    return db
