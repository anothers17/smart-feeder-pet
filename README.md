# 🐾 Smart Pet Feeder IoT Project

![Smart Pet Feeder App]

> **IoT Project**  
> 🎓 **Department:** Electronic Engineering  
> 🏫 **University:** Suranaree University of Technology (SUT)

A professional, modular, and production-ready IoT system for automated pet feeding. This project features a dual-mode architecture supporting both **Real Hardware (ESP32)** and a **Virtual Simulator** for testing without physical components.

---

## ✨ Key Features

- **Dual Mode Support**: Switch between `SIMULATOR` and `REAL` hardware modes seamlessly.
- **Modular Architecture**: Clean separation between MQTT communication, Database logic, and GUI.
- **Configurable**: Environment-based configuration (no hard-coded credentials).
- **Responsive GUI**: Real-time updates for food levels, motor status, and feeding history.
- **Database Integration**: Tracks feeding history with month-based reporting and data visualization.
- **Smart Logic**: Automatic "Auto-90g" feeding mode and safety overflow protection.
- **Docker Ready**: One-click setup for MQTT Broker and MySQL Database using Docker Compose.

---

## 📂 Project Structure

```
smart-pet-feeder/
├── config/                 # System configuration & constants
├── src/
│   ├── mqtt/              # MQTT clients (Real + Simulator)
│   ├── database/          # Database handlers (Real + Mock)
│   ├── ui/                # PyQt5 GUI logic & design files
│   └── utils/             # Logging and helper utilities
├── simulator/             # Virtual device logic & simulator guide
├── mcu/                   # ESP32 firmware (C++/Arduino)
├── docs/                  # Setup guides, architecture, & PDF manuals
├── assets/                # Icons and documentation images
├── main.py               # Application entry point
├── manage.bat            # Project management automation script
└── docker-compose.yml    # Local services orchestration
```

---

## 🚀 Quick Start (Simulator Mode)

Test the entire system right now on your computer:

1.  **Prerequisites**: Install [Python 3.8+](https://www.python.org/).
2.  **Initialize**: Run `manage.bat` and select **Option 1 (Setup)** to install dependencies.
3.  **Run**: Select **Option 2 (Simulator)**.
    - The **Simulator Terminal** will open to act as your "Virtual ESP32".
    - The **Application GUI** will open for you to control the feeder.

---

## 🛠️ Real Hardware Setup

Ready to build the physical feeder? 
- Check the [Hardware Setup Guide](mcu/README.md) for wiring diagrams and firmware upload instructions.
- Uses **ESP32**, **Servo Motor**, and **HX711 Load Cell**.

---

## 🐳 Docker Services

For `REAL` mode or local service testing, you can spin up a local MQTT broker and MySQL database:
1.  Run `manage.bat` and select **Option 4 (Docker Up)**.
2.  Configuration is automatically handled via the `.env` file.

---

## 📜 Step-by-Step Guides

For detailed, step-by-step instructions on how to set up and run the project, please refer to:

- 💻 **[Simulator Setup Guide](docs/setup_simulator.md)** - For Windows users.
- 🍎 **[macOS & Linux Setup Guide](docs/setup_unix.md)** - For Unix-like systems.
- 🔧 **[Real Hardware Setup Guide](docs/setup_real.md)** - For assembling physical ESP32 hardware.
- 📦 **[Database & Docker Setup](docs/docker-setup.md)** - For initializing local services.

---

## 🏗️ Architecture & Technical Docs

- [System Architecture](docs/architecture.md)
- [MQTT Simulator Details](simulator/README.md)
- [Firmware Documentation](mcu/README.md)

---

## 🧪 Testing

The project includes a comprehensive suite of unit tests to ensure reliability:

1.  **Run Tests**:
    ```bash
    py -m pytest tests/
    ```
2.  **Coverage**:
    - **Settings**: Verifies environment variable loading and defaults.
    - **Simulator**: Validates feeding logic, auto-stop triggers, and eating behavior.

---

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
