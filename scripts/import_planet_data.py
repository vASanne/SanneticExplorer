#!/usr/bin/env python3
"""
Import planet data from JSON files into the database
"""

import json
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sannetic_explorer.models.celestial_bodies import CelestialBody
from sannetic_explorer.models.orbital_parameters import OrbitalParameters  
from sannetic_explorer.models.physical_characteristics import PhysicalCharacteristics
from sannetic_explorer.models.base import Base

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/sannetic_explorer")

def load_planet_data():
    """Load planet data from JSON files"""
    planets_dir = project_root / "Data" / "Planets"
    planet_files = [
        "mercury.json", "venus.json", "earth.json", "mars.json",
        "jupiter.json", "saturn.json", "uranus.json", "neptune.json"
    ]
    
    planets_data = []
    
    for planet_file in planet_files:
        file_path = planets_dir / planet_file
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                planets_data.append(data)
        else:
            print(f"Warning: {planet_file} not found")
    
    return planets_data

def create_celestial_body(planet_data):
    """Create a CelestialBody from planet JSON data"""
    
    # Extract basic info
    name = planet_data.get("name", "Unknown")
    planet_type = planet_data.get("type", "planet")
    
    # Extract mass
    mass_kg = None
    if "mass" in planet_data and isinstance(planet_data["mass"], dict):
        mass_kg = planet_data["mass"].get("value")
    
    # Extract radius (diameter / 2)
    radius_km = None
    if "diameter" in planet_data and isinstance(planet_data["diameter"], dict):
        diameter = planet_data["diameter"].get("value")
        if diameter:
            radius_km = diameter / 2
    
    # Extract distance from sun
    mean_distance_au = None
    if "distanceFromSun" in planet_data and isinstance(planet_data["distanceFromSun"], dict):
        mean_distance_au = planet_data["distanceFromSun"].get("value")
    
    # Extract orbital speed
    orbital_speed_kms = None
    if "orbit" in planet_data and "orbitalSpeed" in planet_data["orbit"]:
        orbital_speed_kms = planet_data["orbit"]["orbitalSpeed"].get("value")
    
    # Extract gravity
    surface_gravity_ms2 = None
    if "gravity" in planet_data and isinstance(planet_data["gravity"], dict):
        surface_gravity_ms2 = planet_data["gravity"].get("value")
    
    # Extract atmosphere composition for color
    color_hex = get_planet_color(name)
    
    # Extract moon count
    moon_count = 0
    if "moons" in planet_data and "count" in planet_data["moons"]:
        moon_count = planet_data["moons"]["count"]
    
    # Create CelestialBody
    celestial_body = CelestialBody(
        name=name,
        type="planet",
        subtype=planet_type,
        mass_kg=mass_kg,
        radius_km=radius_km,
        mean_distance_au=mean_distance_au,
        orbital_speed_kms=orbital_speed_kms,
        surface_gravity_ms2=surface_gravity_ms2,
        color_hex=color_hex,
        data_quality="good",
        data_sources={"source": f"Data/Planets/{name.lower()}.json"}
    )
    
    return celestial_body, planet_data

def create_orbital_parameters(celestial_body, planet_data):
    """Create OrbitalParameters from planet JSON data"""
    
    if "orbit" not in planet_data:
        return None
    
    orbit_data = planet_data["orbit"]
    
    # Extract orbital period
    orbital_period_days = None
    if "orbitalPeriod" in planet_data and isinstance(planet_data["orbitalPeriod"], dict):
        orbital_period_days = planet_data["orbitalPeriod"].get("value")
    
    # Extract rotation period
    rotation_period_hours = None
    if "rotationPeriod" in planet_data and isinstance(planet_data["rotationPeriod"], dict):
        rotation_days = planet_data["rotationPeriod"].get("value")
        if rotation_days:
            rotation_period_hours = rotation_days * 24
    
    # Extract orbital elements
    semi_major_axis_km = None
    if "semiMajorAxis" in orbit_data and isinstance(orbit_data["semiMajorAxis"], dict):
        au_value = orbit_data["semiMajorAxis"].get("value")
        if au_value:
            semi_major_axis_km = au_value * 149597870.7  # Convert AU to km
    
    eccentricity = orbit_data.get("eccentricity")
    
    inclination_degrees = None
    if "inclination" in orbit_data and isinstance(orbit_data["inclination"], dict):
        inclination_degrees = orbit_data["inclination"].get("value")
    
    longitude_ascending_node_degrees = None
    if "longitudeOfAscendingNode" in orbit_data and isinstance(orbit_data["longitudeOfAscendingNode"], dict):
        longitude_ascending_node_degrees = orbit_data["longitudeOfAscendingNode"].get("value")
    
    argument_periapsis_degrees = None
    if "argumentOfPeriapsis" in orbit_data and isinstance(orbit_data["argumentOfPeriapsis"], dict):
        argument_periapsis_degrees = orbit_data["argumentOfPeriapsis"].get("value")
    
    mean_anomaly_degrees = None
    if "meanAnomaly" in orbit_data and isinstance(orbit_data["meanAnomaly"], dict):
        mean_anomaly_degrees = orbit_data["meanAnomaly"].get("value")
    
    orbital_speed_kms = None
    if "orbitalSpeed" in orbit_data and isinstance(orbit_data["orbitalSpeed"], dict):
        orbital_speed_kms = orbit_data["orbitalSpeed"].get("value")
    
    # Distance from parent (sun)
    distance_from_parent_km = None
    if semi_major_axis_km:
        distance_from_parent_km = semi_major_axis_km
    
    orbital_params = OrbitalParameters(
        celestial_body_id=celestial_body.id,
        semi_major_axis_km=semi_major_axis_km,
        eccentricity=eccentricity,
        inclination_degrees=inclination_degrees,
        longitude_ascending_node_degrees=longitude_ascending_node_degrees,
        argument_periapsis_degrees=argument_periapsis_degrees,
        mean_anomaly_degrees=mean_anomaly_degrees,
        orbital_period_days=orbital_period_days,
        orbital_speed_kms=orbital_speed_kms,
        rotation_period_hours=rotation_period_hours,
        distance_from_parent_km=distance_from_parent_km,
        epoch=orbit_data.get("epoch", "J2000")
    )
    
    return orbital_params

