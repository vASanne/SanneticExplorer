#!/usr/bin/env python3
"""
Script to fix structure errors in JSON files by adding missing required fields.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

def add_missing_fields(data: Dict[str, Any], required_structure: Dict[str, Any]) -> Dict[str, Any]:
    """Add missing fields from required structure to data."""
    for key, value in required_structure.items():
        if key not in data:
            data[key] = value
        elif isinstance(value, dict) and isinstance(data[key], dict):
            data[key] = add_missing_fields(data[key], value)
    return data

def fix_natural_satellite_file(file_path: Path) -> bool:
    """Fix a natural satellite JSON file by adding missing required fields."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Required structure for natural satellites
        required_structure = {
            'physicalCharacteristics': {
                'radius': {'value': 'noValue', 'unit': 'km'},
                'mass': {'value': 'noValue', 'unit': 'kg'},
                'density': {'value': 'noValue', 'unit': 'g/cm³'},
                'gravity': {'value': 'noValue', 'unit': 'm/s²'},
                'escapeVelocity': {'value': 'noValue', 'unit': 'km/s'}
            },
            'orbitalParameters': {
                'semiMajorAxis': {'value': 'noValue', 'unit': 'km'},
                'eccentricity': 'noValue',
                'inclination': {'value': 'noValue', 'unit': 'degrees'},
                'orbitalPeriod': {'value': 'noValue', 'unit': 'days'}
            },
            'surface': {
                'type': 'noValue',
                'features': ['noValue'],
                'albedo': {'value': 'noValue', 'unit': 'noValue'},
                'temperature': {
                    'min': {'value': 'noValue', 'unit': 'K'},
                    'max': {'value': 'noValue', 'unit': 'K'},
                    'average': {'value': 'noValue', 'unit': 'K'}
                }
            },
            'atmosphere': {
                'present': False,
                'composition': [],
                'pressure': {'value': 'noValue', 'unit': 'Pa'}
            },
            'magneticField': {
                'present': False,
                'strength': {'value': 'noValue', 'unit': 'T'},
                'dipoleMoment': {'value': 'noValue', 'unit': 'T·m³'}
            },
            'internalStructure': {
                'core': {
                    'radius': {'value': 'noValue', 'unit': 'km'},
                    'composition': 'noValue'
                },
                'mantle': {
                    'thickness': {'value': 'noValue', 'unit': 'km'},
                    'composition': 'noValue'
                }
            },
            'exploration': {
                'firstFlyby': 'noValue',
                'firstOrbiter': 'noValue',
                'firstLander': 'noValue'
            },
            'scientificSignificance': 'noValue',
            'historicalSignificance': 'noValue',
            'metadata': {
                'lastUpdated': '2024-01-01',
                'dataQuality': 'incomplete',
                'sources': []
            }
        }
        
        # Add missing fields
        data = add_missing_fields(data, required_structure)
        
        # Save the updated file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"✓ Fixed: {file_path.name}")
        return True
        
    except Exception as e:
        print(f"✗ Error fixing {file_path.name}: {e}")
        return False

def main():
    """Main function to fix structure errors in all JSON files."""
    print("Fixing structure errors in JSON files...")
    
    # Fix Natural Satellites
    print("\n--- Fixing Natural Satellites ---")
    natural_satellites_dir = Path("Data/NaturalSatellites")
    fixed_count = 0
    total_count = 0
    
    for json_file in natural_satellites_dir.glob("*.json"):
        if json_file.name not in ['index.json', '.template.json']:
            total_count += 1
            if fix_natural_satellite_file(json_file):
                fixed_count += 1
    
    print(f"\nNatural Satellites: Fixed {fixed_count}/{total_count} files")
    
    print("\nStructure fixes completed!")
    print("You can now run validation again to see the improvements.")

if __name__ == "__main__":
    main() 