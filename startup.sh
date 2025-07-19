#!/bin/bash
# Sannetic Explorer Container Startup Script

echo "🚀 Starting Sannetic Explorer Container..."

# Start cron service
service cron start
echo "✅ Cron service started"

# Install cron jobs
if [ -f /app/crontab ]; then
    crontab /app/crontab
    echo "✅ Cron jobs installed"
else
    echo "⚠️ No crontab file found, skipping cron setup"
fi

# Create log directories
mkdir -p /var/log
mkdir -p /app/logs
echo "✅ Log directories created"

# Run initial status check
cd /app
python scripts/status_report.py
echo "✅ Initial status check completed"

# Keep container running
echo "🔄 Container ready - automation active"
tail -f /var/log/sannetic-cron.log /var/log/sannetic-health.log
