#!/usr/bin/env python3
"""
Data Migration Script
Migrates existing JSON data from Sannetic Explorer to PostgreSQL database
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from uuid import uuid4

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import database and models
from database import get_db, init_database
from models import (
    CelestialBody, OrbitalParameters, PhysicalCharacteristics, 
    StellarCharacteristics, SpacecraftMission, TLEElements,
    ExplorationHistory, SimulationState
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataMigrator:
    """Handles migration of JSON data to PostgreSQL database"""
    
    def __init__(self, data_dir: str = "Data"):
        self.data_dir = Path(data_dir)
        self.migration_stats = {
            "celestial_bodies": 0,
            "orbital_parameters": 0,
            "physical_characteristics": 0,
            "stellar_characteristics": 0,
            "spacecraft_missions": 0,
            "tle_elements": 0,
            "exploration_history": 0,
            "errors": []
        }
    
    def migrate_all_data(self):
        """Migrate all data from JSON files to database"""
        logger.info("Starting data migration...")
        
        # Initialize database
        init_database()
        
        # Migrate each data type
        self._migrate_stars()
        self._migrate_planets()
        self._migrate_natural_satellites()
        self._migrate_spacecraft()
        self._migrate_satellites()
        
        # Print migration statistics
        self._print_migration_stats()
    
    def _migrate_stars(self):
        """Migrate star data"""
        logger.info("Migrating stars...")
        stars_dir = self.data_dir / "Stars"
        
        if not stars_dir.exists():
            logger.warning("Stars directory not found")
            return
        
        # Process index file first
        index_file = stars_dir / "index.json"
        if index_file.exists():
            with open(index_file, 'r') as f:
                index_data = json.load(f)
            
            # Process each star
            for star_info in index_data.get('stars', []):
                star_name = star_info.get('name')
                if star_name:
                    self._migrate_star(star_name)
    
    def _migrate_star(self, star_name: str):
        """Migrate a single star"""
        star_file = self.data_dir / "Stars" / f"{star_name.lower()}.json"
        
        if not star_file.exists():
            logger.warning(f"Star file not found: {star_file}")
            return
        
        try:
            with open(star_file, 'r') as f:
                star_data = json.load(f)
            
            with get_db() as session:
                # Create celestial body
                celestial_body = self._create_celestial_body(
                    session, star_data, "star", None
                )
                
                # Create stellar characteristics
                if celestial_body:
                    self._create_stellar_characteristics(session, celestial_body, star_data)
                
                session.commit()
                self.migration_stats["celestial_bodies"] += 1
                
        except Exception as e:
            logger.error(f"Error migrating star {star_name}: {e}")
            self.migration_stats["errors"].append(f"Star {star_name}: {e}")
    
    def _migrate_planets(self):
        """Migrate planet data"""
        logger.info("Migrating planets...")
        planets_dir = self.data_dir / "Planets"
        
        if not planets_dir.exists():
            logger.warning("Planets directory not found")
            return
        
        # Get Sun as parent for planets
        sun_id = self._get_celestial_body_id("Sun")
        
        # Process index file
        index_file = planets_dir / "index.json"
        if index_file.exists():
            with open(index_file, 'r') as f:
                index_data = json.load(f)
            
            # Process each planet
            for planet_info in index_data.get('planets', []):
                planet_name = planet_info.get('name')
                if planet_name:
                    self._migrate_planet(planet_name, sun_id)
    
    def _migrate_planet(self, planet_name: str, parent_id: Optional[str]):
        """Migrate a single planet"""
        planet_file = self.data_dir / "Planets" / f"{planet_name.lower()}.json"
        
        if not planet_file.exists():
            logger.warning(f"Planet file not found: {planet_file}")
            return
        
        try:
            with open(planet_file, 'r') as f:
                planet_data = json.load(f)
            
            with get_db() as session:
                # Create celestial body
                celestial_body = self._create_celestial_body(
                    session, planet_data, "planet", parent_id
                )
                
                # Create orbital parameters
                if celestial_body:
                    self._create_orbital_parameters(session, celestial_body, planet_data)
                    self._create_physical_characteristics(session, celestial_body, planet_data)
                
                session.commit()
                self.migration_stats["celestial_bodies"] += 1
                
        except Exception as e:
            logger.error(f"Error migrating planet {planet_name}: {e}")
            self.migration_stats["errors"].append(f"Planet {planet_name}: {e}")
    
    def _migrate_natural_satellites(self):
        """Migrate natural satellite (moon) data"""
        logger.info("Migrating natural satellites...")
        moons_dir = self.data_dir / "NaturalSatellites"
        
        if not moons_dir.exists():
            logger.warning("NaturalSatellites directory not found")
            return
        
        # Process each moon file
        for moon_file in moons_dir.glob("*.json"):
            if moon_file.name == "index.json":
                continue
            
            moon_name = moon_file.stem
            self._migrate_natural_satellite(moon_name)
    
    def _migrate_natural_satellite(self, moon_name: str):
        """Migrate a single natural satellite"""
        moon_file = self.data_dir / "NaturalSatellites" / f"{moon_name}.json"
        
        try:
            with open(moon_file, 'r') as f:
                moon_data = json.load(f)
            
            # Get parent planet ID
            parent_name = moon_data.get('parentBody') or moon_data.get('planet')
            parent_id = self._get_celestial_body_id(parent_name) if parent_name else None
            
            with get_db() as session:
                # Create celestial body
                celestial_body = self._create_celestial_body(
                    session, moon_data, "moon", parent_id
                )
                
                # Create orbital parameters
                if celestial_body:
                    self._create_orbital_parameters(session, celestial_body, moon_data)
                    self._create_physical_characteristics(session, celestial_body, moon_data)
                
                session.commit()
                self.migration_stats["celestial_bodies"] += 1
                
        except Exception as e:
            logger.error(f"Error migrating moon {moon_name}: {e}")
            self.migration_stats["errors"].append(f"Moon {moon_name}: {e}")
    
    def _migrate_spacecraft(self):
        """Migrate spacecraft data"""
        logger.info("Migrating spacecraft...")
        spacecraft_dir = self.data_dir / "Spacecraft"
        
        if not spacecraft_dir.exists():
            logger.warning("Spacecraft directory not found")
            return
        
        # Process index file
        index_file = spacecraft_dir / "index.json"
        if index_file.exists():
            with open(index_file, 'r') as f:
                index_data = json.load(f)
            
            # Process each spacecraft
            for spacecraft_info in index_data.get('spacecraft', []):
                spacecraft_name = spacecraft_info.get('name')
                if spacecraft_name:
                    self._migrate_spacecraft_item(spacecraft_name)
    
    def _migrate_spacecraft_item(self, spacecraft_name: str):
        """Migrate a single spacecraft"""
        spacecraft_file = self.data_dir / "Spacecraft" / f"{spacecraft_name.lower()}.json"
        
        if not spacecraft_file.exists():
            logger.warning(f"Spacecraft file not found: {spacecraft_file}")
            return
        
        try:
            with open(spacecraft_file, 'r') as f:
                spacecraft_data = json.load(f)
            
            with get_db() as session:
                # Create celestial body
                celestial_body = self._create_celestial_body(
                    session, spacecraft_data, "spacecraft", None
                )
                
                # Create spacecraft mission
                if celestial_body:
                    self._create_spacecraft_mission(session, celestial_body, spacecraft_data)
                
                session.commit()
                self.migration_stats["celestial_bodies"] += 1
                
        except Exception as e:
            logger.error(f"Error migrating spacecraft {spacecraft_name}: {e}")
            self.migration_stats["errors"].append(f"Spacecraft {spacecraft_name}: {e}")
    
    def _migrate_satellites(self):
        """Migrate satellite data"""
        logger.info("Migrating satellites...")
        satellites_dir = self.data_dir / "Satellites"
        
        if not satellites_dir.exists():
            logger.warning("Satellites directory not found")
            return
        
        # Process each satellite file
        for satellite_file in satellites_dir.glob("*.json"):
            if satellite_file.name == "index.json":
                continue
            
            satellite_name = satellite_file.stem
            self._migrate_satellite(satellite_name)
    
    def _migrate_satellite(self, satellite_name: str):
        """Migrate a single satellite"""
        satellite_file = self.data_dir / "Satellites" / f"{satellite_name}.json"
        
        try:
            with open(satellite_file, 'r') as f:
                satellite_data = json.load(f)
            
            with get_db() as session:
                # Create celestial body
                celestial_body = self._create_celestial_body(
                    session, satellite_data, "satellite", None
                )
                
                # Create spacecraft mission
                if celestial_body:
                    self._create_spacecraft_mission(session, celestial_body, satellite_data)
                
                session.commit()
                self.migration_stats["celestial_bodies"] += 1
                
        except Exception as e:
            logger.error(f"Error migrating satellite {satellite_name}: {e}")
            self.migration_stats["errors"].append(f"Satellite {satellite_name}: {e}")
    
    def _create_celestial_body(self, session, data: Dict[str, Any], body_type: str, parent_id: Optional[str]) -> Optional[CelestialBody]:
        """Create a celestial body record"""
        try:
            # Extract basic properties
            name = data.get('name', 'Unknown')
            subtype = data.get('type', '')
            
            # Extract mass
            mass_kg = None
            if 'mass' in data:
                mass_data = data['mass']
                if isinstance(mass_data, dict):
                    mass_kg = mass_data.get('value')
                else:
                    mass_kg = mass_data
            
            # Extract radius/diameter
            radius_km = None
            if 'radius' in data:
                radius_data = data['radius']
                if isinstance(radius_data, dict):
                    radius_km = radius_data.get('value')
                else:
                    radius_km = radius_data
            elif 'diameter' in data:
                diameter_data = data['diameter']
                if isinstance(diameter_data, dict):
                    radius_km = diameter_data.get('value', 0) / 2
                else:
                    radius_km = diameter_data / 2
            
            # Extract surface gravity
            surface_gravity_ms2 = None
            if 'gravity' in data:
                gravity_data = data['gravity']
                if isinstance(gravity_data, dict):
                    surface_gravity_ms2 = gravity_data.get('value')
                else:
                    surface_gravity_ms2 = gravity_data
            
            # Create celestial body
            celestial_body = CelestialBody(
                name=name,
                type=body_type,
                subtype=subtype,
                parent_id=parent_id,
                mass_kg=mass_kg,
                radius_km=radius_km,
                surface_gravity_ms2=surface_gravity_ms2,
                discovery_date=data.get('discovery', {}).get('date') if isinstance(data.get('discovery'), dict) else data.get('discovery'),
                discoverer=data.get('discovery', {}).get('discoverer') if isinstance(data.get('discovery'), dict) else None,
                discovery_method=data.get('discovery', {}).get('method') if isinstance(data.get('discovery'), dict) else None,
                data_quality=data.get('metadata', {}).get('dataQuality', 'unknown') if isinstance(data.get('metadata'), dict) else 'unknown',
                data_sources=data.get('dataSources', {})
            )
            
            session.add(celestial_body)
            session.flush()  # Get the ID
            
            return celestial_body
            
        except Exception as e:
            logger.error(f"Error creating celestial body: {e}")
            return None
    
    def _create_orbital_parameters(self, session, celestial_body: CelestialBody, data: Dict[str, Any]):
        """Create orbital parameters record"""
        try:
            orbit_data = data.get('orbit', {})
            
            # Extract orbital elements
            semi_major_axis_km = None
            if 'semiMajorAxis' in orbit_data:
                axis_data = orbit_data['semiMajorAxis']
                if isinstance(axis_data, dict):
                    value = axis_data.get('value', 0)
                    unit = axis_data.get('unit', 'km')
                    if unit == 'AU':
                        semi_major_axis_km = value * 149597870.7  # Convert AU to km
                    else:
                        semi_major_axis_km = value
                else:
                    semi_major_axis_km = axis_data
            
            # Extract other orbital parameters
            orbital_period_days = None
            if 'orbitalPeriod' in orbit_data:
                period_data = orbit_data['orbitalPeriod']
                if isinstance(period_data, dict):
                    orbital_period_days = period_data.get('value')
                else:
                    orbital_period_days = period_data
            
            orbital_speed_kms = None
            if 'orbitalSpeed' in orbit_data:
                speed_data = orbit_data['orbitalSpeed']
                if isinstance(speed_data, dict):
                    orbital_speed_kms = speed_data.get('value')
                else:
                    orbital_speed_kms = speed_data
            
            # Create orbital parameters
            orbital_params = OrbitalParameters(
                celestial_body_id=celestial_body.id,
                semi_major_axis_km=semi_major_axis_km,
                eccentricity=orbit_data.get('eccentricity'),
                inclination_degrees=orbit_data.get('inclination', {}).get('value') if isinstance(orbit_data.get('inclination'), dict) else orbit_data.get('inclination'),
                longitude_ascending_node_degrees=orbit_data.get('longitudeOfAscendingNode', {}).get('value') if isinstance(orbit_data.get('longitudeOfAscendingNode'), dict) else orbit_data.get('longitudeOfAscendingNode'),
                argument_periapsis_degrees=orbit_data.get('argumentOfPeriapsis', {}).get('value') if isinstance(orbit_data.get('argumentOfPeriapsis'), dict) else orbit_data.get('argumentOfPeriapsis'),
                mean_anomaly_degrees=orbit_data.get('meanAnomaly', {}).get('value') if isinstance(orbit_data.get('meanAnomaly'), dict) else orbit_data.get('meanAnomaly'),
                orbital_period_days=orbital_period_days,
                orbital_speed_kms=orbital_speed_kms,
                epoch=orbit_data.get('epoch'),
                mutual_perturbations=orbit_data.get('mutualPerturbations', [])
            )
            
            session.add(orbital_params)
            self.migration_stats["orbital_parameters"] += 1
            
        except Exception as e:
            logger.error(f"Error creating orbital parameters: {e}")
    
    def _create_physical_characteristics(self, session, celestial_body: CelestialBody, data: Dict[str, Any]):
        """Create physical characteristics record"""
        try:
            # Extract temperature data
            surface_temperature_k = None
            if 'surfaceTemperature' in data:
                temp_data = data['surfaceTemperature']
                if isinstance(temp_data, dict):
                    # Convert Celsius to Kelvin if needed
                    temp_value = temp_data.get('value', 0)
                    if temp_data.get('unit') == '°C':
                        surface_temperature_k = temp_value + 273.15
                    else:
                        surface_temperature_k = temp_value
            
            # Extract atmospheric data
            has_atmosphere = False
            atmospheric_pressure_pa = None
            atmospheric_composition = None
            
            if 'atmosphere' in data:
                atm_data = data['atmosphere']
                if isinstance(atm_data, dict):
                    has_atmosphere = atm_data.get('present', True)
                    if 'pressure' in atm_data:
                        pressure_data = atm_data['pressure']
                        if isinstance(pressure_data, dict):
                            atmospheric_pressure_pa = pressure_data.get('value')
                        else:
                            atmospheric_pressure_pa = pressure_data
                    atmospheric_composition = atm_data.get('composition')
            
            # Create physical characteristics
            physical_chars = PhysicalCharacteristics(
                celestial_body_id=celestial_body.id,
                surface_temperature_k=surface_temperature_k,
                has_atmosphere=has_atmosphere,
                atmospheric_pressure_pa=atmospheric_pressure_pa,
                atmospheric_composition=atmospheric_composition,
                surface_type=data.get('surface', {}).get('type') if isinstance(data.get('surface'), dict) else None,
                has_rings=data.get('rings', {}).get('hasRings', False) if isinstance(data.get('rings'), dict) else False
            )
            
            session.add(physical_chars)
            self.migration_stats["physical_characteristics"] += 1
            
        except Exception as e:
            logger.error(f"Error creating physical characteristics: {e}")
    
    def _create_stellar_characteristics(self, session, celestial_body: CelestialBody, data: Dict[str, Any]):
        """Create stellar characteristics record"""
        try:
            stellar_data = data.get('stellarParameters', {})
            
            stellar_chars = StellarCharacteristics(
                celestial_body_id=celestial_body.id,
                spectral_type=stellar_data.get('spectralType'),
                luminosity_lsun=stellar_data.get('luminosity', {}).get('value') if isinstance(stellar_data.get('luminosity'), dict) else stellar_data.get('luminosity'),
                effective_temperature_k=stellar_data.get('effectiveTemperature', {}).get('value') if isinstance(stellar_data.get('effectiveTemperature'), dict) else stellar_data.get('effectiveTemperature'),
                absolute_magnitude=stellar_data.get('absoluteMagnitude', {}).get('value') if isinstance(stellar_data.get('absoluteMagnitude'), dict) else stellar_data.get('absoluteMagnitude'),
                apparent_magnitude=stellar_data.get('apparentMagnitude', {}).get('value') if isinstance(stellar_data.get('apparentMagnitude'), dict) else stellar_data.get('apparentMagnitude'),
                color_index_bv=stellar_data.get('colorIndex', {}).get('value') if isinstance(stellar_data.get('colorIndex'), dict) else stellar_data.get('colorIndex')
            )
            
            session.add(stellar_chars)
            self.migration_stats["stellar_characteristics"] += 1
            
        except Exception as e:
            logger.error(f"Error creating stellar characteristics: {e}")
    
    def _create_spacecraft_mission(self, session, celestial_body: CelestialBody, data: Dict[str, Any]):
        """Create spacecraft mission record"""
        try:
            mission_data = data.get('mission', {})
            
            mission = SpacecraftMission(
                celestial_body_id=celestial_body.id,
                mission_name=mission_data.get('name'),
                agency=mission_data.get('agency'),
                launch_date=mission_data.get('launchDate'),
                launch_site=mission_data.get('launchSite'),
                launch_vehicle=mission_data.get('launchVehicle'),
                status=mission_data.get('status'),
                mass_kg=mission_data.get('specifications', {}).get('mass') if isinstance(mission_data.get('specifications'), dict) else None,
                dimensions_m=mission_data.get('specifications', {}).get('dimensions') if isinstance(mission_data.get('specifications'), dict) else None,
                power_watts=mission_data.get('specifications', {}).get('power') if isinstance(mission_data.get('specifications'), dict) else None,
                payload=data.get('payload', []),
                ground_stations=data.get('groundStations', [])
            )
            
            session.add(mission)
            self.migration_stats["spacecraft_missions"] += 1
            
        except Exception as e:
            logger.error(f"Error creating spacecraft mission: {e}")
    
    def _get_celestial_body_id(self, name: str) -> Optional[str]:
        """Get celestial body ID by name"""
        if not name:
            return None
        
        try:
            with get_db() as session:
                body = session.query(CelestialBody).filter(CelestialBody.name == name).first()
                return str(body.id) if body else None
        except Exception as e:
            logger.error(f"Error getting celestial body ID for {name}: {e}")
            return None
    
    def _print_migration_stats(self):
        """Print migration statistics"""
        logger.info("=== Migration Statistics ===")
        for key, value in self.migration_stats.items():
            if key != "errors":
                logger.info(f"{key.replace('_', ' ').title()}: {value}")
        
        if self.migration_stats["errors"]:
            logger.warning(f"Errors encountered: {len(self.migration_stats['errors'])}")
            for error in self.migration_stats["errors"][:5]:  # Show first 5 errors
                logger.error(f"  - {error}")

def main():
    """Main migration function"""
    migrator = DataMigrator()
    migrator.migrate_all_data()

if __name__ == "__main__":
    main() 