#!/usr/bin/env python3
"""
Sannetic Explorer - Configuration Manager
Centralized configuration loading and validation from .env files
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union
import logging

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")
    load_dotenv = None

class ConfigManager:
    """Centralized configuration manager for Sannetic Explorer"""
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration manager"""
        self.project_root = Path(__file__).parent.parent
        self.env_file = env_file or self.project_root / ".env"
        self.config = {}
        self.logger = self._setup_logger()
        
        # Load environment variables
        self._load_env_file()
        self._load_config()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup basic logger"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _load_env_file(self):
        """Load environment variables from .env file"""
        if load_dotenv and self.env_file.exists():
            load_dotenv(self.env_file)
            self.logger.info(f"Loaded environment variables from {self.env_file}")
        elif self.env_file.exists():
            # Manual .env loading if python-dotenv is not available
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            self.logger.info(f"Manually loaded environment variables from {self.env_file}")
        else:
            self.logger.warning(f"No .env file found at {self.env_file}")
    
    def _load_config(self):
        """Load all configuration values"""
        self.config = {
            # AI System Configuration
            'ai': {
                'openai_api_key': self.get_env('OPENAI_API_KEY'),
                'openai_model': self.get_env('OPENAI_MODEL', 'gpt-4o-mini'),
                'openai_max_tokens': self.get_env_int('OPENAI_MAX_TOKENS', 2000),
                'openai_temperature': self.get_env_float('OPENAI_TEMPERATURE', 0.3),
                'enable_error_analysis': self.get_env_bool('AI_ENABLE_ERROR_ANALYSIS', True),
                'enable_orbital_calculations': self.get_env_bool('AI_ENABLE_ORBITAL_CALCULATIONS', True),
                'enable_optimization': self.get_env_bool('AI_ENABLE_OPTIMIZATION', True),
                'confidence_threshold': self.get_env_float('AI_CONFIDENCE_THRESHOLD', 0.7),
                'max_retries': self.get_env_int('AI_MAX_RETRIES', 3),
                'daily_cost_limit': self.get_env_float('AI_DAILY_COST_LIMIT', 5.00),
                'monthly_cost_limit': self.get_env_float('AI_MONTHLY_COST_LIMIT', 50.00),
                'cost_tracking': self.get_env_bool('AI_COST_TRACKING', True),
            },
            
            # Satellite Tracking APIs
            'apis': {
                'n2yo_api_key': self.get_env('N2YO_API_KEY'),
                'n2yo_base_url': self.get_env('N2YO_BASE_URL', 'https://api.n2yo.com/rest/v1/satellite'),
                'space_track_username': self.get_env('SPACE_TRACK_USERNAME'),
                'space_track_password': self.get_env('SPACE_TRACK_PASSWORD'),
                'space_track_base_url': self.get_env('SPACE_TRACK_BASE_URL', 'https://www.space-track.org'),
                'timeout_seconds': self.get_env_int('API_TIMEOUT_SECONDS', 30),
                'max_retries': self.get_env_int('API_MAX_RETRIES', 3),
                'verify_ssl': self.get_env_bool('API_VERIFY_SSL', True),
            },
            
            # System Configuration
            'system': {
                'log_level': self.get_env('LOG_LEVEL', 'INFO'),
                'log_format': self.get_env('LOG_FORMAT', '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(message)s'),
                'log_max_files': self.get_env_int('LOG_MAX_FILES', 10),
                'update_batch_size': self.get_env_int('UPDATE_BATCH_SIZE', 5),
                'update_delay_seconds': self.get_env_int('UPDATE_DELAY_SECONDS', 2),
                'api_rate_limit_delay': self.get_env_int('API_RATE_LIMIT_DELAY', 1),
            },
            
            # Dashboard Configuration
            'dashboard': {
                'port': self.get_env_int('DASHBOARD_PORT', 8080),
                'host': self.get_env('DASHBOARD_HOST', '0.0.0.0'),
                'auto_refresh': self.get_env_int('DASHBOARD_AUTO_REFRESH', 30),
                'secret_key': self.get_env('DASHBOARD_SECRET_KEY', 'sannetic_explorer_default_key'),
                'session_timeout': self.get_env_int('DASHBOARD_SESSION_TIMEOUT', 3600),
            },
            
            # Data Quality Thresholds
            'data_quality': {
                'excellent_threshold': self.get_env_int('DATA_QUALITY_EXCELLENT_THRESHOLD', 100),
                'good_threshold': self.get_env_int('DATA_QUALITY_GOOD_THRESHOLD', 50),
                'fair_threshold': self.get_env_int('DATA_QUALITY_FAIR_THRESHOLD', 10),
            },
            
            # Development Settings
            'development': {
                'debug_mode': self.get_env_bool('DEBUG_MODE', False),
                'verbose_logging': self.get_env_bool('VERBOSE_LOGGING', False),
                'development_mode': self.get_env_bool('DEVELOPMENT_MODE', False),
                'test_mode': self.get_env_bool('TEST_MODE', False),
                'mock_api_responses': self.get_env_bool('MOCK_API_RESPONSES', False),
            },
            
            # Cache Configuration
            'cache': {
                'enabled': self.get_env_bool('CACHE_ENABLED', True),
                'ttl_seconds': self.get_env_int('CACHE_TTL_SECONDS', 1800),
                'max_size': self.get_env_int('CACHE_MAX_SIZE', 100),
            }
        }
    
    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable as string"""
        return os.getenv(key, default)
    
    def get_env_int(self, key: str, default: int = 0) -> int:
        """Get environment variable as integer"""
        try:
            value = os.getenv(key)
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid integer value for {key}, using default: {default}")
            return default
    
    def get_env_float(self, key: str, default: float = 0.0) -> float:
        """Get environment variable as float"""
        try:
            value = os.getenv(key)
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid float value for {key}, using default: {default}")
            return default
    
    def get_env_bool(self, key: str, default: bool = False) -> bool:
        """Get environment variable as boolean"""
        value = os.getenv(key, '').lower()
        if value in ('true', '1', 'yes', 'on'):
            return True
        elif value in ('false', '0', 'no', 'off'):
            return False
        else:
            return default
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value by section and key"""
        try:
            return self.config.get(section, {}).get(key, default)
        except Exception as e:
            self.logger.error(f"Error getting config {section}.{key}: {e}")
            return default
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.config.get(section, {})
    
    def is_api_configured(self, api_name: str) -> bool:
        """Check if specific API is configured"""
        apis = self.get_section('apis')
        
        if api_name.lower() == 'openai':
            return bool(self.get('ai', 'openai_api_key'))
        elif api_name.lower() == 'n2yo':
            return bool(apis.get('n2yo_api_key'))
        elif api_name.lower() == 'space_track':
            return bool(apis.get('space_track_username')) and bool(apis.get('space_track_password'))
        else:
            return False
    
    def get_configured_apis(self) -> Dict[str, bool]:
        """Get status of all API configurations"""
        return {
            'openai': self.is_api_configured('openai'),
            'n2yo': self.is_api_configured('n2yo'),
            'space_track': self.is_api_configured('space_track'),
        }
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return status"""
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'api_status': self.get_configured_apis()
        }
        
        # Check critical configurations
        if not self.get('ai', 'openai_api_key'):
            validation_results['warnings'].append("OpenAI API key not configured - AI features will be limited")
        
        if not self.get('apis', 'n2yo_api_key'):
            validation_results['warnings'].append("N2YO API key not configured - real-time tracking unavailable")
        
        if not self.get('apis', 'space_track_username') or not self.get('apis', 'space_track_password'):
            validation_results['warnings'].append("Space-Track credentials not configured - TLE data unavailable")
        
        # Check for invalid values
        if self.get('dashboard', 'port') < 1 or self.get('dashboard', 'port') > 65535:
            validation_results['errors'].append("Invalid dashboard port number")
            validation_results['valid'] = False
        
        if self.get('ai', 'openai_temperature') < 0 or self.get('ai', 'openai_temperature') > 2:
            validation_results['warnings'].append("OpenAI temperature should be between 0 and 2")
        
        return validation_results
    
    def print_status(self):
        """Print configuration status"""
        print("\n" + "="*60)
        print("🔧 SANNETIC EXPLORER CONFIGURATION STATUS")
        print("="*60)
        
        # API Status
        print("\n📡 API Configuration:")
        apis = self.get_configured_apis()
        for api, configured in apis.items():
            status = "✅ Configured" if configured else "❌ Not configured"
            print(f"  {api.upper()}: {status}")
        
        # System Settings
        print(f"\n🖥️  Dashboard: http://{self.get('dashboard', 'host')}:{self.get('dashboard', 'port')}")
        print(f"📊 Auto-refresh: {self.get('dashboard', 'auto_refresh')}s")
        print(f"📝 Log level: {self.get('system', 'log_level')}")
        
        # AI Settings
        if self.is_api_configured('openai'):
            print(f"\n🤖 AI Model: {self.get('ai', 'openai_model')}")
            print(f"🧠 Max tokens: {self.get('ai', 'openai_max_tokens')}")
            print(f"🌡️  Temperature: {self.get('ai', 'openai_temperature')}")
            print(f"💰 Daily limit: ${self.get('ai', 'daily_cost_limit')}")
        
        # Validation
        validation = self.validate_config()
        if validation['warnings']:
            print(f"\n⚠️  Warnings:")
            for warning in validation['warnings']:
                print(f"  - {warning}")
        
        if validation['errors']:
            print(f"\n❌ Errors:")
            for error in validation['errors']:
                print(f"  - {error}")
        
        print("\n" + "="*60)

# Global configuration instance
config = ConfigManager()

def get_config() -> ConfigManager:
    """Get global configuration instance"""
    return config

def main():
    """Main function for testing configuration"""
    config_manager = ConfigManager()
    config_manager.print_status()
    
    # Validation test
    validation = config_manager.validate_config()
    print(f"\nConfiguration valid: {validation['valid']}")

if __name__ == "__main__":
    main() 