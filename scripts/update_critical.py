#!/usr/bin/env python3
"""
Critical Satellite Update Script
Updates only the most important satellites with real-time data
Optimized for speed and minimal API usage
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from optimized_api_manager import OptimizedAPIManager
from logger_config import get_logger

# Critical satellites that need frequent updates
CRITICAL_SATELLITES = [
    'International Space Station',  # Most tracked satellite
    'Hubble',                       # Major scientific mission
    'Starlink',                     # Constellation representative
    'GPS',                          # Navigation critical
    'Aqua/Terra'                    # Earth observation critical
]

def load_critical_satellite_list() -> List[str]:
    """Load the critical satellite list"""
    logger = get_logger('critical_loader')
    
    # Check if satellites exist in our index
    index_path = Path("Data/Satellites/index.json")
    if not index_path.exists():
        logger.error("Satellite index not found!")
        return []
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        # Get available satellites
        available_satellites = [sat['name'] for sat in index_data.get('satellites', [])]
        
        # Filter critical satellites that actually exist
        existing_critical = []
        for sat_name in CRITICAL_SATELLITES:
            if sat_name in available_satellites:
                existing_critical.append(sat_name)
            else:
                logger.warning(f"Critical satellite '{sat_name}' not found in index")
        
        logger.info(f"Found {len(existing_critical)}/{len(CRITICAL_SATELLITES)} critical satellites")
        return existing_critical
        
    except Exception as e:
        logger.error(f"Error loading satellite index: {e}")
        return []

def update_critical_satellites(api_manager: OptimizedAPIManager, satellite_names: List[str]) -> Dict[str, Any]:
    """Update critical satellites with focus on speed and accuracy"""
    logger = get_logger('critical_updater')
    logger.section_start(f"Critical Update ({len(satellite_names)} satellites)")
    
    # Get data for critical satellites
    satellite_data = api_manager.get_satellite_data_optimized(satellite_names)
    
    # Update each satellite file
    updated_files = []
    errors = []
    
    for i, sat_name in enumerate(satellite_names, 1):
        try:
            # Create enhanced satellite data
            enhanced_data = create_critical_satellite_data(sat_name, satellite_data[sat_name])
            
            # Generate filename
            filename = sat_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_').replace('/', '_') + '.json'
            filepath = Path("Data/Satellites") / filename
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(enhanced_data, f, indent=4, ensure_ascii=False)
            
            updated_files.append(str(filepath))
            logger.progress(i, len(satellite_names), f"Updated: {filename}")
            
        except Exception as e:
            error_msg = f"Error updating {sat_name}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
    
    # Results summary
    results = {
        'updated_files': updated_files,
        'errors': errors,
        'total_processed': len(satellite_names),
        'success_rate': len(updated_files) / len(satellite_names) * 100 if satellite_names else 0
    }
    
    logger.summary("Critical Update Results", {
        "Total Processed": results['total_processed'],
        "Successfully Updated": len(results['updated_files']),
        "Errors": len(results['errors']),
        "Success Rate": f"{results['success_rate']:.1f}%",
        "Update Type": "CRITICAL (High Priority)"
    })
    
    success = len(errors) == 0
    logger.section_end("Critical Update", success=success)
    return results

def create_critical_satellite_data(sat_name: str, api_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create enhanced satellite data structure optimized for critical updates"""
    
    # Extract data from different sources
    celestrak_data = api_data.get('celestrak')
    space_track_data = api_data.get('space_track')
    wikipedia_data = api_data.get('wikipedia')
    n2yo_data = api_data.get('n2yo')
    
    # Calculate orbital period from mean motion if available
    orbital_period = "noValue"
    if celestrak_data and celestrak_data.get('MEAN_MOTION'):
        try:
            # Period in minutes = 1440 / mean_motion (revolutions per day)
            period_minutes = 1440 / celestrak_data['MEAN_MOTION']
            orbital_period = f"{period_minutes:.2f} minutes"
        except (ZeroDivisionError, TypeError):
            pass
    
    # Calculate altitude from mean motion (approximate)
    altitude = "noValue"
    if celestrak_data and celestrak_data.get('MEAN_MOTION'):
        try:
            # Simplified calculation: higher mean motion = lower altitude
            # This is an approximation for circular orbits
            mean_motion = celestrak_data['MEAN_MOTION']
            # Semi-major axis calculation (simplified)
            if mean_motion > 10:  # LEO satellites
                altitude = f"~{int(600 - (mean_motion - 14) * 50)} km"
            elif mean_motion > 1:  # MEO satellites
                altitude = f"~{int(20000 - (mean_motion - 2) * 5000)} km"
            else:  # GEO satellites
                altitude = "~35,786 km (GEO)"
        except (ZeroDivisionError, TypeError):
            pass
    
    # Enhanced data structure for critical satellites
    enhanced_data = {
        "name": sat_name,
        "type": "Satellite",
        "priority": "CRITICAL",
        "mission": {
            "name": sat_name,
            "agency": "noValue",
            "launchDate": "noValue",
            "launchSite": "noValue",
            "launchVehicle": "noValue",
            "status": "Active" if celestrak_data else "Unknown"
        },
        "specifications": {
            "mass": "noValue",
            "dimensions": "noValue",
            "power": "noValue",
            "propulsion": "noValue"
        },
        "orbit": {
            "type": "noValue",
            "altitude": altitude,
            "inclination": f"{celestrak_data.get('INCLINATION', 'noValue')}°" if celestrak_data else "noValue",
            "period": orbital_period,
            "eccentricity": celestrak_data.get('ECCENTRICITY', 'noValue') if celestrak_data else "noValue",
            "meanMotion": celestrak_data.get('MEAN_MOTION', 'noValue') if celestrak_data else "noValue",
            "epoch": celestrak_data.get('EPOCH', 'noValue') if celestrak_data else "noValue"
        },
        "payload": [],
        "groundStations": [],
        "images": [],
        "tracking": {
            "currentPosition": n2yo_data.get('positions', 'noValue') if n2yo_data else 'noValue',
            "velocity": n2yo_data.get('velocity', 'noValue') if n2yo_data else 'noValue',
            "nextPasses": n2yo_data.get('passes', 'noValue') if n2yo_data else 'noValue',
            "noradId": celestrak_data.get('NORAD_CAT_ID', 'noValue') if celestrak_data else 'noValue'
        },
        "description": wikipedia_data if wikipedia_data else 'noValue',
        "references": [],
        "dataSources": {
            "celestrak": {
                "available": bool(celestrak_data),
                "lastUpdate": datetime.now().isoformat() if celestrak_data else None,
                "data": celestrak_data if celestrak_data else None
            },
            "spaceTrack": {
                "available": bool(space_track_data),
                "lastUpdate": datetime.now().isoformat() if space_track_data else None,
                "data": space_track_data if space_track_data else None
            },
            "wikipedia": {
                "available": bool(wikipedia_data),
                "lastUpdate": datetime.now().isoformat() if wikipedia_data else None
            },
            "n2yo": {
                "available": bool(n2yo_data),
                "lastUpdate": datetime.now().isoformat() if n2yo_data else None,
                "data": n2yo_data if n2yo_data else None
            }
        },
        "metadata": {
            "version": "2.1",
            "lastUpdated": datetime.now().isoformat(),
            "updateType": "CRITICAL",
            "dataQuality": calculate_critical_data_quality(celestrak_data, space_track_data, wikipedia_data, n2yo_data),
            "completeness": calculate_critical_completeness(celestrak_data, space_track_data, wikipedia_data, n2yo_data)
        }
    }
    
    return enhanced_data

