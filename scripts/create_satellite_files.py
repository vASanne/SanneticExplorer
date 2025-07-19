import json
import os
import requests
from pathlib import Path
import time
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import ephem
from ephem import readtle, Ecliptic, Equatorial
import numpy as np
from math import pi, sqrt, cos, sin, atan2

def get_celestrak_data(satellite_name: str) -> Optional[Dict[str, Any]]:
    """Fetch satellite data from Celestrak."""
    base_url = "https://celestrak.org/NORAD/elements/gp.php"
    params = {
        "NAME": satellite_name,
        "FORMAT": "json"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Celestrak data for {satellite_name}: {e}")
        return None

def get_n2yo_data(satellite_name: str) -> Optional[Dict[str, Any]]:
    """Fetch satellite data from N2YO."""
    base_url = "https://www.n2yo.com/rest/v1/satellite"
    params = {
        "apiKey": os.getenv("N2YO_API_KEY", "DEMO_KEY"),
        "name": satellite_name
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching N2YO data for {satellite_name}: {e}")
        return None

def get_space_track_data(satellite_name: str) -> Optional[Dict[str, Any]]:
    """Fetch satellite data from Space-Track."""
    base_url = "https://www.space-track.org/ajaxauth/login"
    data = {
        "identity": os.getenv("SPACE_TRACK_USERNAME", ""),
        "password": os.getenv("SPACE_TRACK_PASSWORD", "")
    }
    
    try:
        # First, get the session
        session = requests.Session()
        response = session.post(base_url, data=data)
        response.raise_for_status()
        
        # Then, get the satellite data
        query_url = "https://www.space-track.org/basicspacedata/query/class/gp/NAME/" + satellite_name
        response = session.get(query_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Space-Track data for {satellite_name}: {e}")
        return None

def get_wiki_data(satellite_name: str) -> Optional[str]:
    """Fetch additional data from Wikipedia API."""
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "exintro": "true",
        "titles": satellite_name
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        pages = data["query"]["pages"]
        page_id = list(pages.keys())[0]
        return pages[page_id].get("extract", "")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Wikipedia data for {satellite_name}: {e}")
        return None

def calculate_orbital_elements(tle_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate detailed orbital elements from TLE data."""
    try:
        # Create satellite object from TLE
        sat = readtle(
            tle_data.get("name", "Unknown"),
            tle_data.get("line1", ""),
            tle_data.get("line2", "")
        )
        
        # Calculate orbit parameters
        sat.compute()
        
        # Basic orbital elements
        a = sat.a  # semi-major axis in kilometers
        e = sat.e  # eccentricity
        i = sat.inc  # inclination in degrees
        raan = sat.raan  # right ascension of ascending node in degrees
        argp = sat.argp  # argument of perigee in degrees
        M = sat.M  # mean anomaly in degrees
        n = sat.n  # mean motion in revolutions per day
        
        # Calculate additional parameters
        b = a * sqrt(1 - e**2)  # semi-minor axis
        p = a * (1 - e**2)  # semi-latus rectum
        T = 2 * pi * sqrt(a**3 / (398600.4418))  # orbital period in seconds
        v = sat.n * 2 * pi / 86400  # angular velocity in radians per second
        
        # Calculate true anomaly
        E = M + e * sin(M)  # eccentric anomaly (approximate)
        for _ in range(5):  # Newton-Raphson iteration for better accuracy
            E = E - (E - e * sin(E) - M) / (1 - e * cos(E))
        nu = 2 * atan2(sqrt(1 + e) * sin(E/2), sqrt(1 - e) * cos(E/2))  # true anomaly
        
        # Calculate orbital velocity
        r = a * (1 - e * cos(E))  # distance from center
        v_total = sqrt(398600.4418 * (2/r - 1/a))  # total velocity in km/s
        
        # Calculate ground track parameters
        earth_radius = 6378.137  # Earth's radius in km
        period_minutes = T / 60
        ground_track_shift = 360 * (period_minutes / 1440)  # longitudinal shift per orbit
        
        return {
            "basic": {
                "semiMajorAxis": a,  # in kilometers
                "semiMinorAxis": b,  # in kilometers
                "eccentricity": e,
                "inclination": i,  # in degrees
                "rightAscension": raan,  # in degrees
                "argumentOfPeriapsis": argp,  # in degrees
                "meanAnomaly": M,  # in degrees
                "trueAnomaly": np.degrees(nu),  # in degrees
                "period": T / 86400,  # in days
                "meanMotion": n  # in revolutions per day
            },
            "derived": {
                "semiLatusRectum": p,  # in kilometers
                "angularVelocity": v,  # in radians per second
                "orbitalVelocity": v_total,  # in km/s
                "periodMinutes": period_minutes,
                "groundTrackShift": ground_track_shift  # in degrees per orbit
            },
            "epoch": str(sat.epoch)
        }
    except Exception as e:
        print(f"Error calculating orbital elements: {e}")
        return {}

def calculate_visibility_windows(sat: ephem.EarthSatellite, observer_lat: float, observer_lon: float, 
                               days: int = 1) -> Dict[str, Any]:
    """Calculate visibility windows for a ground station."""
    try:
        observer = ephem.Observer()
        observer.lat = str(observer_lat)
        observer.lon = str(observer_lon)
        
        visibility_windows = []
        current_time = datetime.now()
        
        for day in range(days):
            observer.date = current_time
            next_pass = observer.next_pass(sat)
            
            if next_pass:
                rise_time, rise_az, max_alt_time, max_alt, set_time, set_az = next_pass
                
                visibility_windows.append({
                    "rise": {
                        "time": str(rise_time),
                        "azimuth": np.degrees(rise_az)
                    },
                    "culmination": {
                        "time": str(max_alt_time),
                        "altitude": np.degrees(max_alt)
                    },
                    "set": {
                        "time": str(set_time),
                        "azimuth": np.degrees(set_az)
                    },
                    "duration": (set_time - rise_time) * 86400  # duration in seconds
                })
            
            current_time = current_time.replace(day=current_time.day + 1)
        
        return {
            "observer": {
                "latitude": observer_lat,
                "longitude": observer_lon
            },
            "windows": visibility_windows
        }
    except Exception as e:
        print(f"Error calculating visibility windows: {e}")
        return {}

def calculate_orbital_perturbations(tle_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate orbital perturbations and their effects."""
    try:
        sat = readtle(
            tle_data.get("name", "Unknown"),
            tle_data.get("line1", ""),
            tle_data.get("line2", "")
        )
        
        # Extract perturbation parameters from TLE
        bstar = sat.bstar  # B* drag term
        ndot = sat.ndot  # First derivative of mean motion
        nddot = sat.nddot  # Second derivative of mean motion
        
        # Calculate approximate decay rate
        decay_rate = -2 * bstar * 0.5  # Approximate decay rate in km/day
        
        return {
            "drag": {
                "bstar": bstar,
                "decayRate": decay_rate
            },
            "motion": {
                "ndot": ndot,  # First derivative of mean motion
                "nddot": nddot  # Second derivative of mean motion
            }
        }
    except Exception as e:
        print(f"Error calculating orbital perturbations: {e}")
        return {}

def create_satellite_file(satellite_data: Dict[str, Any], filename: Path, 
                         celestrak_data: Optional[Dict[str, Any]] = None,
                         n2yo_data: Optional[Dict[str, Any]] = None,
                         space_track_data: Optional[Dict[str, Any]] = None,
                         wiki_data: Optional[str] = None) -> None:
    """Create a JSON file for a satellite with data from multiple sources."""
    template = {
        "name": satellite_data.get("name", "noValue"),
        "type": "Satellite",
        "mission": {
            "name": satellite_data.get("missionName", "noValue"),
            "agency": satellite_data.get("agency", "noValue"),
            "launchDate": satellite_data.get("launchDate", "noValue"),
            "launchSite": satellite_data.get("launchSite", "noValue"),
            "launchVehicle": satellite_data.get("launchVehicle", "noValue"),
            "status": satellite_data.get("status", "noValue")
        },
        "specifications": {
            "mass": satellite_data.get("mass", "noValue"),
            "dimensions": satellite_data.get("dimensions", "noValue"),
            "power": satellite_data.get("power", "noValue"),
            "propulsion": satellite_data.get("propulsion", "noValue")
        },
        "orbit": {
            "type": satellite_data.get("orbitType", "noValue"),
            "altitude": satellite_data.get("altitude", "noValue"),
            "inclination": satellite_data.get("inclination", "noValue"),
            "period": satellite_data.get("period", "noValue")
        },
        "payload": satellite_data.get("payload", []),
        "groundStations": satellite_data.get("groundStations", []),
        "images": satellite_data.get("images", []),
        "description": wiki_data if wiki_data else "noValue",
        "references": [],
        "lastUpdated": datetime.now().isoformat(),
        "dataSources": {
            "celestrak": celestrak_data if celestrak_data else "noValue",
            "n2yo": n2yo_data if n2yo_data else "noValue",
            "spaceTrack": space_track_data if space_track_data else "noValue"
        }
    }
    
    # Add enhanced orbit calculations if available
    if celestrak_data:
        # Calculate detailed orbital elements
        orbital_elements = calculate_orbital_elements(celestrak_data)
        if orbital_elements:
            template["orbit"].update(orbital_elements)
        
        # Calculate orbital perturbations
        perturbations = calculate_orbital_perturbations(celestrak_data)
        if perturbations:
            template["orbit"]["perturbations"] = perturbations
        
        # Calculate visibility windows for each ground station
        if "groundStations" in template and template["groundStations"]:
            visibility = {}
            for station in template["groundStations"]:
                if "latitude" in station and "longitude" in station:
                    windows = calculate_visibility_windows(
                        readtle(template["name"], celestrak_data["line1"], celestrak_data["line2"]),
                        station["latitude"],
                        station["longitude"]
                    )
                    if windows:
                        visibility[station["name"]] = windows
            if visibility:
                template["orbit"]["visibility"] = visibility
    
    # Add tracking data if available
    if n2yo_data:
        template["tracking"] = {
            "currentPosition": n2yo_data.get("position", "noValue"),
            "lastUpdate": n2yo_data.get("lastUpdate", "noValue"),
            "velocity": n2yo_data.get("velocity", "noValue")
        }
    
    # Save the template to a file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=4)

def main():
    # Read the index.json file
    index_path = Path("Data/Satellites/index.json")
    if not index_path.exists():
        print("index.json not found!")
        return

    with open(index_path, 'r', encoding='utf-8') as f:
        index_data = json.load(f)

    # Create output directory if it doesn't exist
    output_dir = Path("Data/Satellites")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each satellite
    for satellite in index_data["satellites"]:
        filename = output_dir / satellite["filename"]
        print(f"Creating or updating file for {satellite['name']}...")
        
        # Fetch data from multiple sources
        celestrak_data = get_celestrak_data(satellite["name"])
        n2yo_data = get_n2yo_data(satellite["name"])
        space_track_data = get_space_track_data(satellite["name"])
        wiki_data = get_wiki_data(satellite["name"])
        
        create_satellite_file(satellite, filename, celestrak_data, n2yo_data, space_track_data, wiki_data)
        time.sleep(1)  # Be nice to the APIs

    print("Done!")

if __name__ == "__main__":
    main() 