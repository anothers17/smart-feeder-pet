# 🤖 ESP32 Smart Pet Feeder - Real Hardware Setup

Welcome to the hardware setup guide for the Smart Pet Feeder! If you have the physical components ready, follow these steps to get your feeder up and running.

---

## 🔌 Wiring Diagram

Connect your components to the ESP32 according to the pinout table below:

| Component | Pin Label | ESP32 Pin (GPIO) | Notes |
| :--- | :--- | :--- | :--- |
| **Servo Motor** | Signal (Orange/Yellow) | **GPIO 18** | Connect VCC to 5V and GND as well |
| **HX711 (Load Cell)** | DT (Data) | **GPIO 19** | For food weight measurement |
| **HX711 (Load Cell)** | SCK (Clock) | **GPIO 21** | For food weight measurement |
| **Power Supply** | Vin / 5V | VIN | Recommended: 5V 2A Adapter |
| **Power Supply** | GND | GND | Common ground for all components |

---

## 💻 Arduino IDE Setup

Prepare your environment to upload the firmware to the ESP32:

1.  **Install Arduino IDE**: Download it from [arduino.cc](https://www.arduino.cc/en/software)
2.  **Configure ESP32 Board**:
    - Go to `File` -> `Preferences`
    - In `Additional Boards Manager URLs`, enter:
      `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
    - Go to `Tools` -> `Board` -> `Boards Manager`, search for **esp32**, and click Install
3.  **Install Libraries**:
    Go to `Sketch` -> `Include Library` -> `Manage Libraries` and search for/install:
    - **PubSubClient** (by Nick O'Leary) - For MQTT communication
    - **ESP32Servo** (by Kevin Harrington) - For servo control
    - **HX711 Arduino Library** (by Bogdan Necula) - For the load cell

---

## 🚀 Uploading Firmware

Once your IDE is ready and wiring is complete:

1.  **Open Project**: Open `mcu/smart_pet_feeder/smart_pet_feeder.ino`
2.  **Configuration**: 
    - Copy `config.example.h` and rename it to **`config.h`**
    - Open `config.h` and enter your WiFi SSID, Password, and MQTT details.
3.  **Select Board**: 
    - Go to `Tools` -> `Board` -> `ESP32 Arduino` -> Select your model (e.g., **DOIT ESP32 DEVKIT V1**)
4.  **Select Port**: 
    - Connect the ESP32 via USB and go to `Tools` -> `Port` to select the corresponding COM Port.
5.  **Upload**: 
    - Click the **Upload** arrow (->) and wait for "Done uploading".

---

## 🔍 Verification

- Open the **Serial Monitor** (magnifying glass icon in the top right).
- Set the Baud Rate to **115200**.
- You should see messages like "WiFi connected" and "connected" (meaning MQTT is successful).

---

> [!TIP]
> If the upload fails to connect, try holding the **BOOT** button on the ESP32 when the "Connecting......." message appears in the console.
