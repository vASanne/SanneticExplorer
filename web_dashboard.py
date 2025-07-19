#!/usr/bin/env python3
"""
Sannetic Explorer Web Dashboard
Real-time status page showing system health, errors, data status, and live logs
"""

import os
import sys
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template, jsonify, request
import threading
import time

# Add the scripts directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

# Import configuration manager
try:
    from scripts.config_manager import get_config
    config = get_config()
except ImportError:
    print("Warning: Configuration manager not available, using defaults")
    config = None

# Simple logging setup
import logging
log_level = config.get('system', 'log_level', 'INFO') if config else 'INFO'
log_format = config.get('system', 'log_format') if config else '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=getattr(logging, log_level), format=log_format)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class SystemMonitor:
    """Monitor system status and collect real-time data"""
    
    def __init__(self):
        self.last_update = datetime.now()
        self.status_cache = {}
        self.update_interval = config.get('dashboard', 'auto_refresh', 30) if config else 30
        
    def get_system_status(self):
        """Get comprehensive system status"""
        try:
            # Check if we need to update cache
            if (datetime.now() - self.last_update).seconds > self.update_interval:
                self.update_status_cache()
            
            return self.status_cache
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return self.get_fallback_status()
    
    def update_status_cache(self):
        """Update the status cache with fresh data"""
        try:
            self.status_cache = {
                'timestamp': datetime.now().isoformat(),
                'system_health': self.get_system_health(),
                'data_statistics': self.get_data_statistics(),
                'error_summary': self.get_error_summary(),
                'api_status': self.get_api_status(),
                'recent_activity': self.get_recent_activity(),
                'ai_status': self.get_ai_status(),
                'config_status': self.get_config_status()
            }
            self.last_update = datetime.now()
            logger.info("Status cache updated successfully")
        except Exception as e:
            logger.error(f"Error updating status cache: {e}")
            self.status_cache = self.get_fallback_status()
    
    def get_config_status(self):
        """Get configuration status"""
        try:
            if not config:
                return {'error': 'Configuration manager not available'}
            
            validation = config.validate_config()
            return {
                'valid': validation['valid'],
                'warnings_count': len(validation['warnings']),
                'errors_count': len(validation['errors']),
                'api_configured_count': sum(validation['api_status'].values()),
                'total_apis': len(validation['api_status']),
                'warnings': validation['warnings'][:3],  # Show first 3 warnings
                'errors': validation['errors'][:3],      # Show first 3 errors
                'last_check': datetime.now().strftime("%H:%M:%S")
            }
        except Exception as e:
            logger.error(f"Error getting config status: {e}")
            return {'error': str(e)}
    
    def get_system_health(self):
        """Get overall system health metrics"""
        try:
            # Check core directories
            data_dir = Path("Data")
            satellites_dir = data_dir / "Satellites"
            logs_dir = Path("logs")
            
            health = {
                'overall_status': 'healthy',
                'components': {
                    'data_directory': satellites_dir.exists(),
                    'logs_directory': logs_dir.exists(),
                    'scripts_directory': Path("scripts").exists(),
                    'config_files': Path("requirements.txt").exists(),
                    'env_config': config is not None and Path("env.example").exists()
                },
                'uptime': self.get_uptime(),
                'last_check': datetime.now().strftime("%H:%M:%S")
            }
            
            # Determine overall status
            if all(health['components'].values()):
                health['overall_status'] = 'healthy'
            elif any(health['components'].values()):
                health['overall_status'] = 'warning'
            else:
                health['overall_status'] = 'error'
            
            return health
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {'overall_status': 'error', 'error': str(e)}
    
    def get_data_statistics(self):
        """Get data statistics and object counts"""
        try:
            stats = {
                'satellites': 0,
                'planets': 0,
                'natural_satellites': 0,
                'spacecraft': 0,
                'stars': 0,
                'total_objects': 0,
                'last_updated': 'Unknown',
                'data_quality': 'Unknown'
            }
            
            # Count satellites
            satellites_dir = Path("Data/Satellites")
            if satellites_dir.exists():
                satellite_files = list(satellites_dir.glob("*.json"))
                stats['satellites'] = len([f for f in satellite_files if f.name != "index.json"])
                
                # Check index file for last update
                index_file = satellites_dir / "index.json"
                if index_file.exists():
                    try:
                        with open(index_file, 'r') as f:
                            index_data = json.load(f)
                            stats['last_updated'] = index_data.get('metadata', {}).get('last_updated', 'Unknown')
                            if 'satellites' in index_data:
                                stats['satellites'] = len(index_data['satellites'])
                    except:
                        pass
            
            # Count other object types
            for obj_type in ['Planets', 'NaturalSatellites', 'Spacecraft', 'Stars']:
                obj_dir = Path(f"Data/{obj_type}")
                if obj_dir.exists():
                    obj_files = list(obj_dir.glob("*.json"))
                    count = len([f for f in obj_files if f.name != "index.json"])
                    stats[obj_type.lower().replace('naturalsatellites', 'natural_satellites')] = count
            
            # Calculate total
            stats['total_objects'] = (stats['satellites'] + stats['planets'] + 
                                    stats['natural_satellites'] + stats['spacecraft'] + stats['stars'])
            
            # Estimate data quality using config thresholds
            if config:
                excellent_threshold = config.get('data_quality', 'excellent_threshold', 100)
                good_threshold = config.get('data_quality', 'good_threshold', 50)
                fair_threshold = config.get('data_quality', 'fair_threshold', 10)
            else:
                excellent_threshold, good_threshold, fair_threshold = 100, 50, 10
            
            if stats['total_objects'] >= excellent_threshold:
                stats['data_quality'] = 'Excellent'
            elif stats['total_objects'] >= good_threshold:
                stats['data_quality'] = 'Good'
            elif stats['total_objects'] >= fair_threshold:
                stats['data_quality'] = 'Fair'
            else:
                stats['data_quality'] = 'Poor'
            
            return stats
        except Exception as e:
            logger.error(f"Error getting data statistics: {e}")
            return {'error': str(e), 'total_objects': 0}
    
    def get_error_summary(self):
        """Get recent errors from log files"""
        try:
            errors = []
            logs_dir = Path("logs")
            
            if logs_dir.exists():
                # Get the most recent log files (last 3)
                log_files = sorted(logs_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)[:3]
                
                for log_file in log_files:
                    try:
                        with open(log_file, 'r') as f:
                            lines = f.readlines()
                            
                        # Look for ERROR lines in the last 100 lines
                        recent_lines = lines[-100:]
                        for line in recent_lines:
                            if 'ERROR' in line:
                                # Parse timestamp and error message
                                parts = line.strip().split(' | ')
                                if len(parts) >= 4:
                                    timestamp = parts[0]
                                    level = parts[1]
                                    component = parts[2]
                                    message = ' | '.join(parts[4:])
                                    
                                    errors.append({
                                        'timestamp': timestamp,
                                        'component': component,
                                        'message': message,
                                        'file': log_file.name
                                    })
                    except Exception as e:
                        logger.error(f"Error reading log file {log_file}: {e}")
            
            # Sort by timestamp (most recent first) and limit to 10
            errors = sorted(errors, key=lambda x: x['timestamp'], reverse=True)[:10]
            
            return {
                'count': len(errors),
                'recent_errors': errors,
                'last_check': datetime.now().strftime("%H:%M:%S")
            }
        except Exception as e:
            logger.error(f"Error getting error summary: {e}")
            return {'count': 0, 'recent_errors': [], 'error': str(e)}
    
    def get_api_status(self):
        """Get API status and credentials"""
        try:
            if config:
                # Use configuration manager
                api_status = config.get_configured_apis()
                status = {
                    'openai': api_status.get('openai', False),
                    'n2yo': api_status.get('n2yo', False),
                    'space_track': api_status.get('space_track', False),
                    'last_check': datetime.now().strftime("%H:%M:%S")
                }
            else:
                # Fallback to environment variables
                status = {
                    'openai': bool(os.getenv('OPENAI_API_KEY')),
                    'n2yo': bool(os.getenv('N2YO_API_KEY')),
                    'space_track': bool(os.getenv('SPACE_TRACK_USERNAME')) and bool(os.getenv('SPACE_TRACK_PASSWORD')),
                    'last_check': datetime.now().strftime("%H:%M:%S")
                }
            
            # Count available APIs
            available_apis = sum([status['openai'], status['n2yo'], status['space_track']])
            status['available_count'] = available_apis
            status['total_count'] = 3
            
            return status
        except Exception as e:
            logger.error(f"Error getting API status: {e}")
            return {'error': str(e)}
    
    def get_recent_activity(self):
        """Get recent system activity"""
        try:
            activities = []
            logs_dir = Path("logs")
            
            if logs_dir.exists():
                # Get the most recent log file
                log_files = sorted(logs_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
                
                if log_files:
                    recent_log = log_files[0]
                    try:
                        with open(recent_log, 'r') as f:
                            lines = f.readlines()
                        
                        # Get last 20 lines for recent activity
                        recent_lines = lines[-20:]
                        for line in recent_lines:
                            if any(keyword in line for keyword in ['INFO', 'WARNING', 'ERROR']):
                                parts = line.strip().split(' | ')
                                if len(parts) >= 4:
                                    timestamp = parts[0]
                                    level = parts[1]
                                    component = parts[2]
                                    message = ' | '.join(parts[4:])
                                    
                                    activities.append({
                                        'timestamp': timestamp,
                                        'level': level,
                                        'component': component,
                                        'message': message[:100] + '...' if len(message) > 100 else message
                                    })
                    except Exception as e:
                        logger.error(f"Error reading recent log: {e}")
            
            return {
                'count': len(activities),
                'activities': activities[-10:],  # Last 10 activities
                'last_check': datetime.now().strftime("%H:%M:%S")
            }
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return {'count': 0, 'activities': [], 'error': str(e)}
    
    def get_ai_status(self):
        """Get AI system status"""
        try:
            if config:
                ai_enabled = config.is_api_configured('openai')
                ai_config = config.get_section('ai')
            else:
                ai_enabled = bool(os.getenv('OPENAI_API_KEY'))
                ai_config = {}
            
            ai_status = {
                'enabled': ai_enabled,
                'assistant_available': Path("scripts/ai_assistant.py").exists(),
                'enhanced_manager_available': Path("scripts/enhanced_delta_manager.py").exists(),
                'health_check_available': Path("scripts/ai_health_check.py").exists(),
                'config_manager_available': config is not None,
                'last_check': datetime.now().strftime("%H:%M:%S")
            }
            
            # Add AI configuration details if available
            if config and ai_enabled:
                ai_status['model'] = ai_config.get('openai_model', 'Unknown')
                ai_status['max_tokens'] = ai_config.get('openai_max_tokens', 0)
                ai_status['temperature'] = ai_config.get('openai_temperature', 0)
                ai_status['daily_limit'] = ai_config.get('daily_cost_limit', 0)
            
            # Count AI features
            available_features = sum([
                ai_status['assistant_available'],
                ai_status['enhanced_manager_available'], 
                ai_status['health_check_available'],
                ai_status['config_manager_available']
            ])
            ai_status['features_available'] = available_features
            ai_status['total_features'] = 4
            
            return ai_status
        except Exception as e:
            logger.error(f"Error getting AI status: {e}")
            return {'error': str(e)}
    
    def get_uptime(self):
        """Get system uptime (simplified)"""
        try:
            # Use the oldest log file as a proxy for uptime
            logs_dir = Path("logs")
            if logs_dir.exists():
                log_files = list(logs_dir.glob("*.log"))
                if log_files:
                    oldest_log = min(log_files, key=lambda x: x.stat().st_ctime)
                    uptime_seconds = time.time() - oldest_log.stat().st_ctime
                    
                    # Convert to human readable
                    days = int(uptime_seconds // 86400)
                    hours = int((uptime_seconds % 86400) // 3600)
                    minutes = int((uptime_seconds % 3600) // 60)
                    
                    if days > 0:
                        return f"{days}d {hours}h {minutes}m"
                    elif hours > 0:
                        return f"{hours}h {minutes}m"
                    else:
                        return f"{minutes}m"
            
            return "Unknown"
        except Exception as e:
            return "Unknown"
    
    def get_fallback_status(self):
        """Fallback status when main status collection fails"""
        return {
            'timestamp': datetime.now().isoformat(),
            'system_health': {'overall_status': 'unknown', 'error': 'Status collection failed'},
            'data_statistics': {'total_objects': 0, 'error': 'Data collection failed'},
            'error_summary': {'count': 0, 'recent_errors': []},
            'api_status': {'error': 'API status unavailable'},
            'recent_activity': {'count': 0, 'activities': []},
            'ai_status': {'error': 'AI status unavailable'},
            'config_status': {'error': 'Config status unavailable'}
        }
    
    def get_live_logs(self, lines=50):
        """Get live log output (terminal-like)"""
        try:
            logs_dir = Path("logs")
            if not logs_dir.exists():
                return ["No logs directory found"]
            
            # Get the most recent log file
            log_files = sorted(logs_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
            if not log_files:
                return ["No log files found"]
            
            recent_log = log_files[0]
            with open(recent_log, 'r') as f:
                all_lines = f.readlines()
            
            # Get last N lines
            recent_lines = all_lines[-lines:]
            
            # Format for terminal display
            formatted_lines = []
            for line in recent_lines:
                # Remove timestamp prefix for cleaner display
                clean_line = line.strip()
                if ' | ' in clean_line:
                    parts = clean_line.split(' | ')
                    if len(parts) >= 4:
                        timestamp = parts[0]
                        level = parts[1]
                        component = parts[2]
                        message = ' | '.join(parts[4:])
                        
                        # Color coding based on level
                        if 'ERROR' in level:
                            formatted_lines.append(f"<span class='log-error'>[{timestamp}] {component}: {message}</span>")
                        elif 'WARNING' in level:
                            formatted_lines.append(f"<span class='log-warning'>[{timestamp}] {component}: {message}</span>")
                        elif 'INFO' in level:
                            formatted_lines.append(f"<span class='log-info'>[{timestamp}] {component}: {message}</span>")
                        else:
                            formatted_lines.append(f"[{timestamp}] {component}: {message}")
                    else:
                        formatted_lines.append(clean_line)
                else:
                    formatted_lines.append(clean_line)
            
            return formatted_lines
        except Exception as e:
            logger.error(f"Error getting live logs: {e}")
            return [f"Error reading logs: {str(e)}"]

# Global monitor instance
monitor = SystemMonitor()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    status = monitor.get_system_status()
    return jsonify(status)

@app.route('/api/logs')
def api_logs():
    """API endpoint for live logs"""
    lines = request.args.get('lines', 50, type=int)
    logs = monitor.get_live_logs(lines)
    return jsonify({'logs': logs, 'timestamp': datetime.now().isoformat()})

@app.route('/api/refresh')
def api_refresh():
    """Force refresh of status cache"""
    monitor.update_status_cache()
    return jsonify({'status': 'refreshed', 'timestamp': datetime.now().isoformat()})

@app.route('/api/config')
def api_config():
    """API endpoint for configuration status"""
    if config:
        validation = config.validate_config()
        return jsonify({
            'config_available': True,
            'validation': validation,
            'api_status': config.get_configured_apis(),
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'config_available': False,
            'error': 'Configuration manager not available',
            'timestamp': datetime.now().isoformat()
        })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Get dashboard configuration
    dashboard_host = config.get('dashboard', 'host', '0.0.0.0') if config else '0.0.0.0'
    dashboard_port = config.get('dashboard', 'port', 8080) if config else 8080
    
    print("🌐 Starting Sannetic Explorer Web Dashboard...")
    print(f"📊 Dashboard will be available at: http://localhost:{dashboard_port}")
    print("🔄 Auto-refresh every 30 seconds")
    print("📱 Mobile-friendly responsive design")
    print("🌌 Animated starfield background")
    
    if config:
        print("✅ Configuration manager loaded")
        config.print_status()
    else:
        print("⚠️  Configuration manager not available - using defaults")
    
    # Start the Flask app
    app.run(host=dashboard_host, port=dashboard_port, debug=False) 