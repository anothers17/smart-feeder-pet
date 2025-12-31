#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>
#include "config.h" // User must copy config.example.h to config.h

// Global Objects
WiFiClient espClient;
PubSubClient client(espClient);
Servo feederServo;

// Application State
float current_weight = 0.0f;
float food_mount = MAX_FOOD_CAPACITY;
int motor_state = 0; // 0: STOP, 1: OPEN
unsigned long last_publish_time = 0;
const unsigned long publish_interval = 2000;

// Function Prototypes
void setupWiFi();
void callback(char* topic, byte* payload, unsigned int length);
void reconnect();
void updateSensors();
void publishData();
void updateFoodMount(float weight_diff);

void setup() {
    Serial.begin(115200);
    
    // Initialize Hardware
    feederServo.attach(PIN_SERVO);
    feederServo.write(SERVO_CLOSE_ANGLE);
    
    // Setup Connectivity
    setupWiFi();
    client.setServer(MQTT_BROKER, MQTT_PORT);
    client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect(); // เชื่อมต่อ MQTT ใหม่ถ้าหลุด
  }
  client.loop();

  unsigned long now = millis();
  if (now - last_publish_time > publish_interval) { // ส่งข้อมูลตามช่วงเวลาที่กำหนด
    last_publish_time = now;
    
    updateSensors(); // อ่านค่าน้ำหนักจริงจาก Load Cell (หรือจำลองค่าใน Demo)
    publishData(); // ส่งข้อมูลสถานะปัจจุบันขึ้น MQTT
  }
}

void setupWiFi() {
    delay(10);
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(WIFI_SSID);

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
    Serial.print("Message arrived [");
    Serial.print(topic);
    Serial.print("] ");
    
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    Serial.println(message);

    // Minimal JSON parsing (can use ArduinoJson for more complex logic)
    if (message.indexOf("\"status\":\"on\"") >= 0) {
        Serial.println("Control: OPEN SERVO");
        feederServo.write(SERVO_OPEN_ANGLE);
        motor_state = 1;
    } 
    else if (message.indexOf("\"status\":\"off\"") >= 0) {
        Serial.println("Control: CLOSE SERVO");
        feederServo.write(SERVO_CLOSE_ANGLE);
        motor_state = 0;
    }
    else if (message.indexOf("\"status\":\"r\"") >= 0) {
        Serial.println("Control: RESET/FILL FOOD");
        // Fill logic usually handles motor until weight target
        // For simplicity: auto-feed to 90g
        if (current_weight < FEED_STOP_THRESHOLD) {
            feederServo.write(SERVO_OPEN_ANGLE);
            motor_state = 1;
        }
    }
}

void reconnect() {
    while (!client.connected()) {
        Serial.print("Attempting MQTT connection...");
        if (client.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASSWORD)) {
            Serial.println("connected");
            client.subscribe(TOPIC_CONTROL);
        } else {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
        }
    }
}

void updateSensors() {
    // In real app, read from HX711 Load Cell
    // float reading = scale.get_units(5);
    
    // Simulation logic for dummy values or safety checks
    if (motor_state == 1) {
        float feed_rate = 2.5f; // Simulation rate
        float diff = min(feed_rate, food_mount);
        current_weight += diff;
        updateFoodMount(diff);
        
        if (current_weight >= FEED_STOP_THRESHOLD) {
            Serial.println("Target reached. Closing.");
            feederServo.write(SERVO_CLOSE_ANGLE);
            motor_state = 0;
        }
    }
}

void updateFoodMount(float diff) {
    if (diff > 0) {
        food_mount = max(0.0f, food_mount - diff);
    }
}

void publishData() {
    String payload = "{";
    payload += "\"food_weight\":\"" + String(current_weight) + "\",";
    payload += "\"amount\":\"" + String(food_mount) + "\",";
    payload += "\"motor\":\"" + String(motor_state == 1 ? "OPEN" : "STOP") + "\",";
    payload += "\"status_mount\":\"" + String(food_mount <= 0 ? "empty" : "normal") + "\"";
    payload += "}";

    Serial.print("Publishing: ");
    Serial.println(payload);
    client.publish(TOPIC_MONITORING, payload.c_str());
}
