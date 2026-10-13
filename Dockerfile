# Production Dockerfile for Cambodia Logistics Telegram Bot
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables for unbuffered logging and UTF-8
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Install build dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run unified runner (starts both Bot and 3x/day Scheduler)
CMD ["python", "run_all.py"]
