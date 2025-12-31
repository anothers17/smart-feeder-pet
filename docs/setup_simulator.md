# Simulator Mode Setup Guide

## Overview

Simulator mode allows you to run and test the Smart Pet Feeder application without any physical hardware. This is perfect for:

- Development and testing
- Demonstrations
- Learning the system
- CI/CD pipelines

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- No hardware required! 🎉

## Installation Steps

### 1. Install Python Dependencies

\`\`\`bash
# Navigate to project directory
cd "smart pet feeder/smart pet feeder"

# Install required packages
pip install -r requirements.txt
\`\`\`

### 2. Configure Environment

\`\`\`bash
# Copy the environment template
copy .env.example .env

# Open .env in your text editor
notepad .env
\`\`\`

### 3. Set Simulator Mode

In your `.env` file, ensure the following settings:

\`\`\`env
# Set mode to SIMULATOR
MODE=SIMULATOR

# MQTT settings (can use defaults for simulator)
MQTT_BROKER=localhost
MQTT_PORT=8883
MQTT_CLIENT_ID=smart_pet_feeder_app

# Other settings can remain as default
\`\`\`

## Running the Simulator

You need to run **two** programs:

### Terminal 1: Virtual Device

This simulates the ESP32 hardware:

\`\`\`bash
python simulator/virtual_device.py
\`\`\`

You should see:
\`\`\`
============================================================
🤖 Virtual ESP32 Device Running
============================================================
📡 MQTT Broker: localhost:8883
📊 Publishing to: IoT/project/monitoring
🎮 Listening on: IoT/project/control
🍖 Initial food capacity: 3000g
⏱️  Update interval: 10s
============================================================
\`\`\`

### Terminal 2: GUI Application

This runs the user interface:

\`\`\`bash
python main.py
\`\`\`

You should see the GUI window open with the Smart Pet Feeder interface.

## Using the Simulator

### Control Buttons

- **FEED**: Opens the virtual servo motor
- **STOP**: Closes the virtual servo motor
- **Fill Food**: Resets food capacity to 3000g

### Monitoring

- **Status**: Shows current food weight in bowl
- **Amount**: Shows remaining food in container
- **Graph**: Select a month to view feeding history

### What's Being Simulated

1. **Weight Sensor**: Randomly changes to simulate pet eating
2. **Food Capacity**: Decreases as food is dispensed
3. **Servo Motor**: Opens/closes based on commands
4. **MQTT Communication**: In-memory message queue
5. **Database**: In-memory storage with optional JSON persistence

## Data Persistence

By default, simulator data is stored in memory and lost when you close the application.

To persist data between runs, the mock database saves to:
\`\`\`
simulator/data/feeding_history.json
\`\`\`

This file is automatically created and updated.

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Ensure all dependencies are installed:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### Issue: Virtual device not connecting

**Solution**: Make sure both programs are using the same MQTT settings in `.env`

### Issue: No data showing in UI

**Solution**: 
1. Ensure virtual device is running first
2. Wait 10 seconds for first data update
3. Check console for error messages

### Issue: Graph shows "No Data Available"

**Solution**: The mock database generates 30 days of historical data. Select the current month or previous months to see data.

## Advanced Configuration

### Changing Update Intervals

In `.env`:
\`\`\`env
# UI update interval (milliseconds)
UI_UPDATE_INTERVAL=5000

# In virtual_device.py, you can modify:
# SIMULATOR_UPDATE_INTERVAL = 10  # seconds
\`\`\`

### Customizing Simulated Behavior

Edit `simulator/virtual_device.py` to modify:
- Weight change ranges
- Food consumption rate
- Update frequency
- Initial values

### Generating More Historical Data

Edit `src/database/mock_db.py`:
\`\`\`python
# Change days parameter in _generate_mock_data
self._generate_mock_data(days=90)  # 90 days of data
\`\`\`

## Next Steps

Once you're comfortable with the simulator:

1. Review the [Architecture Documentation](architecture.md)
2. Explore the codebase
3. Try modifying the virtual device behavior
4. Set up real hardware (see [setup_real.md](setup_real.md))

## Tips for Development

- Keep both terminals visible to see real-time communication
- Use the log files for debugging (`smart_pet_feeder.log`)
- Experiment with different feeding patterns
- Test edge cases (empty food, full capacity, etc.)

---

**Happy Simulating! 🚀**
