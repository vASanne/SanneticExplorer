#!/usr/bin/env python3
"""
Optimized Data Update Script for Sannetic Explorer
Uses batch processing and intelligent caching to minimize API calls
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from optimized_api_manager import OptimizedAPIManager
from logger_config import get_logger

def load_satellite_list() -> List[str]:
    """Load the list of satellites from index.json"""
    index_path = Path("Data/Satellites/index.json")
    if not index_path.exists():
        print("Warning: Satellites index.json not found!")
        return []
    
    with open(index_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return [sat.get('name', '') for sat in data.get('satellites', [])]

def update_satellite_files_optimized(api_manager: OptimizedAPIManager, satellite_names: List[str]) -> Dict[str, Any]:
    """Update satellite files using optimized API calls"""
    logger = get_logger('file_updater')
    logger.section_start(f"Updating {len(satellite_names)} Satellite Files")
    
    # Get data for all satellites using batch processing
    satellite_data = api_manager.get_satellite_data_optimized(satellite_names)
    
    # Update each satellite file
    updated_files = []
    errors = []
    
    for i, sat_name in enumerate(satellite_names, 1):
        try:
            # Create filename from satellite name
            filename = sat_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
            filename = f"{filename}.json"
            filepath = Path("Data/Satellites") / filename
            
            # Get the data for this satellite
            sat_data = satellite_data.get(sat_name, {})
            
            # Create enhanced satellite data structure
            enhanced_data = create_enhanced_satellite_data(sat_name, sat_data)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(enhanced_data, f, indent=4, ensure_ascii=False)
            
            updated_files.append(str(filepath))
            logger.progress(i, len(satellite_names), f"Updated: {filename}")
            
        except Exception as e:
            error_msg = f"Error updating {sat_name}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
    
    results = {
        'updated_files': updated_files,
        'errors': errors,
        'total_processed': len(satellite_names),
        'success_rate': len(updated_files) / len(satellite_names) * 100 if satellite_names else 0
    }
    
    logger.summary("File Update Results", {
        "Total Processed": results['total_processed'],
        "Successfully Updated": len(results['updated_files']),
        "Errors": len(results['errors']),
        "Success Rate": f"{results['success_rate']:.1f}%"
    })
    
    logger.section_end("Updating Satellite Files", success=len(errors) == 0)
    return results

def create_enhanced_satellite_data(sat_name: str, api_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create enhanced satellite data structure from API responses"""
    
    # Extract data from different sources
    celestrak_data = api_data.get('celestrak', {})
    space_track_data = api_data.get('space_track', {})
    wikipedia_data = api_data.get('wikipedia', '')
    n2yo_data = api_data.get('n2yo', {})
    
    # Create the enhanced data structure
    enhanced_data = {
        "name": sat_name,
        "type": "Satellite",
        "identification": {
            "noradCatalogId": celestrak_data.get('NORAD_CAT_ID', 'noValue'),
            "internationalDesignator": celestrak_data.get('INTLDES', 'noValue'),
            "objectName": celestrak_data.get('OBJECT_NAME', sat_name),
            "objectType": celestrak_data.get('OBJECT_TYPE', 'noValue')
        },
        "mission": {
            "name": extract_mission_name(sat_name, celestrak_data),
            "agency": extract_agency(sat_name, celestrak_data),
            "launchDate": celestrak_data.get('EPOCH', 'noValue'),
            "status": "Active" if celestrak_data else "Unknown"
        },
        "orbital": {
            "epoch": celestrak_data.get('EPOCH', 'noValue'),
            "meanMotion": celestrak_data.get('MEAN_MOTION', 'noValue'),
            "eccentricity": celestrak_data.get('ECCENTRICITY', 'noValue'),
            "inclination": celestrak_data.get('INCLINATION', 'noValue'),
            "argumentOfPerigee": celestrak_data.get('ARG_OF_PERICENTER', 'noValue'),
            "rightAscension": celestrak_data.get('RA_OF_ASC_NODE', 'noValue'),
            "meanAnomaly": celestrak_data.get('MEAN_ANOMALY', 'noValue'),
            "bstarDrag": celestrak_data.get('BSTAR', 'noValue'),
            "tle": {
                "line1": celestrak_data.get('TLE_LINE1', 'noValue'),
                "line2": celestrak_data.get('TLE_LINE2', 'noValue')
            }
        },
        "tracking": {
            "currentPosition": n2yo_data.get('positions', 'noValue') if n2yo_data else 'noValue',
            "velocity": n2yo_data.get('velocity', 'noValue') if n2yo_data else 'noValue',
            "nextPasses": n2yo_data.get('passes', 'noValue') if n2yo_data else 'noValue'
        },
        "description": wikipedia_data if wikipedia_data else 'noValue',
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
            "version": "2.0",
            "lastUpdated": datetime.now().isoformat(),
            "dataQuality": calculate_data_quality(celestrak_data, space_track_data, wikipedia_data, n2yo_data),
            "completeness": calculate_completeness(celestrak_data, space_track_data, wikipedia_data, n2yo_data)
        }
    }
    
    return enhanced_data

def extract_mission_name(sat_name: str, celestrak_data: Dict[str, Any]) -> str:
    """Extract mission name from satellite data"""
    if 'STARLINK' in sat_name.upper():
        return 'Starlink'
    elif 'ISS' in sat_name.upper() or 'ZARYA' in sat_name.upper():
        return 'International Space Station'
    elif 'HUBBLE' in sat_name.upper():
        return 'Hubble Space Telescope'
    elif 'GPS' in sat_name.upper():
        return 'Global Positioning System'
    elif 'NOAA' in sat_name.upper():
        return 'National Oceanic and Atmospheric Administration'
    elif celestrak_data.get('OBJECT_NAME'):
        return celestrak_data['OBJECT_NAME']
    else:
        return sat_name

