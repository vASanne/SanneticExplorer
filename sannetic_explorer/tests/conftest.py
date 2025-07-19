"""
Pytest configuration and fixtures for Sannetic Explorer tests

Provides common fixtures and configuration for all backend tests.
"""

import pytest
from typing import Generator
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from sannetic_explorer.api import app
from sannetic_explorer.models import Base
from sannetic_explorer.services.database import get_db


# Test database configuration
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def test_db():
    """Create test database tables"""
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(test_db) -> Generator[Session, None, None]:
    """Create database session for testing"""
    connection = test_engine.connect()
    transaction = connection.begin()
    
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session) -> Generator[TestClient, None, None]:
    """Create test client with database session"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    with patch('sannetic_explorer.api.redis_client') as mock:
        mock.get.return_value = None
        mock.setex.return_value = True
        mock.incr.return_value = 1
        mock.lpush.return_value = 1
        yield mock


@pytest.fixture
def sample_celestial_bodies():
    """Sample celestial bodies for testing"""
    return [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Sun",
            "type": "star",
            "subtype": "yellow_dwarf",
            "parent_id": None,
            "mass_kg": 1.989e30,
            "radius_km": 696340.0,
            "density_kg_m3": 1408.0,
            "surface_gravity_ms2": 274.0,
            "escape_velocity_kms": 617.7,
            "mean_distance_au": 0.0,
            "orbital_speed_kms": 0.0,
            "color_hex": "#FFD700",
            "texture_url": None,
            "albedo": 0.306,
            "discovery_date": "Prehistoric",
            "discoverer": "Unknown",
            "discovery_method": "Visual observation",
            "data_quality": "excellent",
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": None
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "name": "Earth",
            "type": "planet",
            "subtype": "terrestrial",
            "parent_id": "550e8400-e29b-41d4-a716-446655440000",
            "mass_kg": 5.972e24,
            "radius_km": 6371.0,
            "density_kg_m3": 5514.0,
            "surface_gravity_ms2": 9.81,
            "escape_velocity_kms": 11.19,
            "mean_distance_au": 1.0,
            "orbital_speed_kms": 29.78,
            "color_hex": "#0077BE",
            "texture_url": None,
            "albedo": 0.367,
            "discovery_date": "Prehistoric",
            "discoverer": "Unknown",
            "discovery_method": "Visual observation",
            "data_quality": "excellent",
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": None
        }
    ]


@pytest.fixture
def sample_update_logs():
    """Sample update logs for testing"""
    return [
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "timestamp": "2024-01-15T10:30:00Z",
            "script_name": "update_critical.py",
            "status": "success",
            "message": "Successfully updated 5 critical satellites",
            "duration_sec": 45.2,
            "log_level": "INFO",
            "source_file": "/var/log/update.log"
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440003",
            "timestamp": "2024-01-15T09:15:00Z",
            "script_name": "update_data_optimized.py",
            "status": "error",
            "message": "API rate limit exceeded",
            "duration_sec": 12.8,
            "log_level": "ERROR",
            "source_file": "/var/log/update.log"
        }
    ]


@pytest.fixture
def mock_database_stats():
    """Mock database statistics"""
    return {
        "total_rows": 100,
        "tables": {
            "celestial_bodies": {
                "row_count": 50,
                "columns": {}
            },
            "update_logs": {
                "row_count": 50,
                "columns": {}
            }
        }
    }


# Markers for different test types
pytest_plugins = ["pytest_asyncio"]


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    ) 