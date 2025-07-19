import json
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
import jsonschema
from datetime import datetime
import pandas as pd
import numpy as np

def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_against_template(data: Dict[str, Any], template: Dict[str, Any], file_path: Path) -> List[str]:
    """Validate data against template and return list of errors."""
    errors = []
    
    def check_structure(data_dict: Dict[str, Any], template_dict: Dict[str, Any], path: str = "") -> None:
        for key, template_value in template_dict.items():
            current_path = f"{path}.{key}" if path else key
            
            if key not in data_dict:
                errors.append(f"Missing required field: {current_path}")
            elif isinstance(template_value, dict) and isinstance(data_dict[key], dict):
                check_structure(data_dict[key], template_value, current_path)
            elif isinstance(template_value, list) and isinstance(data_dict[key], list):
                if template_value and isinstance(template_value[0], dict):
                    for i, item in enumerate(data_dict[key]):
                        check_structure(item, template_value[0], f"{current_path}[{i}]")
    
    check_structure(data, template)
    return errors

def validate_data_types(data: Dict[str, Any], template: Dict[str, Any], file_path: Path) -> List[str]:
    """Validate data types against template and return list of errors."""
    errors = []
    
    def check_types(data_dict: Dict[str, Any], template_dict: Dict[str, Any], path: str = "") -> None:
        for key, template_value in template_dict.items():
            current_path = f"{path}.{key}" if path else key
            
            if key in data_dict:
                data_value = data_dict[key]
                if isinstance(template_value, dict) and isinstance(data_value, dict):
                    check_types(data_value, template_value, current_path)
                elif isinstance(template_value, list) and isinstance(data_value, list):
                    if template_value and isinstance(template_value[0], dict):
                        for i, item in enumerate(data_value):
                            check_types(item, template_value[0], f"{current_path}[{i}]")
                elif template_value != "noValue" and data_value == "noValue":
                    errors.append(f"Required field has no value: {current_path}")
    
    check_types(data, template)
    return errors

def validate_cross_references(data: Dict[str, Any], file_path: Path, all_files: Dict[Path, Dict[str, Any]]) -> List[str]:
    """Validate cross-references between files and return list of errors."""
    errors = []
    
    # Check parent body references
    if "parentBody" in data:
        parent_name = data["parentBody"]
        if parent_name != "noValue":
            parent_found = False
            for other_file, other_data in all_files.items():
                if other_data.get("name") == parent_name:
                    parent_found = True
                    break
            if not parent_found:
                errors.append(f"Referenced parent body '{parent_name}' not found in any file")
    
    # Check moon references
    if "moons" in data:
        for moon in data["moons"]:
            moon_found = False
            for other_file, other_data in all_files.items():
                if other_data.get("name") == moon:
                    moon_found = True
                    break
            if not moon_found:
                errors.append(f"Referenced moon '{moon}' not found in any file")
    
    return errors

def generate_statistics(directory: Path) -> Dict[str, Any]:
    """Generate statistics about data completeness."""
    stats = {
        "total_files": 0,
        "total_fields": 0,
        "filled_fields": 0,
        "missing_fields": 0,
        "completion_percentage": 0.0
    }
    
    template = load_json_file(directory / ".template.json")
    
    def count_fields(data_dict: Dict[str, Any], template_dict: Dict[str, Any]) -> Tuple[int, int]:
        total = 0
        filled = 0
        
        for key, template_value in template_dict.items():
            total += 1
            if key in data_dict:
                data_value = data_dict[key]
                if isinstance(template_value, dict) and isinstance(data_value, dict):
                    t, f = count_fields(data_value, template_value)
                    total += t
                    filled += f
                elif isinstance(template_value, list) and isinstance(data_value, list):
                    if template_value and isinstance(template_value[0], dict):
                        for item in data_value:
                            t, f = count_fields(item, template_value[0])
                            total += t
                            filled += f
                elif data_value != "noValue":
                    filled += 1
        
        return total, filled
    
    for file_path in directory.glob("*.json"):
        if file_path.name in [".template.json", "index.json"]:
            continue
            
        stats["total_files"] += 1
        data = load_json_file(file_path)
        total, filled = count_fields(data, template)
        stats["total_fields"] += total
        stats["filled_fields"] += filled
    
    stats["missing_fields"] = stats["total_fields"] - stats["filled_fields"]
    if stats["total_fields"] > 0:
        stats["completion_percentage"] = (stats["filled_fields"] / stats["total_fields"]) * 100
    
    return stats

def main():
    # Process each data directory
    data_dirs = [
        "Data/Planets",
        "Data/NaturalSatellites",
        "Data/Spacecraft",
        "Data/Stars"
    ]
    
    all_files = {}
    validation_results = {}
    
    for directory in data_dirs:
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"\nDirectory {directory} not found")
            continue
            
        print(f"\nProcessing {directory}...")
        template_path = dir_path / ".template.json"
        
        if not template_path.exists():
            print(f"No template found in {directory}")
            continue
            
        template = load_json_file(template_path)
        dir_errors = []
        
        # Load all files in directory
        for file_path in dir_path.glob("*.json"):
            if file_path.name in [".template.json", "index.json"]:
                continue
                
            print(f"Validating {file_path.name}...")
            data = load_json_file(file_path)
            all_files[file_path] = data
            
            # Validate against template
            structure_errors = validate_against_template(data, template, file_path)
            type_errors = validate_data_types(data, template, file_path)
            reference_errors = validate_cross_references(data, file_path, all_files)
            
            if structure_errors or type_errors or reference_errors:
                dir_errors.append({
                    "file": file_path.name,
                    "structure_errors": structure_errors,
                    "type_errors": type_errors,
                    "reference_errors": reference_errors
                })
        
        # Generate statistics
        stats = generate_statistics(dir_path)
        
        validation_results[directory] = {
            "errors": dir_errors,
            "statistics": stats
        }
    
    # Print validation results
    print("\nValidation Results:")
    print("==================")
    
    for directory, results in validation_results.items():
        print(f"\n{directory}:")
        print(f"Total files: {results['statistics']['total_files']}")
        print(f"Completion: {results['statistics']['completion_percentage']:.2f}%")
        
        if results["errors"]:
            print("\nErrors found:")
            for error in results["errors"]:
                print(f"\n{error['file']}:")
                if error["structure_errors"]:
                    print("  Structure errors:")
                    for e in error["structure_errors"]:
                        print(f"    - {e}")
                if error["type_errors"]:
                    print("  Type errors:")
                    for e in error["type_errors"]:
                        print(f"    - {e}")
                if error["reference_errors"]:
                    print("  Reference errors:")
                    for e in error["reference_errors"]:
                        print(f"    - {e}")
        else:
            print("No errors found!")

if __name__ == "__main__":
    main() 