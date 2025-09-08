#!/usr/bin/env python3
"""
Simple script to update planet data from JSON files with only essential fields
"""

import json
import os
import psycopg2
from typing import Dict, Any, Optional

# Database connection parameters
DB_CONFIG = {
    'host': 'db',
    'port': 5432,
    'database': 'sannetic_explorer',
    'user': 'postgres',
    'password': 'postgres'
}

def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Load JSON data from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def update_planet_from_json(cursor, json_data: Dict[str, Any]):
    """Update planet data from JSON"""
    planet_name = json_data.get('name')
    if not planet_name:
        return False
    
    print(f"Updating {planet_name}...")
    
    # Get planet ID
    cursor.execute("SELECT id FROM celestial_bodies WHERE name = %s", (planet_name,))
    result = cursor.fetchone()
    
    if not result:
        print(f"  Planet {planet_name} not found in database")
        return False
    
    planet_id = result[0]
    
    # Update basic data
    updates = []
    values = []
    
    # Mass
    if 'mass' in json_data and isinstance(json_data['mass'], dict):
        mass_value = json_data['mass'].get('value')
        if mass_value:
            updates.append("mass_kg = %s")
            values.append(mass_value)
    
    # Radius (from diameter)
    if 'diameter' in json_data and isinstance(json_data['diameter'], dict):
        diameter = json_data['diameter'].get('value')
        if diameter:
            updates.append("radius_km = %s")
            values.append(diameter / 2)
    
    # Distance from sun
    if 'distanceFromSun' in json_data and isinstance(json_data['distanceFromSun'], dict):
        distance = json_data['distanceFromSun'].get('value')
        if distance:
            updates.append("mean_distance_au = %s")
            values.append(distance)
    
    # Gravity
    if 'gravity' in json_data and isinstance(json_data['gravity'], dict):
        gravity = json_data['gravity'].get('value')
        if gravity:
            updates.append("surface_gravity_ms2 = %s")
            values.append(gravity)
    
    # Update celestial body
    if updates:
        values.append(planet_id)
        cursor.execute(f"""
            UPDATE celestial_bodies 
            SET {', '.join(updates)}
            WHERE id = %s
        """, values)
    
    # Update orbital parameters
    orbital_updates = []
    orbital_values = []
    
    # Orbital period
    if 'orbitalPeriod' in json_data and isinstance(json_data['orbitalPeriod'], dict):
        period = json_data['orbitalPeriod'].get('value')
        if period:
            orbital_updates.append("orbital_period_days = %s")
            orbital_values.append(period)
    
    # Rotation period
    if 'rotationPeriod' in json_data and isinstance(json_data['rotationPeriod'], dict):
        rotation = json_data['rotationPeriod'].get('value')
        if rotation:
            # Convert days to hours
            orbital_updates.append("rotation_period_hours = %s")
            orbital_values.append(rotation * 24)
    
    # Orbital speed
    if 'orbit' in json_data and 'orbitalSpeed' in json_data['orbit']:
        orbit_speed = json_data['orbit']['orbitalSpeed']
        if isinstance(orbit_speed, dict):
            speed = orbit_speed.get('value')
            if speed:
                orbital_updates.append("orbital_speed_kms = %s")
                orbital_values.append(speed)
    
    # Eccentricity
    if 'orbit' in json_data and 'eccentricity' in json_data['orbit']:
        eccentricity = json_data['orbit'].get('eccentricity')
        if eccentricity is not None:
            orbital_updates.append("eccentricity = %s")
            orbital_values.append(eccentricity)
    
    # Inclination
    if 'orbit' in json_data and 'inclination' in json_data['orbit']:
        inclination = json_data['orbit']['inclination']
        if isinstance(inclination, dict):
            inc_value = inclination.get('value')
            if inc_value is not None:
                orbital_updates.append("inclination_degrees = %s")
                orbital_values.append(inc_value)
    
    # Update orbital parameters
    if orbital_updates:
        orbital_values.append(planet_id)
        cursor.execute(f"""
            UPDATE orbital_parameters 
            SET {', '.join(orbital_updates)}
            WHERE celestial_body_id = %s
        """, orbital_values)
    
    # Update physical characteristics
    physical_updates = []
    physical_values = []
    
    # Surface temperature
    if 'surfaceTemperature' in json_data:
        temp = json_data['surfaceTemperature']
        if isinstance(temp, dict):
            min_temp = temp.get('min')
            max_temp = temp.get('max')
            if min_temp is not None and max_temp is not None:
                # Convert Celsius to Kelvin
                min_k = min_temp + 273.15
                max_k = max_temp + 273.15
                avg_k = (min_temp + max_temp) / 2 + 273.15
                
                physical_updates.append("surface_temperature_k = %s")
                physical_values.append(avg_k)
                physical_updates.append("surface_temperature_min_k = %s")
                physical_values.append(min_k)
                physical_updates.append("surface_temperature_max_k = %s")
                physical_values.append(max_k)
    
    # Atmosphere
    if 'atmosphere' in json_data:
        atm = json_data['atmosphere']
        physical_updates.append("has_atmosphere = %s")
        physical_values.append(True)
        
        if 'composition' in atm:
            physical_updates.append("atmospheric_composition = %s")
            physical_values.append(json.dumps(atm['composition']))
        
        if 'pressure' in atm and isinstance(atm['pressure'], dict):
            pressure = atm['pressure'].get('value')
            if pressure and pressure != 'noValue':
                physical_updates.append("atmospheric_pressure_pa = %s")
                physical_values.append(pressure)
    
    # Rings
    if 'rings' in json_data:
        rings = json_data['rings']
        has_rings = rings.get('hasRings', False)
        physical_updates.append("has_rings = %s")
        physical_values.append(has_rings)
    
    # Update physical characteristics
    if physical_updates:
        physical_values.append(planet_id)
        cursor.execute(f"""
            UPDATE physical_characteristics 
            SET {', '.join(physical_updates)}
            WHERE celestial_body_id = %s
        """, physical_values)
    
    # Update moons in data_sources
    if 'moons' in json_data:
        moons = json_data['moons']
        if isinstance(moons, dict):
            moon_count = moons.get('count', 0)
            moon_names = moons.get('names', [])
            
            # Get current data_sources
            cursor.execute("SELECT data_sources FROM celestial_bodies WHERE id = %s", (planet_id,))
            result = cursor.fetchone()
            
            data_sources = result[0] if result and result[0] else {}
            if not isinstance(data_sources, dict):
                data_sources = {}
            
            # Update moons data
            data_sources['moons'] = moon_count
            data_sources['moon_names'] = moon_names
            
            # Update data_sources
            cursor.execute("UPDATE celestial_bodies SET data_sources = %s WHERE id = %s", 
                         (json.dumps(data_sources), planet_id))
    
    return True

