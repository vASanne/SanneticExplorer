#!/usr/bin/env python3
"""
Solar System Data Synchronization Script
Imports celestial body data from JSON files into PostgreSQL database
"""

import os
import sys
import json
import glob
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

# Add the parent directory to Python path to import models and database
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (
    CelestialBody, OrbitalParameters, PhysicalCharacteristics,
    StellarCharacteristics, SpacecraftMission, TLEElements,
    ExplorationHistory, SimulationState
)
from database import get_db, init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SolarSystemDataSync:
    """Handles synchronization of solar system data from JSON files to PostgreSQL"""
    
    def __init__(self, data_dir: str = "Data"):
        self.data_dir = Path(data_dir)
        self.stats = {
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "categories": {}
        }
        
        # Category to celestial body type mapping
        self.category_mapping = {
            "Planets": "planet",
            "Stars": "star", 
            "NaturalSatellites": "moon",
            "Satellites": "satellite",
            "Spacecraft": "spacecraft",
            "Asteroids": "asteroid",
            "Comets": "comet"
        }
        
        # Field mappings for different data structures
        self.field_mappings = {
            "mass": {
                "json_path": ["mass", "value"],
                "unit_conversion": {"kg": 1.0, "g": 0.001, "M⊕": 5.972e24}
            },
            "radius": {
                "json_path": ["radius", "value"],
                "unit_conversion": {"km": 1.0, "m": 0.001, "R⊕": 6371.0}
            },
            "diameter": {
                "json_path": ["diameter", "value"],
                "unit_conversion": {"km": 1.0, "m": 0.001},
                "to_radius": True  # Convert diameter to radius
            },
            "surface_gravity": {
                "json_path": ["gravity", "value"],
                "unit_conversion": {"m/s²": 1.0, "g": 9.81}
            },
            "escape_velocity": {
                "json_path": ["escapeVelocity", "value"],
                "unit_conversion": {"km/s": 1.0, "m/s": 0.001}
            }
        }
    
    def run_sync(self, update_existing: bool = True) -> Dict[str, Any]:
        """Main synchronization method"""
        logger.info("Starting solar system data synchronization...")
        
        # Initialize database
        try:
            init_database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return {"error": str(e)}
        
        # Scan all categories
        categories = self._scan_categories()
        logger.info(f"Found {len(categories)} data categories: {list(categories.keys())}")
        
        # Process each category
        for category, category_path in categories.items():
            logger.info(f"Processing category: {category}")
            self._process_category(category, category_path, update_existing)
        
        # Print final statistics
        self._print_statistics()
        
        return self.stats
    
    def _scan_categories(self) -> Dict[str, Path]:
        """Scan data directory for categories"""
        categories = {}
        
        if not self.data_dir.exists():
            logger.error(f"Data directory not found: {self.data_dir}")
            return categories
        
        for item in self.data_dir.iterdir():
            if item.is_dir() and item.name in self.category_mapping:
                categories[item.name] = item
        
        return categories
    
    def _process_category(self, category: str, category_path: Path, update_existing: bool):
        """Process a single category of celestial bodies"""
        try:
            # Load template for this category
            template = self._load_template(category_path)
            
            # Get all data files
            data_files = self._get_data_files(category_path)
            logger.info(f"Found {len(data_files)} data files in {category}")
            
            # Process each file
            for data_file in data_files:
                self._process_data_file(category, data_file, template, update_existing)
                
        except Exception as e:
            logger.error(f"Error processing category {category}: {e}")
            self.stats["errors"] += 1
    
    def _load_template(self, category_path: Path) -> Dict[str, Any]:
        """Load template.json for a category"""
        template_file = category_path / "template.json"
        
        if template_file.exists():
            try:
                with open(template_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load template for {category_path.name}: {e}")
        
        return {}
    
    def _get_data_files(self, category_path: Path) -> List[Path]:
        """Get all data files in a category directory"""
        data_files = []
        
        # Look for JSON files (excluding index.json and template.json)
        for pattern in ["*.json", "*.JSON"]:
            files = category_path.glob(pattern)
            for file in files:
                if file.name not in ["index.json", "template.json"]:
                    data_files.append(file)
        
        # Look for CSV files
        for pattern in ["*.csv", "*.CSV"]:
            files = category_path.glob(pattern)
            data_files.extend(files)
        
        return sorted(data_files)
    
    def _process_data_file(self, category: str, data_file: Path, template: Dict[str, Any], update_existing: bool):
        """Process a single data file"""
        try:
            # Load data based on file type
            if data_file.suffix.lower() == '.json':
                data = self._load_json_data(data_file)
            elif data_file.suffix.lower() == '.csv':
                data = self._load_csv_data(data_file)
            else:
                logger.warning(f"Unsupported file type: {data_file}")
                return
            
            if not data:
                logger.warning(f"No data found in {data_file}")
                return
            
            # Process the data
            if isinstance(data, list):
                for item in data:
                    self._process_celestial_body(category, item, template, update_existing)
            else:
                self._process_celestial_body(category, data, template, update_existing)
                
        except Exception as e:
            logger.error(f"Error processing file {data_file}: {e}")
            self.stats["errors"] += 1
    
    def _load_json_data(self, file_path: Path) -> Any:
        """Load JSON data from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON file {file_path}: {e}")
            return None
    
    def _load_csv_data(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load CSV data from file"""
        try:
            df = pd.read_csv(file_path)
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Failed to load CSV file {file_path}: {e}")
            return []
    
    def _process_celestial_body(self, category: str, data: Dict[str, Any], template: Dict[str, Any], update_existing: bool):
        """Process a single celestial body"""
        try:
            # Extract basic information
            name = data.get('name', 'Unknown')
            external_id = data.get('id') or data.get('external_id') or name
            
            # Get celestial body type
            body_type = self.category_mapping.get(category, "unknown")
            
            # Check if celestial body already exists
            with get_db() as session:
                existing_body = self._find_existing_body(session, external_id, name)
                
                if existing_body:
                    if update_existing:
                        # Update existing body
                        self._update_celestial_body(session, existing_body, data, template)
                        self.stats["updated"] += 1
                        logger.debug(f"Updated: {name}")
                    else:
                        self.stats["skipped"] += 1
                        logger.debug(f"Skipped (exists): {name}")
                else:
                    # Create new body
                    self._create_celestial_body(session, category, data, template, external_id)
                    self.stats["inserted"] += 1
                    logger.debug(f"Inserted: {name}")
                
                # Update category statistics
                if category not in self.stats["categories"]:
                    self.stats["categories"][category] = {"inserted": 0, "updated": 0, "skipped": 0}
                
                if existing_body and update_existing:
                    self.stats["categories"][category]["updated"] += 1
                elif not existing_body:
                    self.stats["categories"][category]["inserted"] += 1
                else:
                    self.stats["categories"][category]["skipped"] += 1
                    
        except Exception as e:
            logger.error(f"Error processing celestial body {data.get('name', 'Unknown')}: {e}")
            self.stats["errors"] += 1
    
    def _find_existing_body(self, session: Session, external_id: str, name: str) -> Optional[CelestialBody]:
        """Find existing celestial body by external_id or name"""
        # Try to find by external_id first
        if external_id:
            body = session.query(CelestialBody).filter(
                or_(
                    CelestialBody.name == external_id,
                    CelestialBody.alternative_names.contains([external_id])
                )
            ).first()
            if body:
                return body
        
        # Try to find by name
        body = session.query(CelestialBody).filter(CelestialBody.name == name).first()
        return body
    
    def _create_celestial_body(self, session: Session, category: str, data: Dict[str, Any], template: Dict[str, Any], external_id: str):
        """Create a new celestial body"""
        # Extract basic properties
        name = data.get('name', 'Unknown')
        body_type = self.category_mapping.get(category, "unknown")
        
        # Extract subtype
        subtype = data.get('type') or data.get('subtype')
        
        # Extract parent information
        parent_id = None
        parent_name = data.get('parentBody') or data.get('planet') or data.get('parent')
        if parent_name:
            parent = session.query(CelestialBody).filter(CelestialBody.name == parent_name).first()
            if parent:
                parent_id = parent.id
        
        # Extract physical properties
        mass_kg = self._extract_numeric_value(data, "mass")
        radius_km = self._extract_numeric_value(data, "radius")
        if not radius_km:
            radius_km = self._extract_numeric_value(data, "diameter", to_radius=True)
        
        surface_gravity_ms2 = self._extract_numeric_value(data, "surface_gravity")
        escape_velocity_kms = self._extract_numeric_value(data, "escape_velocity")
        
        # Extract discovery information
        discovery_info = data.get('discovery', {})
        if isinstance(discovery_info, dict):
            discovery_date = discovery_info.get('date')
            discoverer = discovery_info.get('discoverer')
            discovery_method = discovery_info.get('method')
        else:
            discovery_date = discovery_info
            discoverer = None
            discovery_method = None
        
        # Create celestial body
        celestial_body = CelestialBody(
            name=name,
            type=body_type,
            subtype=subtype,
            parent_id=parent_id,
            mass_kg=mass_kg,
            radius_km=radius_km,
            surface_gravity_ms2=surface_gravity_ms2,
            escape_velocity_kms=escape_velocity_kms,
            discovery_date=discovery_date,
            discoverer=discoverer,
            discovery_method=discovery_method,
            data_quality=data.get('metadata', {}).get('dataQuality', 'unknown'),
            data_sources=data.get('dataSources', {})
        )
        
        session.add(celestial_body)
        session.flush()  # Get the ID
        
        # Create related records
        self._create_orbital_parameters(session, celestial_body, data)
        self._create_physical_characteristics(session, celestial_body, data)
        
        if body_type == "star":
            self._create_stellar_characteristics(session, celestial_body, data)
        
        if body_type in ["satellite", "spacecraft"]:
            self._create_spacecraft_mission(session, celestial_body, data)
    
    def _update_celestial_body(self, session: Session, celestial_body: CelestialBody, data: Dict[str, Any], template: Dict[str, Any]):
        """Update existing celestial body"""
        # Update basic properties if they've changed
        name = data.get('name')
        if name and name != celestial_body.name:
            celestial_body.name = name
        
        subtype = data.get('type') or data.get('subtype')
        if subtype and subtype != celestial_body.subtype:
            celestial_body.subtype = subtype
        
        # Update physical properties
        mass_kg = self._extract_numeric_value(data, "mass")
        if mass_kg is not None and mass_kg != celestial_body.mass_kg:
            celestial_body.mass_kg = mass_kg
        
        radius_km = self._extract_numeric_value(data, "radius")
        if not radius_km:
            radius_km = self._extract_numeric_value(data, "diameter", to_radius=True)
        if radius_km is not None and radius_km != celestial_body.radius_km:
            celestial_body.radius_km = radius_km
        
        # Update data quality and sources
        data_quality = data.get('metadata', {}).get('dataQuality')
        if data_quality and data_quality != celestial_body.data_quality:
            celestial_body.data_quality = data_quality
        
        data_sources = data.get('dataSources')
        if data_sources and data_sources != celestial_body.data_sources:
            celestial_body.data_sources = data_sources
        
        # Update related records
        self._update_orbital_parameters(session, celestial_body, data)
        self._update_physical_characteristics(session, celestial_body, data)
        
        if celestial_body.type == "star":
            self._update_stellar_characteristics(session, celestial_body, data)
        
        if celestial_body.type in ["satellite", "spacecraft"]:
            self._update_spacecraft_mission(session, celestial_body, data)
    
    def _extract_numeric_value(self, data: Dict[str, Any], field_name: str, to_radius: bool = False) -> Optional[float]:
        """Extract numeric value from nested JSON structure"""
        mapping = self.field_mappings.get(field_name, {})
        json_path = mapping.get("json_path", [field_name])
        unit_conversion = mapping.get("unit_conversion", {})
        
        # Navigate through JSON path
        value = data
        for key in json_path:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        if value is None or value == "noValue":
            return None
        
        try:
            # Convert to float
            numeric_value = float(value)
            
            # Apply unit conversion if needed
            if unit_conversion:
                # Try to find unit in the data
                unit = None
                for key in json_path[:-1]:  # Check parent objects for unit
                    if isinstance(data.get(key), dict):
                        unit = data[key].get("unit")
                        if unit:
                            break
                
                if unit and unit in unit_conversion:
                    numeric_value *= unit_conversion[unit]
            
            # Convert diameter to radius if needed
            if to_radius:
                numeric_value /= 2.0
            
            return numeric_value
            
        except (ValueError, TypeError):
            return None
    
    def _create_orbital_parameters(self, session: Session, celestial_body: CelestialBody, data: Dict[str, Any]):
        """Create orbital parameters record"""
        try:
            orbit_data = data.get('orbit', {})
            
            # Extract orbital elements
            semi_major_axis_km = self._extract_orbital_value(orbit_data, "semiMajorAxis")
            eccentricity = orbit_data.get('eccentricity')
            inclination_degrees = self._extract_orbital_value(orbit_data, "inclination")
            
            # Extract periods
            orbital_period_days = self._extract_orbital_value(orbit_data, "orbitalPeriod")
            orbital_speed_kms = self._extract_orbital_value(orbit_data, "orbitalSpeed")
            
            # Extract rotation
            rotation_period_hours = self._extract_orbital_value(orbit_data, "rotationPeriod", to_hours=True)
            
            # Create orbital parameters
            orbital_params = OrbitalParameters(
                celestial_body_id=celestial_body.id,
                semi_major_axis_km=semi_major_axis_km,
                eccentricity=eccentricity,
                inclination_degrees=inclination_degrees,
                orbital_period_days=orbital_period_days,
                orbital_speed_kms=orbital_speed_kms,
                rotation_period_hours=rotation_period_hours,
                epoch=orbit_data.get('epoch'),
                mutual_perturbations=orbit_data.get('mutualPerturbations', [])
            )
            
            session.add(orbital_params)
            
        except Exception as e:
            logger.warning(f"Failed to create orbital parameters for {celestial_body.name}: {e}")
    
    def _update_orbital_parameters(self, session: Session, celestial_body: CelestialBody, data: Dict[str, Any]):
        """Update orbital parameters record"""
        try:
            orbital_params = session.query(OrbitalParameters).filter(
                OrbitalParameters.celestial_body_id == celestial_body.id
            ).first()
            
            if orbital_params:
                orbit_data = data.get('orbit', {})
                
                # Update values if they exist and are different
                semi_major_axis_km = self._extract_orbital_value(orbit_data, "semiMajorAxis")
                if semi_major_axis_km is not None:
                    orbital_params.semi_major_axis_km = semi_major_axis_km
                
                eccentricity = orbit_data.get('eccentricity')
                if eccentricity is not None:
                    orbital_params.eccentricity = eccentricity
                
                # Update other fields as needed
                
        except Exception as e:
            logger.warning(f"Failed to update orbital parameters for {celestial_body.name}: {e}")
    
    def _extract_orbital_value(self, orbit_data: Dict[str, Any], field_name: str, to_hours: bool = False) -> Optional[float]:
        """Extract orbital value from orbit data"""
        value_data = orbit_data.get(field_name)
        
        if isinstance(value_data, dict):
            value = value_data.get('value')
            unit = value_data.get('unit', '')
        else:
            value = value_data
            unit = ''
        
        if value is None or value == "noValue":
            return None
        
        try:
            numeric_value = float(value)
            
            # Apply unit conversions
            if to_hours and unit == 'days':
                numeric_value *= 24.0
            elif field_name == "semiMajorAxis" and unit == 'AU':
                numeric_value *= 149597870.7  # Convert AU to km
            
            return numeric_value
            
        except (ValueError, TypeError):
            return None
    
    def _create_physical_characteristics(self, session: Session, celestial_body: CelestialBody, data: Dict[str, Any]):
        """Create physical characteristics record"""
        try:
            # Extract temperature data
            surface_temperature_k = self._extract_temperature(data, "surfaceTemperature")
            
            # Extract atmospheric data
            atmosphere_data = data.get('atmosphere', {})
            has_atmosphere = atmosphere_data.get('present', True)
            atmospheric_pressure_pa = self._extract_atmospheric_pressure(atmosphere_data)
            atmospheric_composition = atmosphere_data.get('composition')
            
            # Extract surface data
            surface_data = data.get('surface', {})
            surface_type = surface_data.get('type')
            surface_features = surface_data.get('features', [])
            
            # Extract ring data
            rings_data = data.get('rings', {})
            has_rings = rings_data.get('hasRings', False)
            
            # Create physical characteristics
            physical_chars = PhysicalCharacteristics(
                celestial_body_id=celestial_body.id,
                surface_temperature_k=surface_temperature_k,
                has_atmosphere=has_atmosphere,
                atmospheric_pressure_pa=atmospheric_pressure_pa,
                atmospheric_composition=atmospheric_composition,
                surface_type=surface_type,
                surface_features=surface_features,
                has_rings=has_rings
            )
            
            session.add(physical_chars)
            
        except Exception as e:
            logger.warning(f"Failed to create physical characteristics for {celestial_body.name}: {e}")
    
    def _update_physical_characteristics(self, session: Session, celestial_body: CelestialBody, data: Dict[str, Any]):
        """Update physical characteristics record"""
        try:
            physical_chars = session.query(PhysicalCharacteristics).filter(
                PhysicalCharacteristics.celestial_body_id == celestial_body.id
            ).first()
            
            if physical_chars:
                # Update temperature
                surface_temperature_k = self._extract_temperature(data, "surfaceTemperature")
                if surface_temperature_k is not None:
                    physical_chars.surface_temperature_k = surface_temperature_k
                
                # Update other fields as needed
                
        except Exception as e:
            logger.warning(f"Failed to update physical characteristics for {celestial_body.name}: {e}")
    
    def _extract_temperature(self, data: Dict[str, Any], field_name: str) -> Optional[float]:
        """Extract temperature value and convert to Kelvin"""
        temp_data = data.get(field_name, {})
        
        if isinstance(temp_data, dict):
            # Try to get average temperature first
            value = temp_data.get('average', {}).get('value')
            unit = temp_data.get('average', {}).get('unit', 'K')
            
            # If no average, try min/max
            if value is None:
                min_temp = temp_data.get('min', {}).get('value')
                max_temp = temp_data.get('max', {}).get('value')
                if min_temp is not None and max_temp is not None:
                    value = (float(min_temp) + float(max_temp)) / 2
                    unit = temp_data.get('min', {}).get('unit', 'K')
        else:
            value = temp_data
            unit = 'K'
        
        if value is None or value == "noValue":
            return None
        
        try:
            numeric_value = float(value)
            
            # Convert to Kelvin
            if unit == '°C' or unit == 'C':
                numeric_value += 273.15
            elif unit == '°F' or unit == 'F':
                numeric_value = (numeric_value - 32) * 5/9 + 273.15
            
            return numeric_value
            
        except (ValueError, TypeError):
            return None
    
    def _extract_atmospheric_pressure(self, atmosphere_data: Dict[str, Any]) -> Optional[float]:
        """Extract atmospheric pressure value"""
        pressure_data = atmosphere_data.get('pressure', {})
        
        if isinstance(pressure_data, dict):
            value = pressure_data.get('value')
            unit = pressure_data.get('unit', 'Pa')
        else:
            value = pressure_data
            unit = 'Pa'
        
        if value is None or value == "noValue":
            return None
        
        try:
            numeric_value = float(value)
            
            # Convert to Pa if needed
            if unit == 'bar':
                numeric_value *= 100000
            elif unit == 'atm':
                numeric_value *= 101325
            
            return numeric_value
            
        except (ValueError, TypeError):
            return None
    
    def _create_stellar_characteristics(self, session: Session, celestial_body: CelestialBody, data: Dict[str, Any]):
        """Create stellar characteristics record"""
        try:
            stellar_data = data.get('stellarParameters', {})
            
            stellar_chars = StellarCharacteristics(
                celestial_body_id=celestial_body.id,
                spectral_type=stellar_data.get('spectralType'),
                luminosity_lsun=stellar_data.get('luminosity', {}).get('value'),
                effective_temperature_k=stellar_data.get('effectiveTemperature', {}).get('value'),
                absolute_magnitude=stellar_data.get('absoluteMagnitude', {}).get('value'),
                apparent_magnitude=stellar_data.get('apparentMagnitude', {}).get('value')
            )
            
            session.add(stellar_chars)
            
        except Exception as e:
            logger.warning(f"Failed to create stellar characteristics for {celestial_body.name}: {e}")
    
    def _update_stellar_characteristics(self, session: Session, celestial_body: CelestialBody, data: Dict[str, Any]):
        """Update stellar characteristics record"""
        try:
            stellar_chars = session.query(StellarCharacteristics).filter(
                StellarCharacteristics.celestial_body_id == celestial_body.id
            ).first()
            
            if stellar_chars:
                stellar_data = data.get('stellarParameters', {})
                
                # Update fields as needed
                spectral_type = stellar_data.get('spectralType')
                if spectral_type:
                    stellar_chars.spectral_type = spectral_type
                
        except Exception as e:
            logger.warning(f"Failed to update stellar characteristics for {celestial_body.name}: {e}")
    
    def _create_spacecraft_mission(self, session: Session, celestial_body: CelestialBody, data: Dict[str, Any]):
        """Create spacecraft mission record"""
        try:
            mission_data = data.get('mission', {})
            
            mission = SpacecraftMission(
                celestial_body_id=celestial_body.id,
                mission_name=mission_data.get('name'),
                agency=mission_data.get('agency'),
                status=mission_data.get('status'),
                payload=data.get('payload', []),
                ground_stations=data.get('groundStations', [])
            )
            
            session.add(mission)
            
        except Exception as e:
            logger.warning(f"Failed to create spacecraft mission for {celestial_body.name}: {e}")
    
    def _update_spacecraft_mission(self, session: Session, celestial_body: CelestialBody, data: Dict[str, Any]):
        """Update spacecraft mission record"""
        try:
            mission = session.query(SpacecraftMission).filter(
                SpacecraftMission.celestial_body_id == celestial_body.id
            ).first()
            
            if mission:
                mission_data = data.get('mission', {})
                
                # Update fields as needed
                status = mission_data.get('status')
                if status:
                    mission.status = status
                
        except Exception as e:
            logger.warning(f"Failed to update spacecraft mission for {celestial_body.name}: {e}")
    
    def _print_statistics(self):
        """Print synchronization statistics"""
        logger.info("=" * 60)
        logger.info("SYNCHRONIZATION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total inserted: {self.stats['inserted']}")
        logger.info(f"Total updated: {self.stats['updated']}")
        logger.info(f"Total skipped: {self.stats['skipped']}")
        logger.info(f"Total errors: {self.stats['errors']}")
        logger.info("")
        
        logger.info("By Category:")
        for category, stats in self.stats["categories"].items():
            logger.info(f"  {category}:")
            logger.info(f"    Inserted: {stats['inserted']}")
            logger.info(f"    Updated: {stats['updated']}")
            logger.info(f"    Skipped: {stats['skipped']}")
        logger.info("=" * 60)

def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description="Solar System Data Synchronization")
    parser.add_argument("command", choices=["update", "sync"], help="Command to execute")
    parser.add_argument("--data-dir", default="Data", help="Data directory path")
    parser.add_argument("--no-update", action="store_true", help="Skip updating existing records")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create sync instance
    sync = SolarSystemDataSync(data_dir=args.data_dir)
    
    # Run synchronization
    if args.command in ["update", "sync"]:
        update_existing = not args.no_update
        stats = sync.run_sync(update_existing=update_existing)
        
        if "error" in stats:
            logger.error(f"Synchronization failed: {stats['error']}")
            sys.exit(1)
        else:
            logger.info("Synchronization completed successfully")
    else:
        logger.error(f"Unknown command: {args.command}")
        sys.exit(1)

if __name__ == "__main__":
    main() 