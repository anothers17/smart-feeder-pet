"""Virtual ESP32 Device Simulator for Smart Pet Feeder.

Simulates the behavior of the ESP32 device including:
- Food weight sensor simulation
- Servo motor control
- MQTT communication
- Realistic feeding behavior
"""

import time
import random
import threading
from typing import Optional

# DEBUG: Print immediately
print("\n" + "="*50)
print(">>> BEEP BOOP! VIRTUAL DEVICE INIT...")
print(">>> IF YOU SEE THIS, PYTHON IS RUNNING!")
print("="*50 + "\n")

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.mqtt.simulator import MQTTSimulator
from src.utils.logger import get_logger
from config.settings import get_settings
from config.constants import Constants


class VirtualDevice:
    """Virtual ESP32 device simulator."""
    
    def __init__(self):
        """Initialize virtual device."""
        self.logger = get_logger(__name__)
        self.settings = get_settings()
        
        # Device state
        self.food_mount = float(Constants.DEFAULT_FOOD_CAPACITY)
        self.weight = 0.0
        self.servo_angle = Constants.SERVO_CLOSE
        self.feeding_mode = "NONE"
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # MQTT client
        self.mqtt = MQTTSimulator(
            broker=self.settings.mqtt_broker,
            port=self.settings.mqtt_port,
            client_id="virtual_esp32_device",
            on_message_callback=self._on_mqtt_message
        )
        
        self.logger.info("Virtual ESP32 device initialized")
    
    def _on_mqtt_message(self, topic: str, data: dict):
        """Handle incoming MQTT messages.
        
        Args:
            topic: MQTT topic
            data: Message data
        """
        if topic == self.settings.mqtt_topic_control:
            self._handle_control_message(data)
    
    def _handle_control_message(self, data: dict):
        """Handle control messages from the application.
        
        Args:
            data: Control message data
        """
        if Constants.KEY_STATUS not in data:
            return
        
        status = data[Constants.KEY_STATUS]
        
        if status == Constants.CMD_FEED_ON:
            self.logger.info("Control: FEED ON - Manual Feed Mode")
            self.servo_angle = Constants.SERVO_OPEN
            self.feeding_mode = "MANUAL"
        
        elif status == Constants.CMD_FEED_OFF:
            self.logger.info("Control: FEED OFF - Stopping")
            self.servo_angle = Constants.SERVO_CLOSE
            self.feeding_mode = "NONE"
        
        elif status == Constants.CMD_RESET:
            # Re-mapped to 'Fill Bowl to 90g' as per user request
            self.logger.info("Control: FILL FOOD - Auto Feed to 90g")
            self.servo_angle = Constants.SERVO_OPEN
            self.feeding_mode = "AUTO_90G"
            
            # Note: If we want to support refilling the storage tank, we might need another mechanism
            # or auto-refill when empty. For now, we assume this button is for "Smart Fill".
            if self.food_mount <= 0:
                 self.logger.warning("Storage is empty! Refilling for demo purposes...")
                 self.food_mount = 3000

    def _simulate_feeding_behavior(self):
        """Simulate realistic feeding behavior."""
        # 1. Feeding Logic - ส่วนคำนวณตอนมอเตอร์เปิดเทอาหาร
        if self.servo_angle == Constants.SERVO_OPEN:
            if self.food_mount > 0:
                # Calculate feed amount - เทอาหารออกมาตามความเร็วที่ตั้งไว้
                feed_amount = min(Constants.SIMULATOR_FEED_RATE, self.food_mount)
                
                # Transfer food from storage to bowl
                self.weight += feed_amount
                self.food_mount -= feed_amount
                
                print(f"[Device] Feeding ({self.feeding_mode})... Bowl: {self.weight:.1f}g, Storage: {self.food_mount:.1f}g")
                
                # Check Limits based on Mode
                should_stop = False
                
                # Mode: AUTO_90G -> Stop at 90g (ส่วนนี้คุมให้มอเตอร์หยุดถ้าถึง 90g)
                if self.feeding_mode == "AUTO_90G" and self.weight >= 90.0:
                    print(f"[Device] Auto-Fill Complete (>= 90g). Stopping.")
                    should_stop = True
                
                # Mode: MANUAL -> Stop only at physical max (e.g. 300g or overflow)
                # User asked for "continuous until stop", but let's put a safety at 500g to update UI correctly
                elif self.weight >= 500.0:
                     print(f"[Device] Bowl Overflow Safety (500g). Stopping.")
                     should_stop = True

                if should_stop:
                    self.servo_angle = Constants.SERVO_CLOSE
                    self.feeding_mode = "NONE"
                    # Notify App
                    self._handle_control_message({Constants.KEY_STATUS: Constants.CMD_FEED_OFF})
                    self._publish_sensor_data()
            else:
                print("[Device] Storage EMPTY. Stopping Feed.")
                self.servo_angle = Constants.SERVO_CLOSE
                self.feeding_mode = "NONE"
                self._handle_control_message({Constants.KEY_STATUS: Constants.CMD_FEED_OFF})

        # 2. Eating Logic - จำลองตอนสัตว์เลี้ยงมากินอาหาร (น้ำหนักจะค่อยๆ ลดลงเอง)
        elif self.servo_angle == Constants.SERVO_CLOSE:
            if self.weight > 0:
                # Eating rate - สุ่มความเร็วในการกิน
                eat_rate = random.uniform(0.1, 0.5)
                self.weight = max(0, self.weight - eat_rate)
        
        # Ensure values are within bounds
        self.food_mount = max(0, self.food_mount)
        self.weight = max(0, self.weight)
    
    def _publish_sensor_data(self):
        """Publish sensor data to MQTT."""
        # Print explicitly as a Sensor Reading for user visibility
        print(f"[Sensor] Reading: {self.weight:.1f} g | Status: {int(self.food_mount)} g remaining")

        # Determine status mount
        if self.food_mount <= 0:
            status_mount = Constants.STATUS_EMPTY
        else:
            status_mount = str(int(self.food_mount))
        
        # Determine motor state
        motor_state = Constants.MOTOR_OPEN if self.servo_angle == Constants.SERVO_OPEN else Constants.MOTOR_CLOSE
        
        # Prepare data
        data = {
            Constants.KEY_FOOD_WEIGHT: int(self.weight),
            Constants.KEY_AMOUNT: int(self.food_mount),
            Constants.KEY_STATUS_MOUNT: status_mount,
            Constants.KEY_MOTOR: motor_state
        }
        
        # Publish to monitoring topic
        self.mqtt.publish(self.settings.mqtt_topic_monitoring, data)
        
        self.logger.debug(
            f"Published: weight={self.weight:.1f}g, "
            f"amount={self.food_mount:.1f}g, "
            f"motor={motor_state}"
        )
    
    def _device_loop(self):
        """Main device loop (runs in separate thread)."""
        self.logger.info("Virtual device loop started")
        
        while self.running:
            try:
                # Simulate feeding behavior
                self._simulate_feeding_behavior()
                
                # Publish sensor data
                self._publish_sensor_data()
                
                # Wait for next update
                time.sleep(Constants.SIMULATOR_UPDATE_INTERVAL)
            
            except Exception as e:
                self.logger.error(f"Error in device loop: {e}")
                time.sleep(1)
        
        self.logger.info("Virtual device loop stopped")
    
    def start(self):
        """Start the virtual device."""
        if self.running:
            self.logger.warning("Virtual device is already running")
            return
        
        self.logger.info("Starting virtual ESP32 device...")
        
        # Connect to MQTT
        if not self.mqtt.connect():
            self.logger.error("Failed to connect to MQTT simulator")
            return
        
        # Subscribe to control topic
        self.mqtt.subscribe(self.settings.mqtt_topic_control)
        
        # Start device loop
        self.running = True
        self.thread = threading.Thread(target=self._device_loop, daemon=True)
        self.thread.start()
        
        self.logger.info("Virtual ESP32 device started successfully")
        print("\n" + "="*60)
        print("🤖 Virtual ESP32 Device Running")
        print("="*60)
        print(f"📡 MQTT Broker: {self.settings.mqtt_broker}:{self.settings.mqtt_port}")
        print(f"📊 Publishing to: {self.settings.mqtt_topic_monitoring}")
        print(f"🎮 Listening on: {self.settings.mqtt_topic_control}")
        print(f"🍖 Initial food capacity: {self.food_mount}g")
        print(f"⏱️  Update interval: {Constants.SIMULATOR_UPDATE_INTERVAL}s")
        print("="*60)
        print("Press Ctrl+C to stop\n")
    
    def stop(self):
        """Stop the virtual device."""
        self.logger.info("Stopping virtual ESP32 device...")
        
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2)
        
        self.mqtt.disconnect()
        
        self.logger.info("Virtual ESP32 device stopped")
    
    def run_forever(self):
        """Run the virtual device until interrupted."""
        self.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nShutting down virtual device...")
            self.stop()


def main():
    """Main entry point for running the virtual device standalone."""
    import sys
    from pathlib import Path
    
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Setup logging
    from src.utils.logger import setup_logging
    settings = get_settings()
    setup_logging(log_level=settings.log_level)
    
    # Create and run virtual device
    device = VirtualDevice()
    device.run_forever()


if __name__ == '__main__':
    main()