def main():
    """Main function to update all planet data"""
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🪐 Updating planet data from JSON files...")
        
        # Get all JSON files in Data/Planets/
        data_dir = "/app/Data/Planets"
        planet_names = ['mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
        
        updated_count = 0
        for planet_name in planet_names:
            file_path = os.path.join(data_dir, f"{planet_name}.json")
            
            if os.path.exists(file_path):
                print(f"📄 Processing {planet_name}.json...")
                
                json_data = load_json_file(file_path)
                if json_data:
                    try:
                        if update_planet_from_json(cursor, json_data):
                            updated_count += 1
                            print(f"  ✅ Successfully updated {json_data.get('name', planet_name)}")
                        else:
                            print(f"  ❌ Failed to update {planet_name}")
                    except Exception as e:
                        print(f"  ❌ Error updating {planet_name}: {e}")
                        conn.rollback()
                        cursor = conn.cursor()
            else:
                print(f"📄 File not found: {planet_name}.json")
        
        # Commit changes
        conn.commit()
        print(f"\n🎯 Update complete: {updated_count}/{len(planet_names)} planets updated")
        
        # Verify updates
        print("\n🔍 Verifying updates...")
        cursor.execute("""
            SELECT cb.name, cb.mass_kg, cb.radius_km, pc.surface_temperature_k, 
                   op.orbital_period_days, cb.data_sources
            FROM celestial_bodies cb
            LEFT JOIN physical_characteristics pc ON cb.id = pc.celestial_body_id
            LEFT JOIN orbital_parameters op ON cb.id = op.celestial_body_id
            WHERE cb.type = 'planet'
            ORDER BY cb.mean_distance_au
        """)
        
        results = cursor.fetchall()
        for row in results:
            name, mass, radius, temp, period, data_sources = row
            moons = "N/A"
            if data_sources and isinstance(data_sources, dict) and 'moons' in data_sources:
                moons = str(data_sources['moons'])
            print(f"  {name}: Mass={mass}, Radius={radius}km, Temp={temp}K, Period={period}d, Moons={moons}")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
