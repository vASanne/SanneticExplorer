#!/usr/bin/env python3
"""
Example usage of the Solar System Data Synchronization
Demonstrates how to use the sync functionality programmatically
"""

import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sync import SolarSystemDataSync

def example_basic_sync():
    """Example of basic synchronization"""
    print("=== Basic Synchronization Example ===")
    
    # Create sync instance
    sync = SolarSystemDataSync(data_dir="Data")
    
    # Run synchronization
    stats = sync.run_sync(update_existing=True)
    
    print(f"Sync completed with stats: {stats}")
    return stats

def example_custom_data_dir():
    """Example with custom data directory"""
    print("=== Custom Data Directory Example ===")
    
    # Use a different data directory
    custom_data_dir = "/path/to/custom/data"
    
    sync = SolarSystemDataSync(data_dir=custom_data_dir)
    stats = sync.run_sync(update_existing=False)  # Only insert new records
    
    print(f"Custom sync completed with stats: {stats}")
    return stats

def example_incremental_update():
    """Example of incremental update"""
    print("=== Incremental Update Example ===")
    
    sync = SolarSystemDataSync(data_dir="Data")
    
    # First run: insert all data
    print("First run: inserting all data...")
    stats1 = sync.run_sync(update_existing=False)
    print(f"First run stats: {stats1}")
    
    # Second run: update existing records
    print("Second run: updating existing records...")
    stats2 = sync.run_sync(update_existing=True)
    print(f"Second run stats: {stats2}")
    
    return stats1, stats2

def example_error_handling():
    """Example of error handling"""
    print("=== Error Handling Example ===")
    
    try:
        # Try to sync with non-existent directory
        sync = SolarSystemDataSync(data_dir="/non/existent/path")
        stats = sync.run_sync(update_existing=True)
        print(f"Sync stats: {stats}")
    except Exception as e:
        print(f"Error occurred: {e}")
        print("This is expected behavior for non-existent directory")

def example_selective_sync():
    """Example of selective synchronization by category"""
    print("=== Selective Sync Example ===")
    
    # You can modify the sync script to only process specific categories
    # This is an example of how you might extend the functionality
    
    sync = SolarSystemDataSync(data_dir="Data")
    
    # Process only planets
    print("Processing only planets...")
    # This would require modification to the sync script
    # to add category filtering functionality
    
    print("Selective sync example completed")

def main():
    """Main example function"""
    print("Solar System Data Synchronization Examples")
    print("=" * 50)
    
    # Run examples
    try:
        # Basic sync example
        example_basic_sync()
        print()
        
        # Incremental update example
        example_incremental_update()
        print()
        
        # Error handling example
        example_error_handling()
        print()
        
        # Selective sync example
        example_selective_sync()
        print()
        
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Example failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 