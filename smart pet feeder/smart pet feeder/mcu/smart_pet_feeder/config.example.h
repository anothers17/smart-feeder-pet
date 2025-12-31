#ifndef CONFIG_H
#define CONFIG_H

// WiFi Configuration
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// MQTT Configuration
#define MQTT_BROKER "119.59.99.155"
#define MQTT_PORT 8883
#define MQTT_USER "std_elect3"
#define MQTT_PASSWORD "std_elect3"
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
