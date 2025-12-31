"""Unit tests for main application entry point."""

import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main import initialize_mqtt, initialize_database


class TestMainInitialization(unittest.TestCase):
    """Test initialization logic in main.py."""

    def setUp(self):
        """Set up test environment."""
        self.mock_settings = MagicMock()

    @patch('main.MQTTClient')
    @patch('main.MQTTSimulator')
    def test_initialize_mqtt_simulator_mode(self, mock_simulator, mock_client):
        """Test MQTT initialization in simulator mode."""
        # Arrange
        self.mock_settings.is_simulator = True
        self.mock_settings.mqtt_broker = "localhost"
        self.mock_settings.mqtt_port = 1883
        self.mock_settings.mqtt_client_id = "test_client"
        self.mock_settings.mqtt_username = "user"
        self.mock_settings.mqtt_password = "password"
        self.mock_settings.mqtt_topic_monitoring = "topic/monitor"

        # Mock successful connection
        mock_simulator_instance = mock_simulator.return_value
        mock_simulator_instance.connect.return_value = True

        # Act
        client = initialize_mqtt(self.mock_settings)

        # Assert
        mock_simulator.assert_called_once_with(
            broker="localhost",
            port=1883,
            client_id="test_client",
            username="user",
            password="password"
        )
        mock_client.assert_not_called()
        mock_simulator_instance.connect.assert_called_once()
        mock_simulator_instance.subscribe.assert_called_once_with("topic/monitor")
        self.assertEqual(client, mock_simulator_instance)

    @patch('main.MQTTClient')
    @patch('main.MQTTSimulator')
    def test_initialize_mqtt_real_mode(self, mock_simulator, mock_client):
        """Test MQTT initialization in real mode."""
        # Arrange
        self.mock_settings.is_simulator = False
        self.mock_settings.mqtt_broker = "192.168.1.10"
        self.mock_settings.mqtt_port = 1883
        self.mock_settings.mqtt_client_id = "real_client"
        self.mock_settings.mqtt_username = "admin"
        self.mock_settings.mqtt_password = "secure"
        self.mock_settings.mqtt_topic_monitoring = "real/monitor"

        # Mock successful connection
        mock_client_instance = mock_client.return_value
        mock_client_instance.connect.return_value = True

        # Act
        client = initialize_mqtt(self.mock_settings)

        # Assert
        mock_client.assert_called_once_with(
            broker="192.168.1.10",
            port=1883,
            client_id="real_client",
            username="admin",
            password="secure"
        )
        mock_simulator.assert_not_called()
        mock_client_instance.connect.assert_called_once()
        mock_client_instance.subscribe.assert_called_once_with("real/monitor")
        self.assertEqual(client, mock_client_instance)

    @patch('main.sys.exit')
    @patch('main.MQTTClient')
    def test_initialize_mqtt_connection_failure(self, mock_client, mock_exit):
        """Test MQTT initialization failure handling."""
        # Arrange
        self.mock_settings.is_simulator = False
        mock_client_instance = mock_client.return_value
        mock_client_instance.connect.return_value = False  # Simulate failure

        # Act
        initialize_mqtt(self.mock_settings)

        # Assert
        mock_exit.assert_called_once_with(1)

    @patch('main.MockDatabase')
    @patch('main.DatabaseHandler')
    def test_initialize_database_simulator_mode(self, mock_handler, mock_mock_db):
        """Test Database initialization in simulator mode."""
        # Arrange
        self.mock_settings.is_simulator = True

        # Act
        db = initialize_database(self.mock_settings)

        # Assert
        mock_mock_db.assert_called_once_with(persist_file="simulator/data/feeding_history.json")
        mock_handler.assert_not_called()
        self.assertEqual(db, mock_mock_db.return_value)

    @patch('main.MockDatabase')
    @patch('main.DatabaseHandler')
    def test_initialize_database_real_mode(self, mock_handler, mock_mock_db):
        """Test Database initialization in real mode."""
        # Arrange
        self.mock_settings.is_simulator = False
        self.mock_settings.db_host = "db_host"
        self.mock_settings.db_port = 3306
        self.mock_settings.db_user = "db_user"
        self.mock_settings.db_password = "db_pass"
        self.mock_settings.db_name = "db_name"

        mock_handler_instance = mock_handler.return_value
        mock_handler_instance.test_connection.return_value = True
        mock_handler_instance.initialize_database.return_value = True

        # Act
        db = initialize_database(self.mock_settings)

        # Assert
        mock_handler.assert_called_once_with(
            host="db_host",
            port=3306,
            user="db_user",
            password="db_pass",
            database="db_name"
        )
        mock_mock_db.assert_not_called()
        mock_handler_instance.test_connection.assert_called_once()
        mock_handler_instance.initialize_database.assert_called_once()
        self.assertEqual(db, mock_handler_instance)

    @patch('main.sys.exit')
    @patch('main.DatabaseHandler')
    def test_initialize_database_connection_failure(self, mock_handler, mock_exit):
        """Test Database initialization connection failure."""
        # Arrange
        self.mock_settings.is_simulator = False
        mock_handler_instance = mock_handler.return_value
        mock_handler_instance.test_connection.return_value = False  # Fail connection

        # Act
        initialize_database(self.mock_settings)

        # Assert
        mock_exit.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()
