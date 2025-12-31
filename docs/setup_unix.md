# 🐧 macOS & Linux Setup Guide

This guide provides instructions for setting up the Smart Pet Feeder project on Unix-like systems (Linux, macOS, WSL2).

---

## 🛠️ Prerequisites

- **Python 3.8+**: Usually pre-installed. Check with `python3 --version`.
- **Make**: Essential for using the automation commands.
- **Python-venv**: Some Linux distros (like Ubuntu) require a separate package:
  ```bash
  sudo apt install python3-venv python3-pip
  ```
- **Docker & Docker Compose**: (Optional) For running the MQTT broker and MySQL database.

---

## ⚡ Quick Start (Automation)

Linux and macOS users should use the provided **`Makefile`** for the best experience.

### 1. Project Initialization
```bash
# Install dependencies
make install

# Setup environment variables
make setup-env
```

### 2. Running the Simulator
To run the full simulator environment (Virtual Device + GUI):
```bash
make run-sim
```
*Note: This will launch the virtual device in the background and the GUI in the foreground.*

### 3. Managing Services (Docker)
```bash
# Start MQTT and MySQL
make docker-up

# Stop all services
make docker-down
```

---

## 🕹️ Manual Setup

If you prefer manual control:

### 1. Install Dependencies
```bash
python3 -m pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
nano .env # or your favorite editor
```

### 3. Run Components
Open **two terminals**:

- **Terminal 1 (Device)**: `python3 simulator/virtual_device.py`
- **Terminal 2 (GUI)**: `python3 main.py`

---

## 🔧 Troubleshooting (Unix Specific)

### 1. PyQt5 Visual Issues
In some Linux distributions (like Ubuntu/Debian), you might need additional system libraries:
```bash
sudo apt install libxcb-xinerama0 libqt5gui5
```

### 2. macOS "Command Not Found"
If `make` is not found on macOS, install Xcode Command Line Tools:
```bash
xcode-select --install
```

### 3. Permission Denied (Serial Port)
If uploading to ESP32 fails on Linux:
```bash
sudo usermod -a -G dialout $USER
# (Log out and log back in for changes to take effect)
```

### 3. Python Command
On most Unix systems, use `python3` instead of `python` and `pip3` instead of `pip`. The `Makefile` handles this automatically using `$(shell which python3)`.

---

## 🚀 Comparison

| Feature | Windows | macOS / Linux |
| :--- | :--- | :--- |
| **Automation** | `manage.bat` | `Makefile` / `make` |
| **Python** | `python` / `py` | `python3` |
| **Config** | `copy` / `notepad` | `cp` / `nano` / `vim` |

---
**Happy Coding! 🍎🐧**
