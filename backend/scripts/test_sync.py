#!/usr/bin/env python3
"""
Test script for solar system data synchronization
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sync import SolarSystemDataSync

def create_test_data():
    """Create test data for synchronization testing"""
    test_data_dir = Path("test_data")
    test_data_dir.mkdir(exist_ok=True)
    
    # Create Planets category
    planets_dir = test_data_dir / "Planets"
    planets_dir.mkdir(exist_ok=True)
    
    # Create template
    template = {
        "name": "string",
        "type": "string",
        "mass": {"value": "number", "unit": "string"},
        "diameter": {"value": "number", "unit": "string"},
        "orbit": {
            "semiMajorAxis": {"value": "number", "unit": "string"},
            "eccentricity": "number",
            "orbitalPeriod": {"value": "number", "unit": "string"}
        }
    }
    
    with open(planets_dir / "template.json", 'w') as f:
        json.dump(template, f, indent=2)
    
    # Create test planet data
    earth_data = {
        "name": "Earth",
        "type": "terrestrial planet",
        "mass": {"value": 5.972e24, "unit": "kg"},
        "diameter": {"value": 12742, "unit": "km"},
        "gravity": {"value": 9.81, "unit": "m/s²"},
        "orbit": {
            "semiMajorAxis": {"value": 1.0, "unit": "AU"},
            "eccentricity": 0.0167,
            "orbitalPeriod": {"value": 365.25, "unit": "days"},
            "orbitalSpeed": {"value": 29.78, "unit": "km/s"}
        },
        "atmosphere": {
            "present": True,
            "pressure": {"value": 101325, "unit": "Pa"},
            "composition": {"nitrogen": "78%", "oxygen": "21%"}
        },
        "surface": {
            "type": "rocky",
            "features": ["mountains", "oceans", "continents"]
        },
        "rings": {"hasRings": False},
        "discovery": {"date": "prehistoric", "discoverer": "unknown"},
        "metadata": {"dataQuality": "excellent"},
        "dataSources": {"nasa": "verified", "esa": "verified"}
    }
    
    with open(planets_dir / "earth.json", 'w') as f:
        json.dump(earth_data, f, indent=2)
    
    # Create Stars category
    stars_dir = test_data_dir / "Stars"
    stars_dir.mkdir(exist_ok=True)
    
    sun_data = {
        "name": "Sun",
        "type": "G-type main-sequence star",
        "mass": {"value": 1.989e30, "unit": "kg"},
        "radius": {"value": 696340, "unit": "km"},
        "stellarParameters": {
            "spectralType": "G2V",
            "luminosity": {"value": 1, "unit": "L☉"},
            "effectiveTemperature": {"value": 5778, "unit": "K"},
            "absoluteMagnitude": {"value": 4.83, "unit": "mag"},
            "apparentMagnitude": {"value": -26.74, "unit": "mag"}
        },
        "discovery": {"date": "prehistoric", "discoverer": "unknown"},
        "metadata": {"dataQuality": "excellent"}
    }
    
    with open(stars_dir / "sun.json", 'w') as f:
        json.dump(sun_data, f, indent=2)
    
    # Create NaturalSatellites category
    moons_dir = test_data_dir / "NaturalSatellites"
    moons_dir.mkdir(exist_ok=True)
    
    moon_data = {
        "name": "Moon",
        "type": "natural satellite",
        "parentBody": "Earth",
        "mass": {"value": 7.34767309e22, "unit": "kg"},
        "radius": {"value": 1737.4, "unit": "km"},
        "orbit": {
            "semiMajorAxis": {"value": 384400, "unit": "km"},
            "eccentricity": 0.0549,
            "orbitalPeriod": {"value": 27.322, "unit": "days"},
            "orbitalSpeed": {"value": 1.022, "unit": "km/s"}
        },
        "atmosphere": {"present": False},
        "surface": {
            "type": "rocky",
            "features": ["craters", "maria", "highlands"]
        },
        "discovery": {"date": "prehistoric", "discoverer": "unknown"},
        "metadata": {"dataQuality": "excellent"}
    }
    
    with open(moons_dir / "moon.json", 'w') as f:
        json.dump(moon_data, f, indent=2)
    
    return test_data_dir

def test_sync():
    """Test the synchronization functionality"""
    print("Creating test data...")
    test_data_dir = create_test_data()
    
    print("Testing synchronization...")
    sync = SolarSystemDataSync(data_dir=str(test_data_dir))
    
    try:
        stats = sync.run_sync(update_existing=True)
        print("Test completed successfully!")
        print(f"Statistics: {stats}")
        return True
    except Exception as e:
        print(f"Test failed: {e}")
        return False
    finally:
        # Clean up test data
        import shutil
        shutil.rmtree(test_data_dir, ignore_errors=True)

if __name__ == "__main__":
    success = test_sync()
    sys.exit(0 if success else 1) 