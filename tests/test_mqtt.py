import pytest
import json
from unittest.mock import MagicMock, patch
from src.mqtt.client import MQTTClient

@pytest.fixture
def mqtt_client():
    """Fixture to create an MQTTClient with a mocked paho client."""
    with patch("paho.mqtt.client.Client"):
        client = MQTTClient(
            broker="localhost",
            port=1883,
            client_id="test_client"
        )
        # Manually mock the internal paho client since it was initialized in __init__
        client.client = MagicMock()
        return client

def test_mqtt_publish_serialization(mqtt_client):
    """Test that data is correctly JSON serialized before publishing."""
    test_data = {"status": "on", "value": 123}
    
    # Mock the return value of publish (rc=0 means success)
    mqtt_client.client.publish.return_value.rc = 0
    
    result = mqtt_client.publish("test/topic", test_data)
    
    assert result is True
    mqtt_client.client.publish.assert_called_once()
    cid, payload = mqtt_client.client.publish.call_args[0]
    assert cid == "test/topic"
    assert json.loads(payload) == test_data

def test_mqtt_callback_execution(mqtt_client):
    """Test that the user callback is triggered on message arrival."""
    mock_callback = MagicMock()
    mqtt_client.set_callback(mock_callback)
    
    # Create a mock paho message
    mock_msg = MagicMock()
    mock_msg.topic = "test/topic"
    mock_msg.payload = b'{"key": "value"}'
    
    # Trigger the internal _on_message callback
    mqtt_client._on_message(None, None, mock_msg)
    
    # Verify the user callback was called with parsed data
    mock_callback.assert_called_once_with("test/topic", {"key": "value"})
