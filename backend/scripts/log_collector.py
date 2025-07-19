#!/usr/bin/env python3
"""
Log Collector for Update Scripts
Tails log files and parses them into the database for monitoring and analysis
"""

import os
import sys
import re
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# Add the parent directory to the path so we can import our models
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import UpdateLog, Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LogCollector:
    def __init__(self, log_file: str = "/var/log/update.log", db_url: Optional[str] = None):
        self.log_file = log_file
        self.db_url = db_url or os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/sannetic_explorer")
        self.engine = create_engine(self.db_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Regex patterns for parsing log lines
        self.patterns = {
            'script_start': re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - Starting script: (\w+)'),
            'script_end': re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - Script (\w+) completed in ([\d.]+) seconds'),
            'script_error': re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - ERROR in (\w+): (.+)'),
            'script_warning': re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - WARNING in (\w+): (.+)'),
            'script_info': re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - INFO: (.+)'),
            'cron_entry': re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - cron: (.+)'),
        }
        
        # Track script start times for duration calculation
        self.script_starts = {}
    
    def parse_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a log line and extract relevant information"""
        line = line.strip()
        if not line:
            return None
            
        # Try to match against each pattern
        for pattern_name, pattern in self.patterns.items():
            match = pattern.match(line)
            if match:
                if pattern_name == 'script_start':
                    timestamp_str, script_name = match.groups()
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    self.script_starts[script_name] = timestamp
                    return {
                        'timestamp': timestamp,
                        'script_name': script_name,
                        'status': 'info',
                        'message': f'Script {script_name} started',
                        'duration_sec': None,
                        'log_level': 'INFO'
                    }
                    
                elif pattern_name == 'script_end':
                    timestamp_str, script_name, duration_str = match.groups()
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    duration = float(duration_str)
                    start_time = self.script_starts.get(script_name)
                    
                    return {
                        'timestamp': timestamp,
                        'script_name': script_name,
                        'status': 'success',
                        'message': f'Script {script_name} completed successfully',
                        'duration_sec': duration,
                        'log_level': 'INFO'
                    }
                    
                elif pattern_name == 'script_error':
                    timestamp_str, script_name, error_msg = match.groups()
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    start_time = self.script_starts.get(script_name)
                    duration = None
                    if start_time:
                        duration = (timestamp - start_time).total_seconds()
                    
                    return {
                        'timestamp': timestamp,
                        'script_name': script_name,
                        'status': 'error',
                        'message': error_msg,
                        'duration_sec': duration,
                        'log_level': 'ERROR'
                    }
                    
                elif pattern_name == 'script_warning':
                    timestamp_str, script_name, warning_msg = match.groups()
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    return {
                        'timestamp': timestamp,
                        'script_name': script_name,
                        'status': 'warning',
                        'message': warning_msg,
                        'duration_sec': None,
                        'log_level': 'WARNING'
                    }
                    
                elif pattern_name == 'script_info':
                    timestamp_str, info_msg = match.groups()
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    return {
                        'timestamp': timestamp,
                        'script_name': 'system',
                        'status': 'info',
                        'message': info_msg,
                        'duration_sec': None,
                        'log_level': 'INFO'
                    }
                    
                elif pattern_name == 'cron_entry':
                    timestamp_str, cron_msg = match.groups()
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    return {
                        'timestamp': timestamp,
                        'script_name': 'cron',
                        'status': 'info',
                        'message': cron_msg,
                        'duration_sec': None,
                        'log_level': 'INFO'
                    }
        
        # If no pattern matches, create a generic entry
        try:
            # Try to extract timestamp from the beginning of the line
            timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
            if timestamp_match:
                timestamp_str = timestamp_match.group(1)
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                message = line[len(timestamp_str):].strip()
                
                return {
                    'timestamp': timestamp,
                    'script_name': 'unknown',
                    'status': 'info',
                    'message': message,
                    'duration_sec': None,
                    'log_level': 'INFO'
                }
        except:
            pass
            
        return None
    
    def save_log_entry(self, log_data: Dict[str, Any]) -> bool:
        """Save a log entry to the database"""
        try:
            session = self.Session()
            log_entry = UpdateLog(
                timestamp=log_data['timestamp'],
                script_name=log_data['script_name'],
                status=log_data['status'],
                message=log_data['message'],
                duration_sec=log_data['duration_sec'],
                log_level=log_data['log_level'],
                source_file=self.log_file
            )
            session.add(log_entry)
            session.commit()
            session.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save log entry: {e}")
            return False
    
    def tail_log_file(self):
        """Tail the log file and process new lines"""
        logger.info(f"Starting to tail log file: {self.log_file}")
        
        # Check if file exists
        if not os.path.exists(self.log_file):
            logger.error(f"Log file does not exist: {self.log_file}")
            return
        
        # Get initial file size
        with open(self.log_file, 'r') as f:
            f.seek(0, 2)  # Seek to end
            last_size = f.tell()
        
        while True:
            try:
                with open(self.log_file, 'r') as f:
                    f.seek(last_size)
                    new_lines = f.readlines()
                    last_size = f.tell()
                    
                    for line in new_lines:
                        log_data = self.parse_log_line(line)
                        if log_data:
                            if self.save_log_entry(log_data):
                                logger.debug(f"Saved log entry: {log_data['script_name']} - {log_data['status']}")
                            else:
                                logger.error(f"Failed to save log entry: {log_data}")
                
                time.sleep(1)  # Check every second
                
            except KeyboardInterrupt:
                logger.info("Log collector stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in log collector: {e}")
                time.sleep(5)  # Wait before retrying
    
    def process_existing_log(self):
        """Process the entire existing log file"""
        logger.info(f"Processing existing log file: {self.log_file}")
        
        if not os.path.exists(self.log_file):
            logger.warning(f"Log file does not exist: {self.log_file}")
            return
        
        with open(self.log_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                log_data = self.parse_log_line(line)
                if log_data:
                    if self.save_log_entry(log_data):
                        logger.debug(f"Processed line {line_num}: {log_data['script_name']} - {log_data['status']}")
                    else:
                        logger.error(f"Failed to process line {line_num}: {log_data}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Collect and parse update logs')
    parser.add_argument('--log-file', default='/var/log/update.log', help='Log file to monitor')
    parser.add_argument('--db-url', help='Database URL')
    parser.add_argument('--process-existing', action='store_true', help='Process existing log file and exit')
    parser.add_argument('--tail', action='store_true', help='Tail the log file (default)')
    
    args = parser.parse_args()
    
    collector = LogCollector(log_file=args.log_file, db_url=args.db_url)
    
    if args.process_existing:
        collector.process_existing_log()
    else:
        collector.tail_log_file()

if __name__ == "__main__":
    main() 