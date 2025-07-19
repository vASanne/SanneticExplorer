#!/usr/bin/env python3
"""
Simple script to import planet data into the database
Run this inside the backend container
"""

import json
import os
import sys
from pathlib import Path

# Add the sannetic_explorer package to path
sys.path.insert(0, '/app')

from sannetic_explorer.models.celestial_bodies import CelestialBody
from sannetic_explorer.models.orbital_parameters import OrbitalParameters  
from sannetic_explorer.models.physical_characteristics import PhysicalCharacteristics
from sannetic_explorer.models.base import Base
from sannetic_explorer.services.database import get_db, init_database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Planet data as constants (from the JSON files)
PLANETS_DATA = [
    {
        "name": "Mercury",
        "type": "terrestrial planet",
        "mass_kg": 3.301e23,
        "diameter_km": 4879,
        "distance_au": 0.387,
        "orbital_period_days": 88,
        "orbital_speed_kms": 47.36,
        "gravity_ms2": 3.7,
        "color": "#8c7853",
        "atmosphere": None,
        "moons": 0
    },
    {
        "name": "Venus", 
        "type": "terrestrial planet",
        "mass_kg": 4.867e24,
        "diameter_km": 12104,
        "distance_au": 0.723,
        "orbital_period_days": 225,
        "orbital_speed_kms": 35.02,
        "gravity_ms2": 8.87,
        "color": "#e7cdcd",
        "atmosphere": {"CO2": "96.5%", "N2": "3.5%"},
        "moons": 0
    },
    {
        "name": "Earth",
        "type": "terrestrial planet",
        "mass_kg": 5.972e24,
        "diameter_km": 12742,
        "distance_au": 1.0,
        "orbital_period_days": 365.25,
        "orbital_speed_kms": 29.78,
        "gravity_ms2": 9.81,
        "color": "#6b93d6",
        "atmosphere": {"N2": "78%", "O2": "21%", "Ar": "0.93%", "CO2": "0.04%"},
        "moons": 1
    },
    {
        "name": "Mars",
        "type": "terrestrial planet", 
        "mass_kg": 6.417e23,
        "diameter_km": 6779,
        "distance_au": 1.524,
        "orbital_period_days": 687,
        "orbital_speed_kms": 24.07,
        "gravity_ms2": 3.71,
        "color": "#c1440e",
        "atmosphere": {"CO2": "95.3%", "N2": "2.7%", "Ar": "1.6%"},
        "moons": 2
    },
    {
        "name": "Jupiter",
        "type": "gas giant",
        "mass_kg": 1.898e27,
        "diameter_km": 139820,
        "distance_au": 5.203,
        "orbital_period_days": 4333,
        "orbital_speed_kms": 13.07,
        "gravity_ms2": 24.79,
        "color": "#d8ca9d",
        "atmosphere": {"H2": "90%", "He": "10%"},
        "moons": 95
    },
    {
        "name": "Saturn",
        "type": "gas giant",
        "mass_kg": 5.683e26,
        "diameter_km": 116460,
        "distance_au": 9.537,
        "orbital_period_days": 10759,
        "orbital_speed_kms": 9.68,
        "gravity_ms2": 10.44,
        "color": "#fad5a5",
        "atmosphere": {"H2": "96.3%", "He": "3.25%"},
        "moons": 146,
        "has_rings": True
    },
    {
        "name": "Uranus",
        "type": "ice giant",
        "mass_kg": 8.681e25,
        "diameter_km": 50724,
        "distance_au": 19.191,
        "orbital_period_days": 30687,
        "orbital_speed_kms": 6.80,
        "gravity_ms2": 8.69,
        "color": "#4fd0e7",
        "atmosphere": {"H2": "82.5%", "He": "15.2%", "CH4": "2.3%"},
        "moons": 27
    },
    {
        "name": "Neptune",
        "type": "ice giant",
        "mass_kg": 1.024e26,
        "diameter_km": 49244,
        "distance_au": 30.069,
        "orbital_period_days": 60190,
        "orbital_speed_kms": 5.43,
        "gravity_ms2": 11.15,
        "color": "#4b70dd",
        "atmosphere": {"H2": "80%", "He": "19%", "CH4": "1%"},
        "moons": 14
    }
]

def main():
    """Import planet data"""
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/sannetic_explorer")
    
    # Create database engine and session
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        print("Starting planet data import...")
        
        for planet_data in PLANETS_DATA:
            planet_name = planet_data["name"]
            print(f"\nImporting {planet_name}...")
            
            # Check if planet already exists
            existing = session.query(CelestialBody).filter(CelestialBody.name == planet_name).first()
            if existing:
                print(f"  {planet_name} already exists, skipping...")
                continue
            
            # Create celestial body
            celestial_body = CelestialBody(
                name=planet_name,
                type="planet",
                subtype=planet_data["type"],
                mass_kg=planet_data["mass_kg"],
                radius_km=planet_data["diameter_km"] / 2,
                mean_distance_au=planet_data["distance_au"],
                orbital_speed_kms=planet_data["orbital_speed_kms"],
                surface_gravity_ms2=planet_data["gravity_ms2"],
                color_hex=planet_data["color"],
                data_quality="good",
                data_sources={"source": "NASA/JPL planetary data"}
            )
            
            session.add(celestial_body)
            session.flush()  # Get the ID
            
            # Create orbital parameters
            orbital_params = OrbitalParameters(
                celestial_body_id=celestial_body.id,
                semi_major_axis_km=planet_data["distance_au"] * 149597870.7,  # Convert AU to km
                orbital_period_days=planet_data["orbital_period_days"],
                orbital_speed_kms=planet_data["orbital_speed_kms"],
                distance_from_parent_km=planet_data["distance_au"] * 149597870.7,
                epoch="J2000"
            )
            session.add(orbital_params)
            
            # Create physical characteristics
            physical_chars = PhysicalCharacteristics(
                celestial_body_id=celestial_body.id,
                has_atmosphere=planet_data["atmosphere"] is not None,
                atmospheric_composition=planet_data["atmosphere"],
                has_rings=planet_data.get("has_rings", False),
                surface_type="rocky" if "terrestrial" in planet_data["type"] else "gaseous"
            )
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
        import traceback
        traceback.print_exc()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main() 