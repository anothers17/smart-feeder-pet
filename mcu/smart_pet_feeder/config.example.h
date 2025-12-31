#ifndef CONFIG_H
#define CONFIG_H

// WiFi Configuration
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// MQTT Configuration
#define MQTT_BROKER "YOUR_MQTT_BROKER_IP" // e.g. 192.168.1.100 or localhost
#define MQTT_PORT 1883
#define MQTT_USER "YOUR_MQTT_USERNAME"
#define MQTT_PASSWORD "YOUR_MQTT_PASSWORD"
#define MQTT_CLIENT_ID "ESP32_PetFeeder"

// MQTT Topics
#define TOPIC_MONITORING "IoT/project/monitoring"
#define TOPIC_CONTROL "IoT/project/control"

// Hardware Configuration
#define PIN_SERVO 18
#define PIN_LOAD_CELL_DT 19
#define PIN_LOAD_CELL_SCK 21

// Constants
#define MAX_FOOD_CAPACITY 3000.0f
#define FEED_STOP_THRESHOLD 90.0f
#define SERVO_OPEN_ANGLE 90
#define SERVO_CLOSE_ANGLE 0

#endif // CONFIG_H
