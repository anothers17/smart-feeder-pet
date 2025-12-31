# System Architecture

## Overview

The Smart Pet Feeder is built on a layered architecture that separates concerns and enables both simulator and real hardware modes.

## Architecture Layers

### 1. Presentation Layer (UI)
- **Technology**: PyQt5
- **Responsibility**: User interaction, data visualization
- **Components**:
  - Main Window (`main_window.py`)
  - Generated UI (`petfeed.py`)
  - Graph widgets (pyqtgraph)

### 2. Business Logic Layer
- **Responsibility**: Application logic, mode switching
- **Components**:
  - MQTT Client (`mqtt/client.py`)
  - MQTT Simulator (`mqtt/simulator.py`)
  - Database Handler (`database/handler.py`)
  - Mock Database (`database/mock_db.py`)
  - Configuration Manager (`config/settings.py`)

### 3. Communication Layer
- **Technology**: MQTT Protocol
- **Broker**: External MQTT broker
- **Topics**:
  - Control: `IoT/project/control`
  - Monitoring: `IoT/project/monitoring`

### 4. Device Layer
- **Hardware**: ESP32 microcontroller
- **Components**:
  - Servo motor (food dispensing)
  - Weight sensor (simulated)
  - WiFi module
  - LED indicators

## Component Interaction

```text
┌─────────────────────────────────────────────────────────┐
│                    Application (main.py)                 │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │  Settings  │  │  Initialize  │  │  Dependency     │ │
│  │  Loader    │→ │  Components  │→ │  Injection      │ │
│  └────────────┘  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                      UI Layer (PyQt5)                    │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Main Window                                        │ │
│  │  - Feed Control Buttons                            │ │
│  │  - Status Display                                  │ │
│  │  - Graph Visualization                             │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
         ↓                              ↓
┌──────────────────────┐    ┌──────────────────────┐
│   MQTT Client        │    │  Database Handler    │
│  (Real/Simulator)    │    │  (Real/Mock)         │
└──────────────────────┘    └──────────────────────┘
         ↓                              ↓
┌──────────────────────┐    ┌──────────────────────┐
│   MQTT Broker        │    │  MySQL Database      │
└──────────────────────┘    └──────────────────────┘
         ↓
┌──────────────────────┐
│   ESP32 Device       │
│  - Servo Control     │
│  - Sensor Reading    │
└──────────────────────┘
```

## Mode Architecture

### Simulator Mode

```text
Application → MQTT Simulator → Virtual Device
     ↓
Mock Database (in-memory)
```

- No external dependencies
- In-memory message queue
- Simulated sensor data
- Perfect for development and demos

### Real Mode

```text
Application → MQTT Client → MQTT Broker → ESP32
     ↓
MySQL Database
```

- Requires MQTT broker
- Requires MySQL database
- Real hardware communication
- Production deployment

## Data Flow

### Control Flow (User → Device)

1. User clicks button in UI
2. UI calls MQTT client publish method
3. MQTT client sends JSON message to broker
4. Broker forwards to ESP32 (subscribed to control topic)
5. ESP32 parses message and controls hardware
6. ESP32 publishes status update

### Monitoring Flow (Device → User)

1. ESP32 reads sensors
2. ESP32 publishes JSON data to monitoring topic
3. MQTT broker forwards to application
4. Application stores data in database
5. UI queries database for display
6. UI updates widgets with latest data

### Graph Data Flow

1. User selects month from dropdown
2. UI queries database for monthly data
3. Database returns list of (weight, timestamp) tuples
4. UI processes data and updates graph widget

## Configuration Management

```text
.env file
    ↓
Settings.py (loads and validates)
    ↓
Application components (injected)
```

All configuration is centralized in `.env` file and loaded through `Settings` class, which:
- Validates required fields
- Provides type conversion
- Supports mode-specific validation
- Offers default values

## Error Handling Strategy

1. **Logging**: All errors logged with context
2. **Graceful Degradation**: UI shows error messages instead of crashing
3. **Retry Logic**: MQTT connection retries automatically
4. **Validation**: Configuration validated at startup

## Security Considerations

1. **Credentials**: Never committed to git (`.env` in `.gitignore`)
2. **Config Files**: Template files provided (`config.example.h`)
3. **MQTT**: Supports username/password authentication
4. **Database**: Connection credentials externalized

## Scalability

The architecture supports:
- Multiple device connections (unique client IDs)
- Database connection pooling
- Asynchronous MQTT communication
- Modular component replacement
