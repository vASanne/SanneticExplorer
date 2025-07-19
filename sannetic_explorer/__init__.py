"""
Sannetic Explorer - Solar System Simulation Platform

A comprehensive platform for solar system simulation with FastAPI backend,
SvelteKit frontend, and automated data management.
"""

__version__ = "1.0.0"
__author__ = "Sannetic Explorer Team"
__description__ = "Solar System Simulation Platform"

# Core exports
from .api import app
from .models import Base, CelestialBody, UpdateLog
from .services import database

__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__description__",
    
    # Core components
    "app",
    "Base",
    "CelestialBody", 
    "UpdateLog",
    "database",
] 