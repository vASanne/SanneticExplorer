import json
import os
from pathlib import Path
from typing import Dict, Any, List
import jsonschema
from datetime import datetime

def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(data: Dict[str, Any], file_path: Path) -> None:
    """Save data to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def find_new_fields(template: Dict[str, Any], data: Dict[str, Any], path: str = "") -> List[str]:
    """Recursively find new fields in data that are not in template."""
    new_fields = []
    
    for key, value in data.items():
        current_path = f"{path}.{key}" if path else key
        
        if key not in template:
            new_fields.append(current_path)
        elif isinstance(value, dict) and isinstance(template[key], dict):
            new_fields.extend(find_new_fields(template[key], value, current_path))
        elif isinstance(value, list) and isinstance(template[key], list):
            # Check if list items are dictionaries
            if value and isinstance(value[0], dict) and template[key] and isinstance(template[key][0], dict):
                for item in value:
                    new_fields.extend(find_new_fields(template[key][0], item, f"{current_path}[0]"))
    
    return new_fields

def update_template(template: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    """Update template with new fields from data."""
    updated_template = template.copy()
    
    for key, value in data.items():
        if key not in updated_template:
            # Add new field with appropriate default value
            if isinstance(value, dict):
                updated_template[key] = {}
            elif isinstance(value, list):
                updated_template[key] = []
            else:
                updated_template[key] = "noValue"
        elif isinstance(value, dict) and isinstance(updated_template[key], dict):
            updated_template[key] = update_template(updated_template[key], value)
        elif isinstance(value, list) and isinstance(updated_template[key], list):
            if value and isinstance(value[0], dict) and updated_template[key] and isinstance(updated_template[key][0], dict):
                updated_template[key][0] = update_template(updated_template[key][0], value[0])
    
    return updated_template

def validate_data_against_template(data: Dict[str, Any], template: Dict[str, Any]) -> bool:
    """Validate data against template structure."""
    try:
        jsonschema.validate(instance=data, schema=template)
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"Validation error: {e}")
        return False

def process_directory(directory: Path) -> None:
    """Process all JSON files in a directory to update its template."""
    template_path = directory / ".template.json"
    if not template_path.exists():
        print(f"No template found in {directory}")
        return
    
    template = load_json_file(template_path)
    new_fields_found = False
    
    # Process all JSON files in the directory
    for file_path in directory.glob("*.json"):
        if file_path.name in [".template.json", "index.json"]:
            continue
            
        print(f"Processing {file_path.name}...")
        data = load_json_file(file_path)
        
        # Find new fields
        new_fields = find_new_fields(template, data)
        if new_fields:
            new_fields_found = True
            print(f"New fields found in {file_path.name}:")
            for field in new_fields:
                print(f"  - {field}")
            
            # Update template
            template = update_template(template, data)
    
    if new_fields_found:
        # Add metadata about the update
        if "metadata" not in template:
            template["metadata"] = {}
        template["metadata"]["lastUpdated"] = datetime.now().isoformat()
        template["metadata"]["version"] = template.get("metadata", {}).get("version", 0) + 1
        
        # Save updated template
        save_json_file(template, template_path)
        print(f"\nTemplate updated in {directory}")
    else:
        print(f"\nNo new fields found in {directory}")

def main():
    # Process each data directory
    data_dirs = [
        "Data/Planets",
        "Data/NaturalSatellites",
        "Data/Spacecraft",
        "Data/Stars"
    ]
    
    for directory in data_dirs:
        dir_path = Path(directory)
        if dir_path.exists():
            print(f"\nProcessing {directory}...")
            process_directory(dir_path)
        else:
            print(f"\nDirectory {directory} not found")

if __name__ == "__main__":
    main() 