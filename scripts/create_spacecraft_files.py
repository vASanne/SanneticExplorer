import json
import os
import requests
from pathlib import Path
import time
from datetime import datetime

def get_nasa_spacecraft_data(spacecraft_name):
    """Fetch spacecraft data from NASA's Spacecraft API"""
    base_url = "https://api.nasa.gov/spacecraft"
    params = {
        "api_key": os.getenv("NASA_API_KEY", "DEMO_KEY"),
        "name": spacecraft_name
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching NASA data for {spacecraft_name}: {e}")
        return None

def get_n2yo_data(spacecraft_name):
    """Fetch spacecraft tracking data from N2YO API"""
    base_url = "https://www.n2yo.com/rest/v1/satellite"
    params = {
        "apiKey": os.getenv("N2YO_API_KEY", "DEMO_KEY"),
        "name": spacecraft_name
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching N2YO data for {spacecraft_name}: {e}")
        return None

def get_wiki_data(spacecraft_name):
    """Fetch additional data from Wikipedia API"""
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "exintro": "true",
        "titles": spacecraft_name
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        pages = data["query"]["pages"]
        page_id = list(pages.keys())[0]
        return pages[page_id].get("extract", "")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Wikipedia data for {spacecraft_name}: {e}")
        return None

def create_spacecraft_file(spacecraft_data, filename, nasa_data=None, n2yo_data=None, wiki_data=None):
    """Create a JSON file for a spacecraft with data from multiple sources"""
    template = {
        "name": spacecraft_data.get("name", "noValue"),
        "type": "Spacecraft",
        "mission": {
            "name": spacecraft_data.get("missionName", "noValue"),
            "agency": spacecraft_data.get("agency", "noValue"),
            "launchDate": spacecraft_data.get("launchDate", "noValue"),
            "launchSite": spacecraft_data.get("launchSite", "noValue"),
            "launchVehicle": spacecraft_data.get("launchVehicle", "noValue"),
            "status": spacecraft_data.get("status", "noValue")
        },
        "specifications": {
            "mass": spacecraft_data.get("mass", "noValue"),
            "dimensions": spacecraft_data.get("dimensions", "noValue"),
            "power": spacecraft_data.get("power", "noValue"),
            "propulsion": spacecraft_data.get("propulsion", "noValue")
        },
        "instruments": spacecraft_data.get("instruments", []),
        "orbit": {
            "type": spacecraft_data.get("orbitType", "noValue"),
            "altitude": spacecraft_data.get("altitude", "noValue"),
            "inclination": spacecraft_data.get("inclination", "noValue"),
            "period": spacecraft_data.get("period", "noValue")
        },
        "targets": spacecraft_data.get("targets", []),
        "achievements": spacecraft_data.get("achievements", []),
        "images": spacecraft_data.get("images", []),
        "description": wiki_data if wiki_data else "noValue",
        "references": [],
        "lastUpdated": datetime.now().isoformat(),
        "dataSources": {
            "nasa": nasa_data if nasa_data else "noValue",
            "n2yo": n2yo_data if n2yo_data else "noValue"
        },
        "tracking": {
            "currentPosition": n2yo_data.get("position", "noValue") if n2yo_data else "noValue",
            "lastUpdate": n2yo_data.get("lastUpdate", "noValue") if n2yo_data else "noValue",
            "velocity": n2yo_data.get("velocity", "noValue") if n2yo_data else "noValue"
        }
    }
    
    # Save the template to a file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=4)

def main():
    # Read the index.json file
    index_path = Path("Data/Spacecraft/index.json")
    if not index_path.exists():
        print("index.json not found!")
        return

    with open(index_path, 'r', encoding='utf-8') as f:
        index_data = json.load(f)

    # Create output directory if it doesn't exist
    output_dir = Path("Data/Spacecraft")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each spacecraft
    for spacecraft in index_data["spacecraft"]:
        filename = output_dir / spacecraft["filename"]
        print(f"Creating or updating file for {spacecraft['name']}...")
        
        # Fetch data from multiple sources
        nasa_data = get_nasa_spacecraft_data(spacecraft["name"])
        n2yo_data = get_n2yo_data(spacecraft["name"])
        wiki_data = get_wiki_data(spacecraft["name"])
        
        create_spacecraft_file(spacecraft, filename, nasa_data, n2yo_data, wiki_data)
        time.sleep(1)  # Be nice to the APIs

    print("Done!")

if __name__ == "__main__":
    main() 