.PHONY: setup install run run-sim test clean docker-up docker-down

# Python command - Use 'py' on Windows for compatibility
ifeq ($(OS),Windows_NT)
PYTHON ?= py
else
PYTHON ?= python3
endif
PIP := $(PYTHON) -m pip

# Setup virtual environment and install dependencies
setup:
	$(PYTHON) -m venv venv
	@echo "Virtual environment created."
	@echo "Windows: .\\venv\\Scripts\\activate"
	@echo "Linux/Mac: source venv/bin/activate"

# Install dependencies
install:
	$(PIP) install -r requirements.txt

# Run Real Mode Application
run:
	$(PYTHON) main.py

# Run Simulator Mode (Virtual Device + App)
run-sim:
	@echo "Starting Simulator using $(PYTHON)..."
# Check OS for start command behavior
ifeq ($(OS),Windows_NT)
	start "Simulator" cmd /k "$(PYTHON) simulator/virtual_device.py"
else
	$(PYTHON) simulator/virtual_device.py &
endif
	@echo "Starting App..."
	$(PYTHON) main.py

# Docker commands
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Run Tests
test:
	$(PYTHON) -m pytest

test-v:
	$(PYTHON) -m pytest -v

# Clean up temporary files
clean:
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf */*/__pycache__
