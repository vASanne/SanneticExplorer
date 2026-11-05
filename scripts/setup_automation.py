#!/usr/bin/env python3
"""
Setup Automation Script for Sannetic Explorer
Configures automated update scheduling with cron jobs
"""

import os
import sys
import subprocess
from pathlib import Path
from logger_config import get_logger

def create_cron_schedule():
    """Create the cron schedule configuration"""
    logger = get_logger('cron_setup')
    
    # Cron schedule configuration
    cron_schedule = """# Sannetic Explorer Automated Update Schedule
# Format: minute hour day_of_month month day_of_week user command

# Critical updates every 6 hours (00:00, 06:00, 12:00, 18:00 UTC)
0 */6 * * * root cd /app && make update-critical >> /var/log/sannetic-cron.log 2>&1

# Standard updates every 12 hours (02:00, 14:00 UTC)
0 2,14 * * * root cd /app && make update-optimized >> /var/log/sannetic-cron.log 2>&1

# Full system update daily at 01:00 UTC
0 1 * * * root cd /app && make update-full >> /var/log/sannetic-cron.log 2>&1

# Health check every hour
0 * * * * root cd /app && make status >> /var/log/sannetic-health.log 2>&1

# Log rotation weekly on Sunday at 03:00 UTC
0 3 * * 0 root cd /app && find logs/ -name "*.log" -mtime +7 -delete >> /var/log/sannetic-cron.log 2>&1
"""
    
    # Write cron schedule
    cron_file = Path("crontab")
    try:
        with open(cron_file, 'w') as f:
            f.write(cron_schedule)
        logger.info(f"Created cron schedule: {cron_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to create cron schedule: {e}")
        return False

def create_startup_script():
    """Create startup script for the container"""
    logger = get_logger('startup_setup')
    
    startup_script = """#!/bin/bash
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
"""
    
    startup_file = Path("startup.sh")
    try:
        with open(startup_file, 'w') as f:
            f.write(startup_script)
        
        # Make executable
        os.chmod(startup_file, 0o755)
        logger.info(f"Created startup script: {startup_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to create startup script: {e}")
        return False

def update_dockerfile():
    """Update Dockerfile to support automation"""
    logger = get_logger('dockerfile_setup')
    
    dockerfile_additions = """
# Add cron support for automation
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Copy automation files
COPY crontab /app/crontab
COPY startup.sh /app/startup.sh

# Make startup script executable
RUN chmod +x /app/startup.sh

# Set default command to startup script
CMD ["/app/startup.sh"]
"""
    
    dockerfile_path = Path("Dockerfile")
    if not dockerfile_path.exists():
        logger.error("Dockerfile not found!")
        return False
    
    try:
        # Read current Dockerfile
        with open(dockerfile_path, 'r') as f:
            current_content = f.read()
        
        # Check if automation is already added
        if "cron" in current_content and "startup.sh" in current_content:
            logger.info("Dockerfile already contains automation setup")
            return True
        
        # Add automation setup before the last CMD
        lines = current_content.split('\n')
        
        # Find the last CMD line
        cmd_index = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('CMD'):
                cmd_index = i
        
        if cmd_index >= 0:
            # Insert automation setup before CMD
            lines[cmd_index:cmd_index] = dockerfile_additions.strip().split('\n')
        else:
            # Append automation setup
            lines.extend(dockerfile_additions.strip().split('\n'))
        
        # Write updated Dockerfile
        with open(dockerfile_path, 'w') as f:
            f.write('\n'.join(lines))
        
        logger.info("Updated Dockerfile with automation support")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update Dockerfile: {e}")
        return False

def create_docker_compose_override():
    """Create docker-compose override for automation"""
    logger = get_logger('compose_setup')
    
    override_content = """# Docker Compose Override for Automation
version: '3.8'

services:
  sannetic-explorer:
    # Override command for automation mode
    command: ["/app/startup.sh"]
    
    # Add health check
    healthcheck:
      test: ["CMD", "python", "/app/scripts/status_report.py"]
      interval: 30m
      timeout: 10s
      retries: 3
      start_period: 5m
    
    # Restart policy for automation
    restart: unless-stopped
    
    # Additional volumes for logs
    volumes:
      - ./logs:/app/logs:rw
      - /var/log:/var/log:rw
"""
    
    override_file = Path("docker-compose.automation.yml")
    try:
        with open(override_file, 'w') as f:
            f.write(override_content)
        logger.info(f"Created docker-compose override: {override_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to create docker-compose override: {e}")
        return False

def setup_manual_cron():
    """Setup manual cron jobs for development"""
    logger = get_logger('manual_cron')
    
    logger.info("Setting up manual cron jobs...")
    
    # Create wrapper scripts for manual execution
    scripts = {
        'critical-update.sh': 'cd /app && make update-critical',
        'standard-update.sh': 'cd /app && make update-optimized', 
        'full-update.sh': 'cd /app && make update-full',
        'health-check.sh': 'cd /app && make status'
    }
    
    scripts_dir = Path("automation-scripts")
    scripts_dir.mkdir(exist_ok=True)
    
    for script_name, command in scripts.items():
        script_path = scripts_dir / script_name
        script_content = f"""#!/bin/bash
# Sannetic Explorer - {script_name}
echo "🚀 Running {script_name}..."
{command}
echo "✅ {script_name} completed"
"""
        try:
            with open(script_path, 'w') as f:
                f.write(script_content)
            os.chmod(script_path, 0o755)
            logger.info(f"Created automation script: {script_path}")
        except Exception as e:
            logger.error(f"Failed to create {script_name}: {e}")
            return False
    
    return True

def main():
    """Main setup function"""
    logger = get_logger('automation_setup')
    logger.section_start("Sannetic Explorer Automation Setup")
    
    setup_tasks = [
        ("Creating cron schedule", create_cron_schedule),
        ("Creating startup script", create_startup_script),
        ("Updating Dockerfile", update_dockerfile),
        ("Creating docker-compose override", create_docker_compose_override),
        ("Setting up manual scripts", setup_manual_cron)
    ]
    
    success_count = 0
    for task_name, task_func in setup_tasks:
        logger.info(f"📋 {task_name}...")
        if task_func():
            success_count += 1
            logger.info(f"✅ {task_name} completed")
        else:
            logger.error(f"❌ {task_name} failed")
    
    # Summary
    total_tasks = len(setup_tasks)
    logger.summary("Automation Setup Results", {
        "Total Tasks": total_tasks,
        "Successful": success_count,
        "Failed": total_tasks - success_count,
        "Success Rate": f"{(success_count/total_tasks)*100:.1f}%"
    })
    
    if success_count == total_tasks:
        logger.section_end("Automation Setup", success=True)
        logger.info("🎉 Automation setup completed successfully!")
        logger.info("📋 Next steps:")
        logger.info("  1. Rebuild container: make build")
        logger.info("  2. Start automation: docker compose -p sannetic-explorer -f docker-compose.yml -f docker-compose.automation.yml up -d")
        logger.info("  3. Monitor logs: make tail-logs")
        return 0
    else:
        logger.section_end("Automation Setup", success=False)
        logger.warning("⚠️ Automation setup completed with errors")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 