def extract_agency(sat_name: str, celestrak_data: Dict[str, Any]) -> str:
    """Extract agency from satellite data"""
    name_upper = sat_name.upper()
    
    if 'STARLINK' in name_upper:
        return 'SpaceX'
    elif 'ISS' in name_upper or 'ZARYA' in name_upper:
        return 'NASA/Roscosmos/ESA/JAXA/CSA'
    elif 'HUBBLE' in name_upper:
        return 'NASA/ESA'
    elif 'GPS' in name_upper:
        return 'US Air Force'
    elif 'NOAA' in name_upper:
        return 'NOAA'
    elif 'TERRA' in name_upper or 'AQUA' in name_upper:
        return 'NASA'
    else:
        return 'Unknown'

def calculate_data_quality(celestrak_data: Dict[str, Any], space_track_data: Dict[str, Any], 
                          wikipedia_data: str, n2yo_data: Dict[str, Any]) -> str:
    """Calculate overall data quality score"""
    sources_available = sum([
        bool(celestrak_data),
        bool(space_track_data), 
        bool(wikipedia_data),
        bool(n2yo_data)
    ])
    
    if sources_available >= 3:
        return "High"
    elif sources_available >= 2:
        return "Medium"
    elif sources_available >= 1:
        return "Low"
    else:
        return "None"

def calculate_completeness(celestrak_data: Dict[str, Any], space_track_data: Dict[str, Any],
                          wikipedia_data: str, n2yo_data: Dict[str, Any]) -> float:
    """Calculate data completeness percentage"""
    total_fields = 20  # Expected number of important fields
    filled_fields = 0
    
    # Check Celestrak data completeness
    if celestrak_data:
        celestrak_fields = ['NORAD_CAT_ID', 'OBJECT_NAME', 'EPOCH', 'MEAN_MOTION', 
                           'ECCENTRICITY', 'INCLINATION', 'ARG_OF_PERICENTER', 
                           'RA_OF_ASC_NODE', 'MEAN_ANOMALY']
        filled_fields += sum(1 for field in celestrak_fields if celestrak_data.get(field))
    
    # Check other sources
    if space_track_data:
        filled_fields += 3
    if wikipedia_data:
        filled_fields += 2
    if n2yo_data:
        filled_fields += 3
    
    return round((filled_fields / total_fields) * 100, 1)

def prioritize_satellites(satellite_names: List[str]) -> List[str]:
    """Prioritize satellites based on importance/popularity"""
    priority_keywords = [
        'ISS', 'ZARYA', 'HUBBLE', 'STARLINK', 'GPS', 'NOAA', 
        'TERRA', 'AQUA', 'LANDSAT', 'GOES', 'SENTINEL'
    ]
    
    priority_satellites = []
    regular_satellites = []
    
    for sat_name in satellite_names:
        name_upper = sat_name.upper()
        if any(keyword in name_upper for keyword in priority_keywords):
            priority_satellites.append(sat_name)
        else:
            regular_satellites.append(sat_name)
    
    # Return priority satellites first, then regular ones
    return priority_satellites + regular_satellites

def main():
    """Main function to run optimized data updates"""
    logger = get_logger('main')
    logger.section_start("Sannetic Explorer Optimized Data Update")
    logger.info("Using intelligent batch processing to minimize API calls")
    
    # Initialize the optimized API manager
    api_manager = OptimizedAPIManager()
    
    # Load satellite list
    satellite_names = load_satellite_list()
    if not satellite_names:
        logger.error("No satellites found to update!")
        return
    
    logger.info(f"Found {len(satellite_names)} satellites in index")
    logger.info("Prioritizing satellites for optimal API usage...")
    
    # Prioritize satellites (put most important ones first)
    priority_satellites = prioritize_satellites(satellite_names)
    
    # Limit to reasonable number to avoid API bans
    max_satellites = min(20, len(priority_satellites))  # Process max 20 satellites to be safe
    satellites_to_process = priority_satellites[:max_satellites]
    
    logger.info(f"Processing top {len(satellites_to_process)} priority satellites")
    
    # Update satellite files
    results = update_satellite_files_optimized(api_manager, satellites_to_process)
    
    # Show errors if any
    if results['errors']:
        logger.warning(f"Encountered {len(results['errors'])} errors:")
        for error in results['errors']:
            logger.error(f"  {error}")
    
    # API usage report
    usage_report = api_manager.generate_usage_report()
    
    logger.summary("Final API Usage Report", {
        "Cache Files Created": usage_report['cache_stats']['cached_files'],
        "Celestrak Utilization": f"{usage_report['api_usage']['celestrak']['utilization_percent']:.1f}%",
        "Wikipedia Utilization": f"{usage_report['api_usage']['wikipedia']['utilization_percent']:.1f}%",
        "Space-Track Utilization": f"{usage_report['api_usage']['space_track']['utilization_percent']:.1f}%",
        "N2YO Utilization": f"{usage_report['api_usage']['n2yo']['utilization_percent']:.1f}%",
        "Estimated API Savings": usage_report['optimization_summary']['total_api_calls_saved']
    })
    
    success = len(results['errors']) == 0
    logger.section_end("Sannetic Explorer Data Update", success=success)
    
    if success:
        logger.info("🎉 Data update completed successfully with minimal API impact!")
    else:
        logger.warning("⚠️ Data update completed with some errors. Check logs for details.")

if __name__ == "__main__":
    main() 