# Docker Setup Guide

## Overview

Docker simplifies the deployment of Smart Pet Feeder by containerizing all services:
- MQTT Broker (Mosquitto)
- MySQL Database
- Virtual Device Simulator

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed
- Docker Compose (included with Docker Desktop)

## Quick Start

### 1. Start All Services

\`\`\`bash
# Navigate to project directory
cd "smart pet feeder/smart pet feeder"

# Start all services in background
docker-compose up -d
\`\`\`

This will start:
- ✅ MQTT Broker on port 1883 (and WebSocket on 9001)
- ✅ MySQL Database on port 3306
- ✅ Virtual Device Simulator

### 2. Run the GUI Application

The GUI needs to run on your host machine (not in Docker) for display:

\`\`\`bash
# Copy Docker environment config
copy .env.docker .env

# Install Python dependencies (if not already done)
pip install -r requirements.txt

# Run the application
python main.py
\`\`\`

### 3. Verify Everything is Running

\`\`\`bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f simulator
docker-compose logs -f mqtt
docker-compose logs -f database
\`\`\`

## Service Details

### MQTT Broker (Mosquitto)

- **Port**: 1883 (MQTT), 9001 (WebSocket)
- **Config**: `docker/mosquitto/config/mosquitto.conf`
- **Data**: `docker/mosquitto/data/`
- **Logs**: `docker/mosquitto/log/`

Test connection:
\`\`\`bash
# Using mosquitto_sub (if installed)
mosquitto_sub -h localhost -p 1883 -t "IoT/project/#" -v
\`\`\`

### MySQL Database

- **Port**: 3306
- **Database**: `smart_pet_feeder`
- **User**: `feeder_user`
- **Password**: `smartfeeder123`
- **Init Script**: `docker/mysql/init/01-create-tables.sql`

Connect to database:
\`\`\`bash
# Using Docker
docker-compose exec database mysql -u feeder_user -p smart_pet_feeder

# Using MySQL client
mysql -h localhost -P 3306 -u feeder_user -p smart_pet_feeder
\`\`\`

View data:
\`\`\`sql
SELECT * FROM feeding_history ORDER BY id DESC LIMIT 10;
\`\`\`

### Virtual Device Simulator

- **Container**: `smart-feeder-simulator`
- **Mode**: Automatically set to SIMULATOR
- **Publishes to**: `IoT/project/monitoring`
- **Subscribes to**: `IoT/project/control`

View simulator logs:
\`\`\`bash
docker-compose logs -f simulator
\`\`\`

## Common Commands

### Start Services

\`\`\`bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d mqtt
docker-compose up -d database
docker-compose up -d simulator

# Start with logs visible
docker-compose up
\`\`\`

### Stop Services

\`\`\`bash
# Stop all services
docker-compose down

# Stop and remove volumes (deletes data!)
docker-compose down -v
\`\`\`

### Restart Services

\`\`\`bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart simulator
\`\`\`

### View Logs

\`\`\`bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f simulator

# Last 100 lines
docker-compose logs --tail=100
\`\`\`

### Rebuild Images

\`\`\`bash
# Rebuild after code changes
docker-compose build

# Rebuild and restart
docker-compose up -d --build
\`\`\`

## Configuration

### Environment Variables

Edit `docker-compose.yml` to change:

\`\`\`yaml
environment:
  MYSQL_ROOT_PASSWORD: your_password
  MYSQL_DATABASE: your_database
  MYSQL_USER: your_user
  MYSQL_PASSWORD: your_password
\`\`\`

### MQTT Configuration

Edit `docker/mosquitto/config/mosquitto.conf` for:
- Authentication
- Access control
- Logging levels
- Connection limits

### Database Initialization

Edit `docker/mysql/init/01-create-tables.sql` to:
- Modify table schema
- Add more sample data
- Create additional tables

## Troubleshooting

### Services Won't Start

\`\`\`bash
# Check if ports are already in use
netstat -an | findstr "1883 3306"

# View detailed logs
docker-compose logs

# Remove and recreate
docker-compose down -v
docker-compose up -d
\`\`\`

### Database Connection Failed

\`\`\`bash
# Wait for database to be ready
docker-compose logs database

# Check health status
docker-compose ps

# Verify credentials in .env match docker-compose.yml
\`\`\`

### MQTT Connection Failed

\`\`\`bash
# Check MQTT broker logs
docker-compose logs mqtt

# Test MQTT connection
docker-compose exec mqtt mosquitto_sub -t "#" -v
\`\`\`

### Simulator Not Publishing

\`\`\`bash
# Check simulator logs
docker-compose logs -f simulator

# Restart simulator
docker-compose restart simulator

# Rebuild simulator
docker-compose up -d --build simulator
\`\`\`

## Data Persistence

Data is stored in Docker volumes:

- **MQTT Data**: `docker/mosquitto/data/`
- **MySQL Data**: `docker/mysql/data/`
- **Logs**: `docker/mosquitto/log/`

To backup:
\`\`\`bash
# Backup MySQL
docker-compose exec database mysqldump -u feeder_user -p smart_pet_feeder > backup.sql

# Restore MySQL
docker-compose exec -T database mysql -u feeder_user -p smart_pet_feeder < backup.sql
\`\`\`

## Production Deployment

For production use:

1. **Change default passwords** in `docker-compose.yml`
2. **Enable MQTT authentication** in mosquitto.conf
3. **Use environment files** for secrets
4. **Setup SSL/TLS** for MQTT and MySQL
5. **Configure backups** for database
6. **Use Docker secrets** for sensitive data

Example with secrets:
\`\`\`yaml
services:
  database:
    environment:
      MYSQL_ROOT_PASSWORD_FILE: /run/secrets/db_root_password
    secrets:
      - db_root_password

secrets:
  db_root_password:
    file: ./secrets/db_root_password.txt
\`\`\`

## Advanced Usage

### Running on Remote Server

\`\`\`bash
# SSH to server
ssh user@your-server

# Clone repository
git clone <repo-url>
cd smart-pet-feeder

# Start services
docker-compose up -d

# Access from local machine
# Update .env with server IP
MQTT_BROKER=your-server-ip
DB_HOST=your-server-ip
\`\`\`

### Multiple Environments

\`\`\`bash
# Development
docker-compose -f docker-compose.yml up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
\`\`\`

### Monitoring

\`\`\`bash
# Resource usage
docker stats

# Inspect container
docker inspect smart-feeder-mqtt

# Network inspection
docker network inspect smart-feeder-network
\`\`\`

## Benefits of Docker Setup

✅ **Easy Setup**: One command to start everything
✅ **Consistency**: Same environment everywhere
✅ **Isolation**: Services don't conflict with host
✅ **Portability**: Run on any OS with Docker
✅ **Scalability**: Easy to add more services
✅ **Development**: Quick teardown and rebuild

## Next Steps

- Review [Architecture Documentation](architecture.md)
- Try [Simulator Setup](setup_simulator.md)
- Deploy to [Real Hardware](setup_real.md)

---

**Happy Dockerizing! 🐳**
