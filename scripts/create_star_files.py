import json
import os
import requests
from pathlib import Path
import time
from datetime import datetime

def get_simbad_data(star_name):
    """Fetch star data from SIMBAD Astronomical Database"""
    base_url = "http://simbad.u-strasbg.fr/simbad/sim-id"
    params = {
        "Ident": star_name,
        "output.format": "JSON"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching SIMBAD data for {star_name}: {e}")
        return None

def get_gaia_data(star_name):
    """Fetch star data from Gaia Archive"""
    base_url = "https://gea.esac.esa.int/tap-server/tap/sync"
    query = f"""
    SELECT *
    FROM gaiadr3.gaia_source
    WHERE source_id IN (
        SELECT source_id
        FROM gaiadr3.gaia_source
        WHERE designation = '{star_name}'
    )
    """
    params = {
        "request": "doQuery",
        "lang": "ADQL",
        "query": query,
        "format": "json"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Gaia data for {star_name}: {e}")
        return None

def get_wiki_data(star_name):
    """Fetch additional data from Wikipedia API"""
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "exintro": "true",
        "titles": star_name
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        pages = data["query"]["pages"]
        page_id = list(pages.keys())[0]
        return pages[page_id].get("extract", "")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Wikipedia data for {star_name}: {e}")
        return None

def create_star_file(star_data, filename, simbad_data=None, gaia_data=None, wiki_data=None):
    """Create a JSON file for a star with data from multiple sources"""
    template = {
        "name": star_data.get("name", "noValue"),
        "type": "Star",
        "basic": {
            "designation": star_data.get("designation", "noValue"),
            "constellation": star_data.get("constellation", "noValue"),
            "distance": star_data.get("distance", "noValue"),
            "apparentMagnitude": star_data.get("apparentMagnitude", "noValue"),
            "absoluteMagnitude": star_data.get("absoluteMagnitude", "noValue")
        },
        "physical": {
            "spectralType": star_data.get("spectralType", "noValue"),
            "temperature": star_data.get("temperature", "noValue"),
            "radius": star_data.get("radius", "noValue"),
            "mass": star_data.get("mass", "noValue"),
            "luminosity": star_data.get("luminosity", "noValue"),
            "age": star_data.get("age", "noValue"),
            "rotationPeriod": star_data.get("rotationPeriod", "noValue")
        },
        "position": {
            "rightAscension": star_data.get("rightAscension", "noValue"),
            "declination": star_data.get("declination", "noValue"),
            "galacticCoordinates": star_data.get("galacticCoordinates", "noValue")
        },
        "motion": {
            "properMotion": star_data.get("properMotion", "noValue"),
            "radialVelocity": star_data.get("radialVelocity", "noValue"),
            "parallax": star_data.get("parallax", "noValue")
        },
        "companions": star_data.get("companions", []),
        "planetarySystem": star_data.get("planetarySystem", []),
        "images": star_data.get("images", []),
        "description": wiki_data if wiki_data else "noValue",
        "references": [],
        "lastUpdated": datetime.now().isoformat(),
        "dataSources": {
            "simbad": simbad_data if simbad_data else "noValue",
            "gaia": gaia_data if gaia_data else "noValue"
        }
    }
    
    # Save the template to a file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=4)

def main():
    # Read the index.json file
    index_path = Path("Data/Stars/index.json")
    if not index_path.exists():
        print("index.json not found!")
        return

    with open(index_path, 'r', encoding='utf-8') as f:
        index_data = json.load(f)

    # Create output directory if it doesn't exist
    output_dir = Path("Data/Stars")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each star
    for star in index_data["stars"]:
        filename = output_dir / star["filename"]
        print(f"Creating or updating file for {star['name']}...")
        
        # Fetch data from multiple sources
        simbad_data = get_simbad_data(star["name"])
        gaia_data = get_gaia_data(star["name"])
        wiki_data = get_wiki_data(star["name"])
        
        create_star_file(star, filename, simbad_data, gaia_data, wiki_data)
        time.sleep(1)  # Be nice to the APIs

    print("Done!")

if __name__ == "__main__":
    main() 