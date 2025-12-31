"""MQTT Client wrapper for Smart Pet Feeder.

Provides a clean interface for MQTT operations with connection management,
retry logic, and error handling.
"""

import json
import time
from typing import Callable, Dict, Any, Optional
import paho.mqtt.client as mqtt
from src.utils.logger import get_logger
from config.constants import Constants


class MQTTClient:
    """MQTT Client wrapper with connection management."""
    
    def __init__(
        self,
        broker: str,
        port: int,
        client_id: str,
        username: str = "",
        password: str = "",
        on_message_callback: Optional[Callable] = None
    ):
        """Initialize MQTT client.
        
        Args:
            broker: MQTT broker address
            port: MQTT broker port
            client_id: Unique client identifier
            username: MQTT username (optional)
            password: MQTT password (optional)
            on_message_callback: Callback function for incoming messages
        """
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.username = username
        self.password = password
        self.on_message_callback = on_message_callback
        
        self.logger = get_logger(__name__)
        self.client = mqtt.Client(client_id=client_id)
        self.connected = False
        self.subscribed_topics = set()
        
        # Setup callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Set credentials if provided
        if username and password:
            self.client.username_pw_set(username, password)
        
        self.logger.info(f"MQTT Client initialized: {broker}:{port}")

    def set_callback(self, callback: Callable):
        """Set the message callback function.
        
        Args:
            callback: Function to call when message is received
        """
        self.on_message_callback = callback
        self.logger.debug("MQTT callback updated")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker."""
        if rc == 0:
            self.connected = True
            self.logger.info(f"Connected to MQTT broker: {self.broker}:{self.port}")
            
            # Resubscribe to topics after reconnection
            for topic in self.subscribed_topics:
                self.logger.info(f"Resubscribing to topic: {topic}")
                client.subscribe(topic)
        else:
            self.connected = False
            self.logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker."""
        self.connected = False
        if rc != 0:
            self.logger.warning(f"Unexpected disconnection from MQTT broker. Return code: {rc}")
        else:
            self.logger.info("Disconnected from MQTT broker")
    
    def _on_message(self, client, userdata, msg):
        """Callback when message is received."""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            self.logger.debug(f"Message received on topic '{topic}': {payload}")
            
            # Parse JSON payload
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                self.logger.warning(f"Failed to parse JSON payload: {payload}")
                data = {"raw": payload}
            
            # Call user callback if provided
            if self.on_message_callback:
                self.on_message_callback(topic, data)
        
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    def connect(self, retry_count: int = 3, retry_delay: int = 5) -> bool:
        """Connect to MQTT broker with retry logic.
        
        Args:
            retry_count: Number of connection attempts
            retry_delay: Delay between retries in seconds
        
        Returns:
            bool: True if connected successfully, False otherwise
        """
        for attempt in range(retry_count):
            try:
                self.logger.info(f"Connecting to MQTT broker (attempt {attempt + 1}/{retry_count})...")
                self.client.connect(self.broker, self.port, keepalive=60)
                self.client.loop_start()
                
                # Wait for connection
                timeout = 10
                start_time = time.time()
                while not self.connected and (time.time() - start_time) < timeout:
                    time.sleep(0.1)
                
                if self.connected:
                    return True
                else:
                    self.logger.warning(f"Connection timeout on attempt {attempt + 1}")
            
            except Exception as e:
                self.logger.error(f"Connection error on attempt {attempt + 1}: {e}")
            
            if attempt < retry_count - 1:
                self.logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
        
        self.logger.error("Failed to connect to MQTT broker after all attempts")
        return False
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            self.logger.info("Disconnected from MQTT broker")
        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")
    
    def subscribe(self, topic: str) -> bool:
        """Subscribe to a topic.
        
        Args:
            topic: MQTT topic to subscribe to
        
        Returns:
            bool: True if subscribed successfully
        """
        try:
            result, mid = self.client.subscribe(topic)
            if result == mqtt.MQTT_ERR_SUCCESS:
                self.subscribed_topics.add(topic)
                self.logger.info(f"Subscribed to topic: {topic}")
                return True
            else:
                self.logger.error(f"Failed to subscribe to topic: {topic}")
                return False
        except Exception as e:
            self.logger.error(f"Error subscribing to topic {topic}: {e}")
            return False
    
    def publish(self, topic: str, data: Dict[str, Any]) -> bool:
        """Publish data to a topic.
        
        Args:
            topic: MQTT topic to publish to
            data: Dictionary data to publish (will be JSON serialized)
        
        Returns:
            bool: True if published successfully
        """
        try:
            payload = json.dumps(data)
            result = self.client.publish(topic, payload)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"Published to topic '{topic}': {payload}")
                return True
            else:
                self.logger.error(f"Failed to publish to topic '{topic}'")
                return False
        
        except Exception as e:
            self.logger.error(f"Error publishing to topic {topic}: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if client is connected to broker.
        
        Returns:
            bool: True if connected
        """
        return self.connected
