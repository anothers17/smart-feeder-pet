"""MQTT Simulator for Smart Pet Feeder.

Provides a mock MQTT client for simulator mode that doesn't require
a real MQTT broker. Uses in-memory message queue.
"""

# pylint: disable=unused-argument,no-else-return,broad-exception-caught,too-many-nested-blocks,import-outside-toplevel

import json
import time
import threading
from pathlib import Path
from typing import Callable, Dict, Any, Optional
from src.utils.logger import get_logger


class MQTTSimulator:
    """Mock MQTT client for simulator mode using file-based IPC."""

    def __init__(
        self,
        broker: str,
        port: int,
        client_id: str,
        username: str = "",
        password: str = "",
        on_message_callback: Optional[Callable] = None
    ):
        """Initialize MQTT simulator."""
        self.client_id = client_id
        self.on_message_callback = on_message_callback

        self.logger = get_logger(__name__)
        self.connected = False
        self.subscribed_topics = set()
        self.running = False
        self.message_thread = None
        self.last_read_pos = 0

        # Resolve absolute path for robustness
        # Use a temporary directory or project root? Project root is safer for visibility.
        # Ideally get project root dynamically.
        base_dir = Path.cwd()
        self.bus_file_path = base_dir / "simulator" / "data" / "mqtt_bus.jsonl"

        self.bus_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Clear file on startup if it's the virtual device (optional, but cleaner)
        if "device" in client_id.lower():
            with open(self.bus_file_path, 'w', encoding='utf-8') as f:
                f.write('')

        print(f"[{self.client_id}] MQTT Bus File: {self.bus_file_path}")
        self.logger.info(f"MQTT Simulator initialized (IPC File: {self.bus_file_path})")

    def set_callback(self, callback: Callable):
        """Set the message callback function."""
        self.on_message_callback = callback

    def connect(self, retry_count: int = 3, retry_delay: int = 5) -> bool:
        """Simulate connection."""
        self.logger.info("Connecting to MQTT Simulator bus...")
        time.sleep(0.5)

        self.connected = True
        self.running = True

        # Start reading from end of file (don't process old messages)
        try:
            if self.bus_file_path.exists():
                self.last_read_pos = self.bus_file_path.stat().st_size
        except Exception:
            self.last_read_pos = 0

        self.message_thread = threading.Thread(target=self._process_messages, daemon=True)
        self.message_thread.start()

        self.logger.info("MQTT Simulator connected")
        return True

    def disconnect(self):
        """Disconnect from bus."""
        self.running = False
        self.connected = False
        if self.message_thread:
            self.message_thread.join(timeout=1)
        self.logger.info("MQTT Simulator disconnected")

    def subscribe(self, topic: str) -> bool:
        """Subscribe to a topic."""
        self.subscribed_topics.add(topic)
        self.logger.info(f"Subscribed to topic: {topic}")
        return True

    def publish(self, topic: str, data: Dict[str, Any]) -> bool:
        """Publish data to the bus file."""
        try:
            msg = {
                'topic': topic,
                'payload': data,
                'timestamp': time.time(),
                'publisher': self.client_id
            }

            line = json.dumps(msg) + '\n'

            with open(self.bus_file_path, 'a', encoding='utf-8') as f:
                f.write(line)
                f.flush()
                # os.fsync(f.fileno()) # Force write to disk if needed

            # Print to console for user visibility
            print(f"[{self.client_id}] >>> Sent to {topic}: {data}")
            self.logger.debug(f"Published to {topic}")
            return True
        except Exception as e:
            print(f"[{self.client_id}] ERROR Publishing: {e}")
            self.logger.error(f"Error publishing: {e}")
            return False

    def _process_messages(self):
        """Poll file for new messages."""
        while self.running:
            try:
                if not self.bus_file_path.exists():
                    time.sleep(0.1)
                    continue

                # Check size
                try:
                    current_stats = self.bus_file_path.stat()
                    current_size = current_stats.st_size
                except FileNotFoundError:
                    continue

                if current_size < self.last_read_pos:
                    self.last_read_pos = 0

                if current_size > self.last_read_pos:
                    with open(self.bus_file_path, 'r', encoding='utf-8') as f:
                        f.seek(self.last_read_pos)
                        new_lines = f.readlines()
                        self.last_read_pos = f.tell()

                    for line in new_lines:
                        if not line.strip():
                            continue
                        try:
                            msg = json.loads(line)

                            # Filter out own messages if needed (prevent loops)
                            if msg.get('publisher') == self.client_id:
                                continue

                            if msg['topic'] in self.subscribed_topics:
                                print(
                                    f"[{self.client_id}] <<< "
                                    f"Received {msg['topic']}: {msg['payload']}"
                                )
                                if self.on_message_callback:
                                    self.on_message_callback(msg['topic'], msg['payload'])

                        except json.JSONDecodeError:
                            pass

                time.sleep(0.05)  # Faster polling

            except Exception:
                # self.logger.error(f"Error in message loop: {e}")
                time.sleep(1)

    def is_connected(self) -> bool:
        return self.connected
