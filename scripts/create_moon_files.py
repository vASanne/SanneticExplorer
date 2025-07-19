import json
import os
import requests
from pathlib import Path
import time

def get_moon_data(moon_name):
    """Fetch moon data from JPL Small-Body Database API"""
    base_url = "https://ssd-api.jpl.nasa.gov/sbdb.api"
    params = {
        "sstr": moon_name,
        "full-prec": "true"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("count", 0) == 0:
            print(f"No data found for {moon_name}")
            return None
            
        return data["data"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {moon_name}: {e}")
        return None

def create_moon_file(moon_data, filename, jpl_data=None):
    """Create a JSON file for a moon with the template structure and JPL data"""
    if jpl_data is None:
        jpl_data = {}
    template = {
        "name": moon_data.get("name", "noValue"),
        "type": moon_data.get("type", "noValue"),
        "parentBody": moon_data.get("planet", "noValue"),
        "planet": moon_data["planet"],
        "discovery": moon_data["discovery"],
        "radius": moon_data["radius"],
        "unit": moon_data["unit"],
        "description": "",
        "composition": {
            "surface": "",
            "atmosphere": "",
            "interior": ""
        },
        "orbit": {
            "semiMajorAxis": 0,
            "eccentricity": 0,
            "inclination": 0,
            "orbitalPeriod": 0,
            "unit": "days"
        },
        "physical": {
            "mass": 0,
            "density": 0,
            "surfaceGravity": 0,
            "escapeVelocity": 0,
            "unit": "kg"
        },
        "exploration": {
            "missions": [],
            "discoverer": "",
            "discoveryDate": "",
            "discoveryMethod": ""
        },
        "images": [],
        "references": [],
        "jplMeta": {
            "orbitMeta": {
                "n_obs_used": jpl_data.get("n_obs_used", "noValue"),
                "first_obs": jpl_data.get("first_obs", "noValue"),
                "last_obs": jpl_data.get("last_obs", "noValue"),
                "rms": jpl_data.get("rms", "noValue"),
                "soln_date": jpl_data.get("soln_date", "noValue"),
                "condition_code": jpl_data.get("condition_code", "noValue"),
                "orbit_id": jpl_data.get("orbit_id", "noValue"),
                "producer": jpl_data.get("producer", "noValue"),
                "data_arc": jpl_data.get("data_arc", "noValue"),
                "epoch": jpl_data.get("epoch", "noValue"),
                "equinox": jpl_data.get("equinox", "noValue")
            },
            "orbitElements": jpl_data.get("elements", []),
            "objectMeta": {
                "fullname": jpl_data.get("fullname", "noValue"),
                "spkid": jpl_data.get("spkid", "noValue"),
                "orbit_class": jpl_data.get("orbit_class", {"name": "noValue", "code": "noValue"}),
                "pha": jpl_data.get("pha", "noValue"),
                "neo": jpl_data.get("neo", "noValue"),
                "kind": jpl_data.get("kind", "noValue")
            }
        }
    }
    
    # JPL-API-Daten einfügen, falls vorhanden
    jpl = jpl_data or {}
    template["jplMeta"] = {
        "orbitMeta": {
            "n_obs_used": jpl.get("n_obs_used", "noValue"),
            "first_obs": jpl.get("first_obs", "noValue"),
            "last_obs": jpl.get("last_obs", "noValue"),
            "rms": jpl.get("rms", "noValue"),
            "soln_date": jpl.get("soln_date", "noValue"),
            "condition_code": jpl.get("condition_code", "noValue"),
            "orbit_id": jpl.get("orbit_id", "noValue"),
            "producer": jpl.get("producer", "noValue"),
            "data_arc": jpl.get("data_arc", "noValue"),
            "epoch": jpl.get("epoch", "noValue"),
            "equinox": jpl.get("equinox", "noValue")
        },
        "orbitElements": jpl.get("elements", []),
        "objectMeta": {
            "fullname": jpl.get("fullname", "noValue"),
            "spkid": jpl.get("spkid", "noValue"),
            "orbit_class": jpl.get("orbit_class", {"name": "noValue", "code": "noValue"}),
            "pha": jpl.get("pha", "noValue"),
            "neo": jpl.get("neo", "noValue"),
            "kind": jpl.get("kind", "noValue")
        }
    }
    
    # Save the template to a file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=4)

def main():
    # Read the index.json file
    index_path = Path("Data/NaturalSatellites/index.json")
    if not index_path.exists():
        print("index.json not found!")
        return

    with open(index_path, 'r', encoding='utf-8') as f:
        index_data = json.load(f)

    # Create output directory if it doesn't exist
    output_dir = Path("Data/NaturalSatellites")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each moon
    for moon in index_data["naturalSatellites"]:
        filename = output_dir / moon["filename"]
        print(f"(Update) Creating or updating file for {moon['name']}...")
        # JPL-API-Daten abrufen
        jpl_data = {}
        try:
            api_response = get_moon_data(moon["name"])
            if api_response and "orbit" in api_response and "object" in api_response:
                jpl_data.update(api_response["orbit"])
                jpl_data.update(api_response["object"])
        except Exception as e:
            print(f"Fehler beim Abrufen der JPL-Daten für {moon['name']}: {e}")
        create_moon_file(moon, filename, jpl_data)
        time.sleep(0.5)

    print("Done!")

if __name__ == "__main__":
    main() 