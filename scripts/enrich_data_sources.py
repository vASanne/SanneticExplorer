import json
import os
import requests
from pathlib import Path
import time
from datetime import datetime
from typing import Dict, Any, Optional

def get_exoplanet_data(target_name: str) -> Optional[Dict[str, Any]]:
    """Fetch exoplanet data from NASA Exoplanet Archive."""
    base_url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
    query = f"""
    SELECT *
    FROM ps
    WHERE hostname = '{target_name}'
    """
    params = {
        "query": query,
        "format": "json"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching exoplanet data for {target_name}: {e}")
        return None

def get_astrophysics_data(target_name: str) -> Optional[Dict[str, Any]]:
    """Fetch data from NASA Astrophysics Data System."""
    base_url = "https://api.adsabs.harvard.edu/v1/search/query"
    headers = {
        "Authorization": f"Bearer {os.getenv('ADS_API_KEY', 'DEMO_KEY')}"
    }
    params = {
        "q": f"title:{target_name}",
        "fl": "title,author,abstract,doi",
        "rows": 5
    }
    
    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching astrophysics data for {target_name}: {e}")
        return None

def get_space_track_data(satellite_name: str) -> Optional[Dict[str, Any]]:
    """Fetch satellite tracking data from Space-Track."""
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

def get_heasarc_data(target_name: str) -> Optional[Dict[str, Any]]:
    """Fetch data from NASA's HEASARC database."""
    base_url = "https://heasarc.gsfc.nasa.gov/cgi-bin/W3Browse/w3query.pl"
    params = {
        "tablehead": "name=heasarc_objects",
        "Action": "Query",
        "Coordinates": "Equatorial",
        "Equinox": "2000",
        "Radius": "0.1",
        "Fields": "All",
        "Name": target_name
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching HEASARC data for {target_name}: {e}")
        return None

def enrich_planet_data(planet_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich planet data with additional sources."""
    name = planet_data.get("name", "")
    if not name:
        return planet_data
    
    # Get exoplanet data if available
    exoplanet_data = get_exoplanet_data(name)
    if exoplanet_data:
        planet_data["exoplanetData"] = exoplanet_data
    
    # Get astrophysics data
    astro_data = get_astrophysics_data(name)
    if astro_data:
        planet_data["astrophysicsData"] = astro_data
    
    # Get HEASARC data
    heasarc_data = get_heasarc_data(name)
    if heasarc_data:
        planet_data["heasarcData"] = heasarc_data
    
    return planet_data

def enrich_spacecraft_data(spacecraft_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich spacecraft data with additional sources."""
    name = spacecraft_data.get("name", "")
    if not name:
        return spacecraft_data
    
    # Get Space-Track data
    space_track_data = get_space_track_data(name)
    if space_track_data:
        spacecraft_data["spaceTrackData"] = space_track_data
    
    # Get astrophysics data
    astro_data = get_astrophysics_data(name)
    if astro_data:
        spacecraft_data["astrophysicsData"] = astro_data
    
    return spacecraft_data

def enrich_star_data(star_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich star data with additional sources."""
    name = star_data.get("name", "")
    if not name:
        return star_data
    
    # Get HEASARC data
    heasarc_data = get_heasarc_data(name)
    if heasarc_data:
        star_data["heasarcData"] = heasarc_data
    
    # Get astrophysics data
    astro_data = get_astrophysics_data(name)
    if astro_data:
        star_data["astrophysicsData"] = astro_data
    
    return star_data

def main():
    # Process each data directory
    data_dirs = {
        "Data/Planets": enrich_planet_data,
        "Data/Spacecraft": enrich_spacecraft_data,
        "Data/Stars": enrich_star_data
    }
    
    for directory, enrich_func in data_dirs.items():
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"\nDirectory {directory} not found")
            continue
            
        print(f"\nProcessing {directory}...")
        
        # Process all JSON files in directory
        for file_path in dir_path.glob("*.json"):
            if file_path.name in [".template.json", "index.json"]:
                continue
                
            print(f"Enriching {file_path.name}...")
            
            # Load and enrich data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            enriched_data = enrich_func(data)
            
            # Add metadata
            if "metadata" not in enriched_data:
                enriched_data["metadata"] = {}
            enriched_data["metadata"]["lastEnriched"] = datetime.now().isoformat()
            
            # Save enriched data
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(enriched_data, f, indent=4)
            
            time.sleep(1)  # Be nice to the APIs

if __name__ == "__main__":
    main() 