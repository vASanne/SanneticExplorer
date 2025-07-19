# Use Python 3.13 slim image as base
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create necessary directories if they don't exist
RUN mkdir -p Data/Planets \
    Data/NaturalSatellites \
    Data/Spacecraft \
    Data/Stars

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command
# Add cron support for automation
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Copy automation files
COPY crontab /app/crontab
COPY startup.sh /app/startup.sh

# Make startup script executable
RUN chmod +x /app/startup.sh

# Set default command to startup script
CMD ["/app/startup.sh"]
CMD ["python", "scripts/update_templates.py"] 