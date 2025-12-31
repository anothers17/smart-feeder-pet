# Real Hardware Setup Guide

## Overview

This guide will help you set up the Smart Pet Feeder with real ESP32 hardware, MQTT broker, and MySQL database.

## Hardware Requirements

### Components Needed

1. **ESP32 Development Board** (any variant)
2. **Servo Motor** (SG90 or similar, 5V)
3. **LEDs** (2x, any color)
4. **Resistors** (2x 220Ω for LEDs)
5. **Breadboard and Jumper Wires**
6. **Power Supply** (5V, 2A recommended)
7. **USB Cable** (for programming ESP32)

### Optional Components

- Weight sensor (HX711 + Load Cell) for real weight measurement
- Enclosure/housing for the feeder
- Pet food container

## Wiring Diagram

\`\`\`
ESP32 Pin Connections:
┌─────────────────────────────────────┐
│ ESP32          →    Component       │
├─────────────────────────────────────┤
│ GPIO 2         →    WiFi LED        │
│ GPIO 18        →    Status LED      │
│ GPIO 13        →    Servo Signal    │
│ 5V             →    Servo VCC       │
│ GND            →    Servo GND       │
│ GND            →    LED Cathodes    │
└─────────────────────────────────────┘

LED Connections:
- WiFi LED: GPIO 2 → 220Ω Resistor → LED → GND
- Status LED: GPIO 18 → 220Ω Resistor → LED → GND

Servo Connections:
- Signal (Orange/Yellow): GPIO 13
- VCC (Red): 5V
- GND (Brown/Black): GND
\`\`\`

## Software Requirements

### 1. Arduino IDE Setup

1. Download and install [Arduino IDE](https://www.arduino.cc/en/software)

2. Add ESP32 board support:
   - Open Arduino IDE
   - Go to **File → Preferences**
   - Add to "Additional Board Manager URLs":
     \`\`\`
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     \`\`\`
   - Go to **Tools → Board → Boards Manager**
   - Search for "esp32" and install "esp32 by Espressif Systems"

3. Install required libraries:
   - Go to **Sketch → Include Library → Manage Libraries**
   - Install:
     - `PubSubClient` by Nick O'Leary
     - `ArduinoJson` by Benoit Blanchon
     - `ESP32Servo` by Kevin Harrington

### 2. MQTT Broker Setup

You have two options:

#### Option A: Use Public Broker (Testing Only)
- Use the default broker in config: `119.59.99.155:8883`
- **Not recommended for production**

#### Option B: Install Your Own Broker (Recommended)

**Using Mosquitto (Windows):**
\`\`\`bash
# Download from https://mosquitto.org/download/
# Install and run:
mosquitto -v
\`\`\`

**Using Docker:**
\`\`\`bash
docker run -d -p 1883:1883 -p 9001:9001 eclipse-mosquitto
\`\`\`

### 3. MySQL Database Setup

#### Option A: Local MySQL

1. Install [MySQL Server](https://dev.mysql.com/downloads/mysql/)

2. Create database and table:
\`\`\`sql
CREATE DATABASE smart_pet_feeder;
USE smart_pet_feeder;

CREATE TABLE feeding_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    food_weight FLOAT,
    amount FLOAT,
    status_mount VARCHAR(50),
    motor VARCHAR(10),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
\`\`\`

#### Option B: Docker MySQL

\`\`\`bash
docker run -d \\
  --name mysql-pet-feeder \\
  -e MYSQL_ROOT_PASSWORD=yourpassword \\
  -e MYSQL_DATABASE=smart_pet_feeder \\
  -p 3306:3306 \\
  mysql:8.0
\`\`\`

## Configuration

### 1. ESP32 Configuration

\`\`\`bash
# Navigate to MCU directory
cd mcu/smart_pet_feeder

# Copy config template
copy config.example.h config.h

# Edit config.h with your settings
notepad config.h
\`\`\`

Update the following in `config.h`:

\`\`\`cpp
// WiFi Settings
#define WIFI_SSID "YourWiFiNetwork"
#define WIFI_PASSWORD "YourWiFiPassword"

// MQTT Settings
#define MQTT_BROKER "your.mqtt.broker.ip"
#define MQTT_PORT 1883
#define MQTT_CLIENT_ID "esp32_pet_feeder_001"

// Adjust pins if needed
#define LED_PIN_WIFI 2
#define LED_PIN_STATUS 18
#define SERVO_PIN 13
\`\`\`

### 2. Application Configuration

\`\`\`bash
# Copy environment template
copy .env.example .env

# Edit .env
notepad .env
\`\`\`

Update the following in `.env`:

\`\`\`env
# Set to REAL mode
MODE=REAL

# MQTT Configuration
MQTT_BROKER=your.mqtt.broker.ip
MQTT_PORT=1883
MQTT_CLIENT_ID=smart_pet_feeder_app

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=smart_pet_feeder
\`\`\`

## Uploading Firmware

1. Connect ESP32 to computer via USB

2. Open Arduino IDE

3. Open `mcu/smart_pet_feeder/smart_pet_feeder.ino`

4. Select board:
   - **Tools → Board → ESP32 Arduino → ESP32 Dev Module**

5. Select port:
   - **Tools → Port → [Your ESP32 Port]**

6. Upload:
   - Click **Upload** button or press **Ctrl+U**

7. Monitor serial output:
   - **Tools → Serial Monitor**
   - Set baud rate to **115200**

You should see:
\`\`\`
========================================
Smart Pet Feeder - ESP32
========================================
Servo initialized
Connecting to WiFi...
WiFi connected!
IP Address: 192.168.1.xxx
MQTT connecting... connected!
========================================
\`\`\`

## Running the Application

\`\`\`bash
# Install Python dependencies
pip install -r requirements.txt

# Run the application
python main.py
\`\`\`

## Testing

### 1. Test MQTT Communication

In Serial Monitor, you should see:
\`\`\`
Published: {"food_weight":50,"amount":2950,"status_mount":"2950","motor":"close"}
\`\`\`

### 2. Test Control

Click buttons in the GUI:
- **FEED** → Servo should move to 90°, Status LED should turn ON
- **STOP** → Servo should move to 0°, Status LED should turn OFF
- **Fill Food** → Amount should reset to 3000g

### 3. Test Database

Check if data is being stored:
\`\`\`sql
SELECT * FROM feeding_history ORDER BY id DESC LIMIT 10;
\`\`\`

## Troubleshooting

### ESP32 Not Connecting to WiFi

1. Check WiFi credentials in `config.h`
2. Ensure WiFi network is 2.4GHz (ESP32 doesn't support 5GHz)
3. Check WiFi signal strength
4. Try different WiFi network

### MQTT Connection Failed

1. Verify MQTT broker is running
2. Check broker IP address and port
3. Test broker with MQTT client (e.g., MQTT Explorer)
4. Check firewall settings

### Database Connection Error

1. Verify MySQL is running
2. Check database credentials
3. Ensure database and table exist
4. Test connection with MySQL client

### Servo Not Moving

1. Check wiring connections
2. Verify servo power supply (needs 5V, sufficient current)
3. Test servo with simple sketch
4. Check GPIO pin assignment

### No Data in UI

1. Verify ESP32 is publishing data (check Serial Monitor)
2. Check MQTT broker logs
3. Verify application is connected to MQTT
4. Check database for new records

## Advanced Configuration

### Adding Real Weight Sensor

To replace simulated weight with real sensor (HX711):

1. Add HX711 library to Arduino IDE
2. Wire HX711 to ESP32:
   - DT → GPIO 4
   - SCK → GPIO 5
3. Modify firmware to read from HX711
4. Calibrate sensor

### Multiple Devices

To run multiple feeders:

1. Give each ESP32 unique `MQTT_CLIENT_ID`
2. Use different MQTT topics per device
3. Update application to handle multiple devices

### Remote Access

To access from outside your network:

1. Setup port forwarding for MQTT broker
2. Use dynamic DNS service
3. Consider VPN for security
4. Use SSL/TLS for MQTT

## Maintenance

### Regular Tasks

- Clean food container weekly
- Check servo operation monthly
- Backup database regularly
- Update firmware as needed

### Monitoring

- Check log files: `smart_pet_feeder.log`
- Monitor database size
- Check MQTT broker logs
- Verify WiFi connection stability

## Safety Notes

⚠️ **Important Safety Information:**

- Ensure proper power supply for servo (insufficient power can cause ESP32 resets)
- Keep electronics away from water
- Secure all wiring to prevent pet access
- Test thoroughly before leaving pet unattended
- Have backup feeding method available

---

**Need Help?** Open an issue on GitHub or check the [Architecture Documentation](architecture.md) for more details.
