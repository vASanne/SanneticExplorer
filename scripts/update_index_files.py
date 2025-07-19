import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd
import numpy as np

def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(data: Dict[str, Any], file_path: Path) -> None:
    """Save data to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def calculate_statistics(directory: Path, template: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate statistics about data completeness and quality."""
    stats = {
        "total_files": 0,
        "total_fields": 0,
        "filled_fields": 0,
        "missing_fields": 0,
        "completion_percentage": 0.0,
        "last_updated": datetime.now().isoformat(),
        "field_statistics": {}
    }
    
    def count_fields(data_dict: Dict[str, Any], template_dict: Dict[str, Any], path: str = "") -> tuple[int, int]:
        total = 0
        filled = 0
        
        for key, template_value in template_dict.items():
            current_path = f"{path}.{key}" if path else key
            total += 1
            
            if key in data_dict:
                data_value = data_dict[key]
                if isinstance(template_value, dict) and isinstance(data_value, dict):
                    t, f = count_fields(data_value, template_value, current_path)
                    total += t
                    filled += f
                elif isinstance(template_value, list) and isinstance(data_value, list):
                    if template_value and isinstance(template_value[0], dict):
                        for item in data_value:
                            t, f = count_fields(item, template_value[0], f"{current_path}[0]")
                            total += t
                            filled += f
                elif data_value != "noValue":
                    filled += 1
                    
                    # Track field statistics
                    if current_path not in stats["field_statistics"]:
                        stats["field_statistics"][current_path] = {
                            "total": 0,
                            "filled": 0,
                            "percentage": 0.0
                        }
                    stats["field_statistics"][current_path]["total"] += 1
                    stats["field_statistics"][current_path]["filled"] += 1
        
        return total, filled
    
    # Process all files in directory
    for file_path in directory.glob("*.json"):
        if file_path.name in [".template.json", "index.json"]:
            continue
            
        stats["total_files"] += 1
        data = load_json_file(file_path)
        total, filled = count_fields(data, template)
        stats["total_fields"] += total
        stats["filled_fields"] += filled
    
    # Calculate percentages
    stats["missing_fields"] = stats["total_fields"] - stats["filled_fields"]
    if stats["total_fields"] > 0:
        stats["completion_percentage"] = (stats["filled_fields"] / stats["total_fields"]) * 100
    
    # Calculate field statistics percentages
    for field in stats["field_statistics"]:
        field_stats = stats["field_statistics"][field]
        if field_stats["total"] > 0:
            field_stats["percentage"] = (field_stats["filled"] / field_stats["total"]) * 100
    
    return stats

def generate_index_content(directory: Path, template: Dict[str, Any]) -> Dict[str, Any]:
    """Generate the content for an index.json file."""
    index_content = {
        "metadata": {
            "lastUpdated": datetime.now().isoformat(),
            "directory": str(directory),
            "totalObjects": 0
        },
        "objects": [],
        "statistics": {}
    }
    
    # Get the object type from the directory name
    object_type = directory.name.lower()
    index_content["objectType"] = object_type
    
    # Process all files in directory
    for file_path in directory.glob("*.json"):
        if file_path.name in [".template.json", "index.json"]:
            continue
            
        try:
            data = load_json_file(file_path)
            index_content["objects"].append({
                "name": data.get("name", "Unknown"),
                "filename": file_path.name,
                "type": data.get("type", object_type),
                "lastUpdated": data.get("metadata", {}).get("lastUpdated", datetime.now().isoformat())
            })
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
    
    # Update total objects count
    index_content["metadata"]["totalObjects"] = len(index_content["objects"])
    
    # Calculate statistics
    index_content["statistics"] = calculate_statistics(directory, template)
    
    return index_content

def update_index_file(directory: Path) -> None:
    """Update the index.json file for a directory."""
    template_path = directory / ".template.json"
    index_path = directory / "index.json"
    
    if not template_path.exists():
        print(f"No template found in {directory}")
        return
    
    print(f"Updating index for {directory}...")
    
    # Load template
    template = load_json_file(template_path)
    
    # Generate new index content
    index_content = generate_index_content(directory, template)
    
    # Save index file
    save_json_file(index_content, index_path)
    print(f"Updated {index_path}")

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
            update_index_file(dir_path)
        else:
            print(f"Directory {directory} not found")

if __name__ == "__main__":
    main() 