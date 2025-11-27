FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required by Manim
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    build-essential \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirement.txt .

# Install Python dependencies
RUN pip install --no-cache-dir fastmcp manim

# Copy the server file
COPY manim_server.py .

# Create media directory for Manim output
RUN mkdir -p /app/media /app/media/manim_tmp

# Declare volume mount point for persistent storage
VOLUME ["/app/media"]

# Ensure unbuffered output for stdio
ENV PYTHONUNBUFFERED=1

# Run the server
CMD ["python", "manim_server.py"]
