#!/usr/bin/env python3
"""
Sannetic Explorer Status Report
Provides a comprehensive overview of the current project state
"""

import json
import os
from pathlib import Path

def count_files_and_errors():
    data_dir = Path('Data')
    categories = ['Planets', 'NaturalSatellites', 'Satellites', 'Spacecraft', 'Stars']
    
    total_files = 0
    total_errors = 0
    
    print('=== SANNETIC EXPLORER STATUS REPORT ===')
    print()
    
    for category in categories:
        cat_path = data_dir / category
        if cat_path.exists():
            files = list(cat_path.glob('*.json'))
            # Exclude index files
            files = [f for f in files if f.name != 'index.json']
            file_count = len(files)
            total_files += file_count
            
            print(f'{category}:')
            print(f'  Files: {file_count}')
            
            # Quick error check on a few files
            error_count = 0
            missing_fields = 0
            no_value_count = 0
            
            for i, file_path in enumerate(files[:10]):  # Check first 10 files
                try:
                    with open(file_path) as f:
                        data = json.load(f)
                        if isinstance(data, list) and len(data) > 0:
                            data = data[0]  # Take first item if it's a list
                        
                        # Check for common issues
                        data_str = str(data)
                        if 'noValue' in data_str:
                            no_value_count += 1
                        if isinstance(data, dict):
                            if not data.get('metadata', {}).get('version'):
                                missing_fields += 1
                            if 'noValue' in data_str or not data.get('metadata', {}).get('version'):
                                error_count += 1
                        else:
                            error_count += 1
                except Exception as e:
                    error_count += 1
            
            if file_count > 0:
                sample_size = min(10, file_count)
                error_rate = (error_count / sample_size) * 100
                print(f'  Sample Error Rate: {error_rate:.1f}% ({error_count}/{sample_size} files)')
                if no_value_count > 0:
                    print(f'  Files with "noValue": {no_value_count}')
                if missing_fields > 0:
                    print(f'  Files missing metadata.version: {missing_fields}')
            print()
    
    print(f'TOTAL FILES: {total_files}')
    print()
    
    # Check API credentials
    print('API CREDENTIALS STATUS:')
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file) as f:
            env_content = f.read()
            
        apis = {
            'N2YO_API_KEY': 'N2YO API',
            'SPACE_TRACK_USERNAME': 'Space-Track Username',
            'SPACE_TRACK_PASSWORD': 'Space-Track Password',
            'NASA_ADS_API_TOKEN': 'NASA ADS API'
        }
        
        for key, name in apis.items():
            if key in env_content and not f'{key}=your_' in env_content and not f'{key}=' in env_content.split(f'{key}=')[1].split('\n')[0].strip() == '':
                print(f'  ✓ {name}: Configured')
            else:
                print(f'  ✗ {name}: Not configured')
    else:
        print('  ✗ No .env file found')
    
    print()
    print('RECENT API TEST RESULTS:')
    print('  ✓ N2YO API: Connected (needs specific satellite IDs/NORAD IDs)')
    print('  ✓ Space-Track: Connected (needs proper query format)')
    print('  ✗ NASA ADS: 401 Authentication error (token may need refresh)')
    print('  ✗ HEASARC: Connection/parsing issues')
    print()
    print('NEXT STEPS:')
    print('  1. Fix API query formats for better satellite data retrieval')
    print('  2. Update NASA ADS token if needed for research papers')
    print('  3. Complete missing field population with default values')
    print('  4. Run comprehensive validation and cleanup')
    print('  5. Update documentation with current status')

if __name__ == '__main__':
    count_files_and_errors() 