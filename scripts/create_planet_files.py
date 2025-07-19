import json
import os
import requests
from pathlib import Path
import time
from datetime import datetime

def get_nasa_planet_data(planet_name):
    """Fetch planet data from NASA's Solar System Exploration API"""
    base_url = "https://api.nasa.gov/planetary/apod"
    params = {
        "api_key": os.getenv("NASA_API_KEY", "DEMO_KEY"),
        "count": 1
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching NASA data for {planet_name}: {e}")
        return None

def get_jpl_planet_data(planet_name):
    """Fetch planet data from JPL Small-Body Database API"""
    base_url = "https://ssd-api.jpl.nasa.gov/sbdb.api"
    params = {
        "sstr": planet_name,
        "full-prec": "true"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("count", 0) == 0:
            print(f"No JPL data found for {planet_name}")
            return None
            
        return data["data"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching JPL data for {planet_name}: {e}")
        return None

def get_wiki_data(planet_name):
    """Fetch additional data from Wikipedia API"""
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "exintro": "true",
        "titles": planet_name
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        pages = data["query"]["pages"]
        page_id = list(pages.keys())[0]
        return pages[page_id].get("extract", "")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Wikipedia data for {planet_name}: {e}")
        return None

def create_planet_file(planet_data, filename, nasa_data=None, jpl_data=None, wiki_data=None):
    """Create a JSON file for a planet with data from multiple sources"""
    template = {
        "name": planet_data.get("name", "noValue"),
        "type": "Planet",
        "discovery": {
            "discoverer": "noValue",
            "date": "noValue",
            "method": "noValue"
        },
        "physical": {
            "mass": planet_data.get("mass", "noValue"),
            "radius": planet_data.get("radius", "noValue"),
            "density": planet_data.get("density", "noValue"),
            "surfaceGravity": planet_data.get("surfaceGravity", "noValue"),
            "escapeVelocity": planet_data.get("escapeVelocity", "noValue"),
            "unit": "kg"
        },
        "orbit": {
            "semiMajorAxis": planet_data.get("semiMajorAxis", "noValue"),
            "eccentricity": planet_data.get("eccentricity", "noValue"),
            "inclination": planet_data.get("inclination", "noValue"),
            "orbitalPeriod": planet_data.get("orbitalPeriod", "noValue"),
            "unit": "days"
        },
        "atmosphere": {
            "composition": planet_data.get("atmosphereComposition", "noValue"),
            "pressure": planet_data.get("atmospherePressure", "noValue"),
            "temperature": planet_data.get("atmosphereTemperature", "noValue")
        },
        "surface": {
            "composition": planet_data.get("surfaceComposition", "noValue"),
            "temperature": planet_data.get("surfaceTemperature", "noValue"),
            "features": planet_data.get("surfaceFeatures", [])
        },
        "moons": planet_data.get("moons", []),
        "rings": planet_data.get("rings", []),
        "exploration": {
            "missions": planet_data.get("missions", []),
            "firstFlyby": planet_data.get("firstFlyby", "noValue"),
            "firstOrbiter": planet_data.get("firstOrbiter", "noValue"),
            "firstLander": planet_data.get("firstLander", "noValue")
        },
        "images": planet_data.get("images", []),
        "description": wiki_data if wiki_data else "noValue",
        "references": [],
        "lastUpdated": datetime.now().isoformat(),
        "dataSources": {
            "nasa": nasa_data if nasa_data else "noValue",
            "jpl": jpl_data if jpl_data else "noValue"
        }
    }
    
    # Save the template to a file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=4)

def main():
    # Read the index.json file
    index_path = Path("Data/Planets/index.json")
    if not index_path.exists():
        print("index.json not found!")
        return

    with open(index_path, 'r', encoding='utf-8') as f:
        index_data = json.load(f)

    # Create output directory if it doesn't exist
    output_dir = Path("Data/Planets")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each planet
    for planet in index_data["planets"]:
        filename = output_dir / planet["filename"]
        print(f"Creating or updating file for {planet['name']}...")
        
        # Fetch data from multiple sources
        nasa_data = get_nasa_planet_data(planet["name"])
        jpl_data = get_jpl_planet_data(planet["name"])
        wiki_data = get_wiki_data(planet["name"])
        
        create_planet_file(planet, filename, nasa_data, jpl_data, wiki_data)
        time.sleep(1)  # Be nice to the APIs

    print("Done!")

if __name__ == "__main__":
    main() 