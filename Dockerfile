# Smart Pet Feeder - Docker Image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PyQt5
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libqt5gui5 \
    libqt5widgets5 \
    libqt5core5a \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV QT_QPA_PLATFORM=offscreen

# Default command (can be overridden)
CMD ["python", "main.py"]
