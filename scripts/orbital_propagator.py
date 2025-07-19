#!/usr/bin/env python3
"""
Orbital Propagation Engine for Sannetic Explorer
Calculates real-time satellite positions from TLE data without API calls
"""

import json
import ephem
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from math import degrees, radians, sqrt, pi, atan2, cos, sin
import logging

from logger_config import get_logger

# Initialize logger
logger = get_logger(__name__)

class OrbitalPropagator:
    """Advanced orbital propagation engine using TLE data"""
    
    def __init__(self):
        self.earth_radius = 6378.137  # Earth radius in km
        self.mu = 398600.4418  # Earth's gravitational parameter in km³/s²
        
    def parse_tle_epoch(self, epoch_str: str) -> datetime:
        """Parse TLE epoch string to datetime"""
        try:
            return datetime.fromisoformat(epoch_str.replace('Z', '+00:00'))
        except:
            # Fallback parsing for different formats
            return datetime.strptime(epoch_str[:19], '%Y-%m-%dT%H:%M:%S')
    
    def get_tle_age(self, tle_data: Dict[str, Any], reference_time: Optional[datetime] = None) -> float:
        """Calculate age of TLE data in days"""
        if reference_time is None:
            reference_time = datetime.utcnow()
        
        epoch = self.parse_tle_epoch(tle_data['EPOCH'])
        return (reference_time - epoch).total_seconds() / 86400.0
    
    def estimate_propagation_accuracy(self, tle_data: Dict[str, Any], age_days: float) -> str:
        """Estimate propagation accuracy based on TLE age and orbit type"""
        mean_motion = float(tle_data.get('MEAN_MOTION', 0))
        eccentricity = float(tle_data.get('ECCENTRICITY', 0))
        
        # Classify orbit type
        if mean_motion > 11:  # LEO
            if age_days < 1:
                return "excellent"
            elif age_days < 3:
                return "good"
            elif age_days < 7:
                return "fair"
            else:
                return "poor"
        elif mean_motion > 1.5:  # MEO
            if age_days < 7:
                return "excellent"
            elif age_days < 14:
                return "good"
            elif age_days < 30:
                return "fair"
            else:
                return "poor"
        else:  # GEO
            if age_days < 14:
                return "excellent"
            elif age_days < 30:
                return "good"
            elif age_days < 60:
                return "fair"
            else:
                return "poor"
    
    def get_max_recommended_age(self, tle_data: Dict[str, Any]) -> int:
        """Get maximum recommended TLE age in days"""
        mean_motion = float(tle_data.get('MEAN_MOTION', 0))
        
        if mean_motion > 11:  # LEO
            return 3
        elif mean_motion > 1.5:  # MEO
            return 14
        else:  # GEO
            return 30
    
    def create_satellite_object(self, tle_data: Dict[str, Any]) -> ephem.EarthSatellite:
        """Create ephem satellite object from TLE data"""
        name = tle_data.get('OBJECT_NAME', 'Unknown')
        
        # Handle both single TLE and array formats
        if isinstance(tle_data, list) and len(tle_data) > 0:
            tle_data = tle_data[0]  # Use first TLE if multiple
        
        # Try to construct TLE lines from data
        line1 = tle_data.get('line1', '')
        line2 = tle_data.get('line2', '')
        
        if not line1 or not line2:
            # Construct TLE lines from orbital elements
            line1 = self.construct_tle_line1(tle_data)
            line2 = self.construct_tle_line2(tle_data)
        
        return ephem.readtle(name, line1, line2)
    
    def construct_tle_line1(self, tle_data: Dict[str, Any]) -> str:
        """Construct TLE line 1 from orbital elements"""
        norad_id = str(tle_data.get('NORAD_CAT_ID', 99999)).zfill(5)
        classification = tle_data.get('CLASSIFICATION_TYPE', 'U')
        object_id = tle_data.get('OBJECT_ID', '99999A')
        
        # Convert epoch to TLE format
        epoch_str = tle_data.get('EPOCH', '')
        epoch_dt = self.parse_tle_epoch(epoch_str)
        year = epoch_dt.year % 100
        day_of_year = epoch_dt.timetuple().tm_yday
        fraction = (epoch_dt.hour * 3600 + epoch_dt.minute * 60 + epoch_dt.second) / 86400.0
        epoch_tle = f"{year:02d}{day_of_year:03d}.{fraction:.8f}"[:14]
        
        ndot = tle_data.get('MEAN_MOTION_DOT', 0)
        nddot = tle_data.get('MEAN_MOTION_DDOT', 0)
        bstar = tle_data.get('BSTAR', 0)
        element_set = tle_data.get('ELEMENT_SET_NO', 999)
        
        line1 = f"1 {norad_id}{classification} {object_id:8s} {epoch_tle} {ndot:10.8f} {nddot:8.0e} {bstar:8.0e} 0 {element_set:4d}"
        
        # Calculate checksum
        checksum = self.calculate_tle_checksum(line1)
        return line1 + str(checksum)
    
    def construct_tle_line2(self, tle_data: Dict[str, Any]) -> str:
        """Construct TLE line 2 from orbital elements"""
        norad_id = str(tle_data.get('NORAD_CAT_ID', 99999)).zfill(5)
        inclination = float(tle_data.get('INCLINATION', 0))
        raan = float(tle_data.get('RA_OF_ASC_NODE', 0))
        eccentricity = float(tle_data.get('ECCENTRICITY', 0))
        arg_perigee = float(tle_data.get('ARG_OF_PERICENTER', 0))
        mean_anomaly = float(tle_data.get('MEAN_ANOMALY', 0))
        mean_motion = float(tle_data.get('MEAN_MOTION', 0))
        rev_number = tle_data.get('REV_AT_EPOCH', 99999)
        
        # Format eccentricity (remove decimal point)
        ecc_str = f"{eccentricity:.7f}"[2:]  # Remove "0."
        
        line2 = f"2 {norad_id} {inclination:8.4f} {raan:8.4f} {ecc_str:7s} {arg_perigee:8.4f} {mean_anomaly:8.4f} {mean_motion:11.8f}{rev_number:5d}"
        
        # Calculate checksum
        checksum = self.calculate_tle_checksum(line2)
        return line2 + str(checksum)
    
    def calculate_tle_checksum(self, line: str) -> int:
        """Calculate TLE checksum"""
        checksum = 0
        for char in line:
            if char.isdigit():
                checksum += int(char)
            elif char == '-':
                checksum += 1
        return checksum % 10
    
    def propagate_position(self, tle_data: Dict[str, Any], target_time: datetime) -> Dict[str, Any]:
        """Calculate satellite position at target time"""
        try:
            # Handle nested data structure
            if isinstance(tle_data, dict) and 'data' in tle_data:
                tle_data = tle_data['data']
            
            # Handle array format
            if isinstance(tle_data, list) and len(tle_data) > 0:
                tle_data = tle_data[0]
            
            sat = self.create_satellite_object(tle_data)
            
            # Set observer time
            observer = ephem.Observer()
            observer.date = target_time
            
            # Compute satellite position
            sat.compute(observer)
            
            # Calculate additional orbital parameters
            altitude = sat.elevation / 1000.0  # Convert to km
            
            # Calculate velocity (approximate)
            dt = 10.0  # seconds
            sat.compute(ephem.Date(target_time + timedelta(seconds=dt)))
            lat2, lon2 = float(sat.sublat), float(sat.sublong)
            
            sat.compute(observer)  # Reset to target time
            lat1, lon1 = float(sat.sublat), float(sat.sublong)
            
            # Calculate ground speed
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            if abs(dlon) > pi:  # Handle longitude wrap-around
                dlon = dlon - 2*pi if dlon > 0 else dlon + 2*pi
            
            ground_speed = sqrt(dlat**2 + dlon**2) * self.earth_radius / dt  # km/s
            
            # Calculate orbital velocity
            mean_motion = float(tle_data.get('MEAN_MOTION', 0))
            if mean_motion > 0:
                period = 24 * 3600 / mean_motion  # seconds
                orbital_radius = altitude + self.earth_radius
                orbital_velocity = 2 * pi * orbital_radius / period  # km/s
            else:
                orbital_velocity = 0
            
            return {
                "position": {
                    "latitude": degrees(float(sat.sublat)),
                    "longitude": degrees(float(sat.sublong)),
                    "altitude": altitude
                },
                "velocity": {
                    "ground_speed": ground_speed,
                    "orbital_velocity": orbital_velocity,
                    "direction": degrees(atan2(dlon, dlat))
                },
                "orbital_elements": {
                    "range": float(sat.range) / 1000.0,  # km
                    "range_velocity": float(sat.range_velocity),  # km/s
                    "elevation_angle": degrees(float(sat.alt)),
                    "azimuth": degrees(float(sat.az))
                },
                "calculation_time": target_time.isoformat(),
                "tle_age_days": self.get_tle_age(tle_data, target_time)
            }
            
        except Exception as e:
            logger.error(f"Error propagating position: {e}")
            return {}
    
    def calculate_orbital_period(self, tle_data: Dict[str, Any]) -> float:
        """Calculate orbital period in minutes"""
        if isinstance(tle_data, list) and len(tle_data) > 0:
            tle_data = tle_data[0]
        
        mean_motion = float(tle_data.get('MEAN_MOTION', 0))
        if mean_motion > 0:
            return 1440.0 / mean_motion  # minutes
        return 0
    
    def predict_passes(self, tle_data: Dict[str, Any], observer_lat: float, 
                      observer_lon: float, days: int = 1) -> List[Dict[str, Any]]:
        """Predict satellite passes over observer location"""
        try:
            if isinstance(tle_data, list) and len(tle_data) > 0:
                tle_data = tle_data[0]
            
            sat = self.create_satellite_object(tle_data)
            
            observer = ephem.Observer()
            observer.lat = str(observer_lat)
            observer.lon = str(observer_lon)
            observer.elevation = 0  # Sea level
            observer.date = datetime.utcnow()
            
            passes = []
            
            for day in range(days):
                try:
                    next_pass = observer.next_pass(sat)
                    if next_pass:
                        rise_time, rise_az, max_alt_time, max_alt, set_time, set_az = next_pass
                        
                        passes.append({
                            "rise": {
                                "time": str(rise_time),
                                "azimuth": degrees(rise_az),
                                "elevation": 0
                            },
                            "culmination": {
                                "time": str(max_alt_time),
                                "elevation": degrees(max_alt),
                                "azimuth": degrees(rise_az + (set_az - rise_az) / 2)
                            },
                            "set": {
                                "time": str(set_time),
                                "azimuth": degrees(set_az),
                                "elevation": 0
                            },
                            "duration": (set_time - rise_time) * 86400,  # seconds
                            "max_elevation": degrees(max_alt)
                        })
                        
                        observer.date = set_time + ephem.minute  # Move past this pass
                except:
                    break  # No more passes
            
            return passes
            
        except Exception as e:
            logger.error(f"Error predicting passes: {e}")
            return []
    
    def is_tle_fresh(self, tle_data: Dict[str, Any], reference_time: Optional[datetime] = None) -> bool:
        """Check if TLE data is fresh enough for accurate propagation"""
        age_days = self.get_tle_age(tle_data, reference_time)
        max_age = self.get_max_recommended_age(tle_data)
        return age_days <= max_age
    
    def get_propagation_report(self, satellite_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive propagation report for satellite"""
        try:
            celestrak_source = satellite_data.get('dataSources', {}).get('celestrak')
            if not celestrak_source or celestrak_source == "noValue":
                return {"status": "no_tle_data", "can_propagate": False}
            
            # Extract actual TLE data
            if isinstance(celestrak_source, dict) and 'data' in celestrak_source:
                celestrak_data = celestrak_source['data']
            else:
                celestrak_data = celestrak_source
            
            if isinstance(celestrak_data, list):
                celestrak_data = celestrak_data[0]
            
            age_days = self.get_tle_age(celestrak_data)
            accuracy = self.estimate_propagation_accuracy(celestrak_data, age_days)
            is_fresh = self.is_tle_fresh(celestrak_data)
            max_age = self.get_max_recommended_age(celestrak_data)
            period = self.calculate_orbital_period(celestrak_data)
            
            return {
                "status": "available",
                "can_propagate": True,
                "tle_age_days": age_days,
                "accuracy_estimate": accuracy,
                "is_fresh": is_fresh,
                "max_recommended_age": max_age,
                "orbital_period_minutes": period,
                "next_update_recommended": is_fresh,
                "orbit_type": self.classify_orbit(celestrak_data)
            }
            
        except Exception as e:
            logger.error(f"Error generating propagation report: {e}")
            return {"status": "error", "can_propagate": False, "error": str(e)}
    
    def classify_orbit(self, tle_data: Dict[str, Any]) -> str:
        """Classify orbit type based on mean motion"""
        mean_motion = float(tle_data.get('MEAN_MOTION', 0))
        
        if mean_motion > 11:
            return "LEO"  # Low Earth Orbit
        elif mean_motion > 1.5:
            return "MEO"  # Medium Earth Orbit
        elif 0.9 <= mean_motion <= 1.1:
            return "GEO"  # Geostationary
        else:
            return "HEO"  # Highly Elliptical Orbit


def load_satellite_data(satellite_name: str) -> Optional[Dict[str, Any]]:
    """Load satellite data from JSON file"""
    try:
        # Map satellite names to filenames
        satellites_index = Path("Data/Satellites/index.json")
        if satellites_index.exists():
            with open(satellites_index, 'r') as f:
                index_data = json.load(f)
            
            # Find filename for satellite
            filename = None
            for sat in index_data.get('satellites', []):
                if sat['name'].lower() == satellite_name.lower():
                    filename = sat['filename']
                    break
            
            if filename:
                sat_file = Path(f"Data/Satellites/{filename}")
                if sat_file.exists():
                    with open(sat_file, 'r') as f:
                        return json.load(f)
        
        return None
    except Exception as e:
        logger.error(f"Error loading satellite data for {satellite_name}: {e}")
        return None


def main():
    """Test orbital propagation capabilities"""
    logger.info("🛰️ Testing Orbital Propagation Engine")
    
    propagator = OrbitalPropagator()
    
    # Test with Starlink (has actual TLE data)
    logger.info("📡 Loading Starlink data...")
    iss_data = load_satellite_data("Starlink")
    
    if iss_data:
        logger.info("✅ Starlink data loaded successfully")
        
        # Generate propagation report
        report = propagator.get_propagation_report(iss_data)
        logger.info(f"📊 Propagation Report: {report}")
        
        # Calculate current position
        celestrak_source = iss_data.get('dataSources', {}).get('celestrak')
        if celestrak_source and celestrak_source != "noValue":
            # Extract actual TLE data
            if isinstance(celestrak_source, dict) and 'data' in celestrak_source:
                celestrak_data = celestrak_source['data']
            else:
                celestrak_data = celestrak_source
            current_time = datetime.utcnow()
            position = propagator.propagate_position(celestrak_data, current_time)
            
            if position:
                pos = position['position']
                vel = position['velocity']
                logger.info(f"🌍 Current Position: {pos['latitude']:.4f}°, {pos['longitude']:.4f}°, {pos['altitude']:.1f}km")
                logger.info(f"🚀 Velocity: {vel['orbital_velocity']:.2f} km/s")
                logger.info(f"⏰ TLE Age: {position['tle_age_days']:.1f} days")
            
            # Predict passes over a location (example: New York)
            passes = propagator.predict_passes(celestrak_data, 40.7128, -74.0060, days=1)
            logger.info(f"🔭 Predicted passes over NYC: {len(passes)}")
            
            for i, pass_info in enumerate(passes[:3]):  # Show first 3 passes
                logger.info(f"   Pass {i+1}: {pass_info['rise']['time']} - Max elev: {pass_info['max_elevation']:.1f}°")
    
    else:
        logger.error("❌ Could not load ISS data")


if __name__ == "__main__":
    main() 