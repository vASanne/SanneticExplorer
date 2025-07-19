#!/usr/bin/env python3
"""
Logging Configuration for Sannetic Explorer
Provides timestamped log files and clean console output
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

class ColoredConsoleFormatter(logging.Formatter):
    """Custom formatter for colored console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[41m', # Red background
    }
    
    RESET = '\033[0m'
    
    ICONS = {
        'DEBUG': '🔍',
        'INFO': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨',
    }
    
    def format(self, record):
        # Get color and icon for log level
        color = self.COLORS.get(record.levelname, '')
        icon = self.ICONS.get(record.levelname, '•')
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Create clean message format
        if record.levelname == 'INFO':
            # For INFO messages, just show the message with icon
            return f"{color}{icon} {record.getMessage()}{self.RESET}"
        else:
            # For other levels, show timestamp and level
            return f"{color}{icon} [{timestamp}] {record.levelname}: {record.getMessage()}{self.RESET}"

class FileFormatter(logging.Formatter):
    """Detailed formatter for log files"""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

class SanneticLogger:
    """Main logger class for Sannetic Explorer"""
    
    def __init__(self, name: str, log_level: str = 'INFO'):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup console and file handlers"""
        
        # Create logs directory
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Generate timestamped log filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f"sannetic_explorer_{timestamp}.log"
        
        # Console handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredConsoleFormatter())
        
        # File handler with detailed logging
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(FileFormatter())
        
        # Add handlers to logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
        # Log the log file location
        self.logger.info(f"Logging to file: {log_file}")
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)
    
    def api_call(self, api_name: str, endpoint: str, status: str, details: str = ""):
        """Log API call with special formatting"""
        if status.lower() == 'success':
            self.logger.info(f"API {api_name}: {endpoint} → {status} {details}")
        else:
            self.logger.error(f"API {api_name}: {endpoint} → {status} {details}")
    
    def progress(self, current: int, total: int, item: str = ""):
        """Log progress with percentage"""
        percentage = (current / total) * 100 if total > 0 else 0
        progress_bar = self._create_progress_bar(percentage)
        self.logger.info(f"Progress: {progress_bar} {current}/{total} ({percentage:.1f}%) {item}")
    
    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Create a visual progress bar"""
        filled = int(width * percentage / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}]"
    
    def section_start(self, section_name: str):
        """Log the start of a major section"""
        separator = "=" * 60
        self.logger.info(f"\n{separator}")
        self.logger.info(f"🚀 Starting: {section_name}")
        self.logger.info(f"{separator}")
    
    def section_end(self, section_name: str, success: bool = True):
        """Log the end of a major section"""
        status = "✅ COMPLETED" if success else "❌ FAILED"
        self.logger.info(f"📋 {section_name}: {status}")
    
    def summary(self, title: str, data: dict):
        """Log a formatted summary"""
        self.logger.info(f"\n📊 {title}")
        self.logger.info("─" * 40)
        for key, value in data.items():
            self.logger.info(f"  {key}: {value}")
        self.logger.info("─" * 40)

def get_logger(name: str, log_level: str = 'INFO') -> SanneticLogger:
    """Get a configured logger instance"""
    return SanneticLogger(name, log_level)

# Convenience functions for quick logging
def log_api_call(api_name: str, endpoint: str, status: str, details: str = ""):
    """Quick API call logging"""
    logger = get_logger('api_calls')
    logger.api_call(api_name, endpoint, status, details)

def log_progress(current: int, total: int, item: str = ""):
    """Quick progress logging"""
    logger = get_logger('progress')
    logger.progress(current, total, item)

def log_error(message: str, logger_name: str = 'general'):
    """Quick error logging"""
    logger = get_logger(logger_name)
    logger.error(message)

def log_info(message: str, logger_name: str = 'general'):
    """Quick info logging"""
    logger = get_logger(logger_name)
    logger.info(message)

# Example usage and testing
if __name__ == "__main__":
    # Test the logging system
    logger = get_logger('test_logger')
    
    logger.section_start("Testing Logging System")
    
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.debug("This is a debug message (only in file)")
    
    logger.api_call("Celestrak", "/gp.php?GROUP=active", "Success", "(11,790 satellites)")
    logger.api_call("N2YO", "/satellite/25544", "Failed", "404 Not Found")
    
    for i in range(1, 6):
        logger.progress(i, 5, f"Processing satellite {i}")
    
    logger.summary("Test Results", {
        "Total Tests": 5,
        "Passed": 4,
        "Failed": 1,
        "Success Rate": "80%"
    })
    
    logger.section_end("Testing Logging System", success=True)
    
    print(f"\n\033[36m📁 Check the 'logs' directory for detailed log files!\033[0m") 