def create_physical_characteristics(celestial_body, planet_data):
    """Create PhysicalCharacteristics from planet JSON data"""
    
    # Extract temperature data
    surface_temperature_k = None
    surface_temperature_min_k = None
    surface_temperature_max_k = None
    
    if "surfaceTemperature" in planet_data:
        temp_data = planet_data["surfaceTemperature"]
        if isinstance(temp_data, dict):
            if "value" in temp_data:
                # Single temperature value
                temp_celsius = temp_data["value"]
                surface_temperature_k = temp_celsius + 273.15
            elif "min" in temp_data and "max" in temp_data:
                # Temperature range
                surface_temperature_min_k = temp_data["min"] + 273.15
                surface_temperature_max_k = temp_data["max"] + 273.15
                surface_temperature_k = (surface_temperature_min_k + surface_temperature_max_k) / 2
    
    # Extract atmosphere data
    has_atmosphere = "atmosphere" in planet_data
    atmospheric_composition = None
    atmospheric_pressure_pa = None
    
    if has_atmosphere:
        atm_data = planet_data["atmosphere"]
        if "composition" in atm_data:
            atmospheric_composition = atm_data["composition"]
        if "pressure" in atm_data and isinstance(atm_data["pressure"], dict):
            atmospheric_pressure_pa = atm_data["pressure"].get("value")
    
    # Extract rings data
    has_rings = False
    ring_system = None
    if "rings" in planet_data:
        rings_data = planet_data["rings"]
        has_rings = rings_data.get("hasRings", False)
        if has_rings and "description" in rings_data:
            ring_system = {"description": rings_data["description"]}
    
    physical_chars = PhysicalCharacteristics(
        celestial_body_id=celestial_body.id,
        surface_temperature_k=surface_temperature_k,
        surface_temperature_min_k=surface_temperature_min_k,
        surface_temperature_max_k=surface_temperature_max_k,
        has_atmosphere=has_atmosphere,
        atmospheric_composition=atmospheric_composition,
        atmospheric_pressure_pa=atmospheric_pressure_pa,
        has_rings=has_rings,
        ring_system=ring_system,
        surface_type="rocky" if planet_data.get("type") == "terrestrial planet" else "gaseous"
    )
    
    return physical_chars

def get_planet_color(planet_name):
    """Get planet color in hex format"""
    colors = {
        "Mercury": "#8c7853",
        "Venus": "#e7cdcd", 
        "Earth": "#6b93d6",
        "Mars": "#c1440e",
        "Jupiter": "#d8ca9d",
        "Saturn": "#fad5a5",
        "Uranus": "#4fd0e7",
        "Neptune": "#4b70dd"
    }
    return colors.get(planet_name, "#ffffff")

def main():
    """Main function to import planet data"""
    
    # Create database engine and session
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Load planet data
        planets_data = load_planet_data()
        print(f"Loaded {len(planets_data)} planet data files")
        
        # Import each planet
        for planet_data in planets_data:
            planet_name = planet_data.get("name", "Unknown")
            print(f"\nImporting {planet_name}...")
            
            # Check if planet already exists
            existing = session.query(CelestialBody).filter(CelestialBody.name == planet_name).first()
            if existing:
                print(f"  {planet_name} already exists, skipping...")
                continue
            
            # Create celestial body
            celestial_body, full_data = create_celestial_body(planet_data)
            session.add(celestial_body)
            session.flush()  # Get the ID
            
            # Create orbital parameters
            orbital_params = create_orbital_parameters(celestial_body, planet_data)
            if orbital_params:
                session.add(orbital_params)
            
            # Create physical characteristics
            physical_chars = create_physical_characteristics(celestial_body, planet_data)
            if physical_chars:
                session.add(physical_chars)
            
            print(f"  {planet_name} imported successfully")
        
        # Commit all changes
        session.commit()
        print("\nAll planet data imported successfully!")
        
        # Show summary
        planet_count = session.query(CelestialBody).filter(CelestialBody.type == "planet").count()
        print(f"Total planets in database: {planet_count}")
        
    except Exception as e:
        session.rollback()
        print(f"Error importing planet data: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main() 