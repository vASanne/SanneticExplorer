#!/usr/bin/env python3
"""
AI Health Check for Sannetic Explorer
Comprehensive system health analysis with AI insights
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add the scripts directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from logger_config import get_logger

# Initialize logger
logger = get_logger(__name__)

def check_ai_availability():
    """Check if AI assistant is available"""
    try:
        import os
        return bool(os.getenv('OPENAI_API_KEY'))
    except Exception as e:
        logger.error(f"Error checking AI availability: {e}")
        return False

def check_system_components():
    """Check core system components"""
    components = {
        "logger": False,
        "orbital_propagator": False,
        "api_manager": False,
        "delta_manager": False,
        "ai_assistant": False
    }
    
    # Check logger
    try:
        logger.info("Testing logger component...")
        components["logger"] = True
    except Exception as e:
        print(f"Logger error: {e}")
    
    # Check orbital propagator
    try:
        from orbital_propagator import OrbitalPropagator
        propagator = OrbitalPropagator()
        components["orbital_propagator"] = True
        logger.info("✅ Orbital propagator available")
    except Exception as e:
        logger.error(f"Orbital propagator error: {e}")
    
    # Check API manager
    try:
        from optimized_api_manager import OptimizedAPIManager
        api_manager = OptimizedAPIManager()
        components["api_manager"] = True
        logger.info("✅ API manager available")
    except Exception as e:
        logger.error(f"API manager error: {e}")
    
    # Check delta manager
    try:
        from delta_update_manager import DeltaUpdateManager
        delta_manager = DeltaUpdateManager()
        components["delta_manager"] = True
        logger.info("✅ Delta manager available")
    except Exception as e:
        logger.error(f"Delta manager error: {e}")
    
    # Check AI assistant
    try:
        # Just check if the file exists and imports
        ai_file = Path(__file__).parent / "ai_assistant.py"
        if ai_file.exists():
            components["ai_assistant"] = True
            logger.info("✅ AI assistant available")
        else:
            logger.error("AI assistant file not found")
    except Exception as e:
        logger.error(f"AI assistant error: {e}")
    
    return components

def check_satellite_data():
    """Check satellite data availability"""
    satellites_dir = Path("Data/Satellites")
    index_file = satellites_dir / "index.json"
    
    data_status = {
        "satellites_dir_exists": satellites_dir.exists(),
        "index_file_exists": index_file.exists(),
        "total_satellites": 0,
        "sample_files_valid": 0,
        "sample_files_checked": 0
    }
    
    if index_file.exists():
        try:
            with open(index_file, 'r') as f:
                index_data = json.load(f)
                satellites = index_data.get('satellites', [])
                data_status["total_satellites"] = len(satellites)
                
                # Check sample of satellite files
                sample_size = min(5, len(satellites))
                for i, sat_info in enumerate(satellites[:sample_size]):
                    sat_name = sat_info['name']
                    filename = sat_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_').replace('/', '_') + '.json'
                    filepath = satellites_dir / filename
                    
                    data_status["sample_files_checked"] += 1
                    if filepath.exists():
                        try:
                            with open(filepath, 'r') as f:
                                sat_data = json.load(f)
                                if isinstance(sat_data, dict) and 'name' in sat_data:
                                    data_status["sample_files_valid"] += 1
                        except:
                            pass
                            
        except Exception as e:
            logger.error(f"Error reading index file: {e}")
    
    return data_status

def check_api_credentials():
    """Check API credentials availability"""
    credentials = {
        "openai_api_key": bool(os.getenv('OPENAI_API_KEY')),
        "n2yo_api_key": bool(os.getenv('N2YO_API_KEY')),
        "space_track_username": bool(os.getenv('SPACE_TRACK_USERNAME')),
        "space_track_password": bool(os.getenv('SPACE_TRACK_PASSWORD'))
    }
    
    return credentials

def generate_health_report():
    """Generate comprehensive health report"""
    logger.info("🔍 Starting AI System Health Check...")
    
    # Check AI availability
    ai_available = check_ai_availability()
    
    # Check system components
    components = check_system_components()
    
    # Check satellite data
    data_status = check_satellite_data()
    
    # Check API credentials
    credentials = check_api_credentials()
    
    # Calculate health scores
    component_score = (sum(components.values()) / len(components)) * 100
    data_score = 0
    if data_status["total_satellites"] > 0:
        data_score = (data_status["sample_files_valid"] / data_status["sample_files_checked"]) * 100
    
    credential_score = (sum(credentials.values()) / len(credentials)) * 100
    
    overall_score = (component_score + data_score + credential_score) / 3
    
    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "ai_available": ai_available,
        "overall_health_score": overall_score,
        "component_health": {
            "score": component_score,
            "details": components
        },
        "data_health": {
            "score": data_score,
            "details": data_status
        },
        "credentials_health": {
            "score": credential_score,
            "details": credentials
        },
        "recommendations": []
    }
    
    # Generate recommendations
    if not ai_available:
        report["recommendations"].append("🤖 Set OPENAI_API_KEY to enable full AI features")
    
    if component_score < 100:
        report["recommendations"].append("🔧 Some system components have issues - check error logs")
    
    if data_score < 80:
        report["recommendations"].append("📊 Satellite data quality is low - run data update")
    
    if not credentials["n2yo_api_key"]:
        report["recommendations"].append("🔑 Set N2YO_API_KEY for real-time satellite tracking")
    
    if not credentials["space_track_username"]:
        report["recommendations"].append("🔑 Set Space-Track credentials for TLE data access")
    
    if overall_score >= 90:
        report["recommendations"].append("✅ System health is excellent!")
    elif overall_score >= 70:
        report["recommendations"].append("⚡ System health is good with minor issues")
    else:
        report["recommendations"].append("⚠️ System health needs attention")
    
    return report

def print_health_report(report):
    """Print formatted health report"""
    logger.info("🤖 AI Health Check Complete")
    logger.info("=" * 60)
    
    # Overall status
    overall_score = report["overall_health_score"]
    if overall_score >= 90:
        status_emoji = "🟢"
    elif overall_score >= 70:
        status_emoji = "🟡"
    else:
        status_emoji = "🔴"
    
    logger.info(f"{status_emoji} Overall System Health: {overall_score:.1f}%")
    logger.info(f"🤖 AI Available: {'✅ Yes' if report['ai_available'] else '❌ No'}")
    logger.info("")
    
    # Component health
    logger.info("🔧 Component Health:")
    for component, status in report["component_health"]["details"].items():
        status_icon = "✅" if status else "❌"
        logger.info(f"   {status_icon} {component.replace('_', ' ').title()}")
    logger.info(f"   📊 Component Score: {report['component_health']['score']:.1f}%")
    logger.info("")
    
    # Data health
    logger.info("📊 Data Health:")
    data_details = report["data_health"]["details"]
    logger.info(f"   📁 Satellites Directory: {'✅' if data_details['satellites_dir_exists'] else '❌'}")
    logger.info(f"   📋 Index File: {'✅' if data_details['index_file_exists'] else '❌'}")
    logger.info(f"   🛰️ Total Satellites: {data_details['total_satellites']}")
    logger.info(f"   ✅ Valid Sample Files: {data_details['sample_files_valid']}/{data_details['sample_files_checked']}")
    logger.info(f"   📊 Data Score: {report['data_health']['score']:.1f}%")
    logger.info("")
    
    # Credentials health
    logger.info("🔑 API Credentials:")
    cred_details = report["credentials_health"]["details"]
    for cred, status in cred_details.items():
        status_icon = "✅" if status else "❌"
        cred_name = cred.replace('_', ' ').upper()
        logger.info(f"   {status_icon} {cred_name}")
    logger.info(f"   📊 Credentials Score: {report['credentials_health']['score']:.1f}%")
    logger.info("")
    
    # Recommendations
    logger.info("💡 Recommendations:")
    for rec in report["recommendations"]:
        logger.info(f"   {rec}")
    
    logger.info("=" * 60)

def main():
    """Main health check function"""
    try:
        report = generate_health_report()
        print_health_report(report)
        
        # Return appropriate exit code
        if report["overall_health_score"] >= 70:
            return 0
        else:
            return 1
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 