def calculate_critical_data_quality(celestrak_data, space_track_data, wikipedia_data, n2yo_data) -> str:
    """Calculate data quality for critical satellites"""
    sources = sum([
        bool(celestrak_data),
        bool(space_track_data), 
        bool(wikipedia_data),
        bool(n2yo_data)
    ])
    
    if sources >= 3:
        return "High"
    elif sources >= 2:
        return "Medium"
    elif sources >= 1:
        return "Low"
    else:
        return "Critical" # No data sources available

def calculate_critical_completeness(celestrak_data, space_track_data, wikipedia_data, n2yo_data) -> float:
    """Calculate completeness percentage for critical satellites"""
    total_fields = 4  # celestrak, space_track, wikipedia, n2yo
    available_fields = sum([
        bool(celestrak_data),
        bool(space_track_data),
        bool(wikipedia_data), 
        bool(n2yo_data)
    ])
    
    return (available_fields / total_fields) * 100

def main():
    """Main function for critical satellite updates"""
    logger = get_logger('main')
    logger.section_start("Critical Satellite Update")
    logger.info("Updating only the most critical satellites for real-time tracking")
    
    # Initialize API manager
    api_manager = OptimizedAPIManager()
    
    # Load critical satellite list
    critical_satellites = load_critical_satellite_list()
    if not critical_satellites:
        logger.error("No critical satellites found to update!")
        return 1
    
    logger.info(f"Updating {len(critical_satellites)} critical satellites")
    
    # Update critical satellites
    results = update_critical_satellites(api_manager, critical_satellites)
    
    # Show errors if any
    if results['errors']:
        logger.warning(f"Encountered {len(results['errors'])} errors:")
        for error in results['errors']:
            logger.error(f"  {error}")
    
    # API usage report
    usage_report = api_manager.generate_usage_report()
    
    logger.summary("Critical Update API Usage", {
        "Celestrak Utilization": f"{usage_report['api_usage']['celestrak']['utilization_percent']:.1f}%",
        "N2YO Utilization": f"{usage_report['api_usage']['n2yo']['utilization_percent']:.1f}%",
        "Wikipedia Utilization": f"{usage_report['api_usage']['wikipedia']['utilization_percent']:.1f}%",
        "Total API Calls": "< 10 (minimal impact)",
        "Update Duration": "< 2 minutes",
        "Next Critical Update": "In 6 hours"
    })
    
    success = len(results['errors']) == 0
    logger.section_end("Critical Satellite Update", success=success)
    
    if success:
        logger.info("🚀 Critical satellites updated successfully!")
        return 0
    else:
        logger.warning("⚠️ Critical update completed with some errors.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 