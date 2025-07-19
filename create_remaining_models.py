#!/usr/bin/env python3
"""
Script to create remaining model files from the original models.py
"""

import re
from pathlib import Path

def extract_class_content(content: str, class_name: str) -> str:
    """Extract a class definition from the content"""
    pattern = rf"class {class_name}\(Base\):(.*?)(?=class |$)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def create_model_file(class_name: str, content: str, filename: str):
    """Create a model file with proper imports and structure"""
    
    # Convert class name to snake_case for filename
    if not filename:
        filename = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower() + '.py'
    
    # Add proper imports and structure
    file_content = f'''"""
{class_name} model for Sannetic Explorer

Model for {class_name.lower().replace('_', ' ')}.
"""

from typing import Optional, List
from uuid import uuid4
from datetime import datetime

from sqlalchemy import (
    Column, String, Float, Boolean, DateTime, JSON, ForeignKey, 
    Integer, Text, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from .base import Base


{content}
'''
    
    # Write the file
    model_path = Path(f"sannetic_explorer/models/{filename}")
    model_path.write_text(file_content)
    print(f"Created {model_path}")

def main():
    """Main function to create all remaining model files"""
    
    # Read the original models.py
    with open("models.py", "r") as f:
        content = f.read()
    
    # Define the remaining models to create
    models_to_create = [
        ("PhysicalCharacteristics", "physical_characteristics.py"),
        ("StellarCharacteristics", "stellar_characteristics.py"),
        ("SpacecraftMission", "spacecraft_missions.py"),
        ("TLEElements", "tle_elements.py"),
        ("ExplorationHistory", "exploration_history.py"),
        ("SimulationState", "simulation_state.py"),
    ]
    
    # Create each model file
    for class_name, filename in models_to_create:
        class_content = extract_class_content(content, class_name)
        if class_content:
            create_model_file(class_name, class_content, filename)
        else:
            print(f"Warning: Could not find class {class_name}")

if __name__ == "__main__":
    main() 