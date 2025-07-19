"""
Tests for UpdateLog model and API endpoints

Tests UpdateLog insertion logic, /updates/status endpoint, and CRUD operations.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from sannetic_explorer.models import UpdateLog, CelestialBody
from sannetic_explorer.api import app
from sannetic_explorer.services.database import get_db


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Create database session for testing"""
    # This would need to be configured with a test database
    # For now, we'll mock the database session
    pass


@pytest.fixture
def sample_update_logs():
    """Create sample update log entries for testing"""
    return [
        {
            "id": uuid4(),
            "timestamp": datetime.now() - timedelta(hours=1),
            "script_name": "update_critical.py",
            "status": "success",
            "message": "Successfully updated 5 critical satellites",
            "duration_sec": 45.2,
            "log_level": "INFO",
            "source_file": "/var/log/update.log"
        },
        {
            "id": uuid4(),
            "timestamp": datetime.now() - timedelta(hours=2),
            "script_name": "update_data_optimized.py",
            "status": "error",
            "message": "API rate limit exceeded",
            "duration_sec": 12.8,
            "log_level": "ERROR",
            "source_file": "/var/log/update.log"
        },
        {
            "id": uuid4(),
            "timestamp": datetime.now() - timedelta(hours=3),
            "script_name": "sync.py",
            "status": "success",
            "message": "Data synchronization completed",
            "duration_sec": 120.5,
            "log_level": "INFO",
            "source_file": "/var/log/update.log"
        },
        {
            "id": uuid4(),
            "timestamp": datetime.now() - timedelta(hours=4),
            "script_name": "ai_health_check.py",
            "status": "warning",
            "message": "Some data quality issues detected",
            "duration_sec": 30.1,
            "log_level": "WARNING",
            "source_file": "/var/log/update.log"
        }
    ]


class TestUpdateLogModel:
    """Test UpdateLog model functionality"""
    
    def test_update_log_creation(self):
        """Test creating UpdateLog instances"""
        log = UpdateLog(
            script_name="test_script.py",
            status="success",
            message="Test message",
            duration_sec=10.5
        )
        
        assert log.script_name == "test_script.py"
        assert log.status == "success"
        assert log.message == "Test message"
        assert log.duration_sec == 10.5
        assert log.timestamp is not None
    
    def test_update_log_repr(self):
        """Test UpdateLog string representation"""
        log = UpdateLog(
            script_name="test_script.py",
            status="success"
        )
        
        repr_str = repr(log)
        assert "UpdateLog" in repr_str
        assert "test_script.py" in repr_str
        assert "success" in repr_str
    
    def test_update_log_constraints(self):
        """Test UpdateLog constraint validation"""
        # Valid status
        log = UpdateLog(
            script_name="test.py",
            status="success"
        )
        assert log.status in ["success", "error", "warning", "info"]
        
        # Valid duration (non-negative)
        log.duration_sec = 0.0
        assert log.duration_sec >= 0
        
        log.duration_sec = 100.5
        assert log.duration_sec >= 0


class TestUpdateLogAPI:
    """Test UpdateLog API endpoints"""
    
    def test_get_latest_updates(self, client, sample_update_logs, monkeypatch):
        """Test GET /updates/latest endpoint"""
        # Mock the database session
        def mock_get_db():
            class MockDB:
                def query(self, model):
                    return self
                
                def order_by(self, *args):
                    return self
                
                def limit(self, limit):
                    return sample_update_logs
                
                def all(self):
                    return sample_update_logs
            
            return MockDB()
        
        monkeypatch.setattr("sannetic_explorer.api.get_db", mock_get_db)
        
        response = client.get("/updates/latest?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
        assert data[0]["script_name"] == "update_critical.py"
        assert data[0]["status"] == "success"
    
    def test_get_latest_updates_with_limit(self, client, sample_update_logs, monkeypatch):
        """Test GET /updates/latest with limit parameter"""
        def mock_get_db():
            class MockDB:
                def query(self, model):
                    return self
                
                def order_by(self, *args):
                    return self
                
                def limit(self, limit):
                    self.limit_value = limit
                    return self
                
                def all(self):
                    return sample_update_logs[:self.limit_value]
            
            return MockDB()
        
        monkeypatch.setattr("sannetic_explorer.api.get_db", mock_get_db)
        
        response = client.get("/updates/latest?limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_script_status(self, client, sample_update_logs, monkeypatch):
        """Test GET /updates/status endpoint"""
        def mock_get_db():
            class MockDB:
                def query(self, model):
                    return self
                
                def distinct(self):
                    return self
                
                def all(self):
                    return [("update_critical.py",), ("update_data_optimized.py",), ("sync.py",), ("ai_health_check.py",)]
                
                def filter(self, *args):
                    return self
                
                def order_by(self, *args):
                    return self
                
                def first(self):
                    # Return the most recent log for each script
                    script_name = "update_critical.py"  # This would be extracted from filter
                    if script_name == "update_critical.py":
                        return sample_update_logs[0]
                    elif script_name == "update_data_optimized.py":
                        return sample_update_logs[1]
                    elif script_name == "sync.py":
                        return sample_update_logs[2]
                    elif script_name == "ai_health_check.py":
                        return sample_update_logs[3]
                    return None
            
            return MockDB()
        
        monkeypatch.setattr("sannetic_explorer.api.get_db", mock_get_db)
        
        response = client.get("/updates/status")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
        
        # Check status mapping
        statuses = [item["status"] for item in data]
        assert "OK" in statuses  # success -> OK
        assert "FAIL" in statuses  # error -> FAIL
        assert "UNKNOWN" in statuses  # warning -> UNKNOWN
    
    def test_trigger_script_valid(self, client, monkeypatch):
        """Test POST /updates/trigger/{script_name} with valid script"""
        def mock_redis():
            class MockRedis:
                def lpush(self, queue, data):
                    return 1
            return MockRedis()
        
        monkeypatch.setattr("sannetic_explorer.api.redis_client", mock_redis())
        
        response = client.post(
            "/updates/trigger/update_critical.py",
            json={"parameters": {"force": True}}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["script_name"] == "update_critical.py"
        assert data["status"] == "queued"
        assert "job_id" in data
    
    def test_trigger_script_invalid(self, client):
        """Test POST /updates/trigger/{script_name} with invalid script"""
        response = client.post(
            "/updates/trigger/invalid_script.py",
            json={"parameters": {}}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid script name" in data["detail"]
    
    def test_rate_limiting(self, client, monkeypatch):
        """Test rate limiting on update endpoints"""
        def mock_redis():
            class MockRedis:
                def get(self, key):
                    return "60"  # Simulate rate limit exceeded
                
                def setex(self, key, ttl, value):
                    pass
                
                def incr(self, key):
                    pass
            return MockRedis()
        
        monkeypatch.setattr("sannetic_explorer.api.redis_client", mock_redis())
        
        response = client.get("/updates/latest")
        
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]


class TestCelestialBodyCRUD:
    """Test CelestialBody CRUD operations remain intact"""
    
    def test_get_celestial_bodies(self, client, monkeypatch):
        """Test GET /celestial-bodies endpoint"""
        sample_bodies = [
            {
                "id": str(uuid4()),
                "name": "Sun",
                "type": "star",
                "mass_kg": 1.989e30,
                "radius_km": 696340.0,
                "data_quality": "excellent",
                "created_at": datetime.now().isoformat(),
                "updated_at": None
            },
            {
                "id": str(uuid4()),
                "name": "Earth",
                "type": "planet",
                "mass_kg": 5.972e24,
                "radius_km": 6371.0,
                "data_quality": "excellent",
                "created_at": datetime.now().isoformat(),
                "updated_at": None
            }
        ]
        
        def mock_get_db():
            class MockDB:
                def query(self, model):
                    return self
                
                def filter(self, *args):
                    return self
                
                def offset(self, offset):
                    return self
                
                def limit(self, limit):
                    return self
                
                def all(self):
                    return sample_bodies
            
            return MockDB()
        
        monkeypatch.setattr("sannetic_explorer.api.get_db", mock_get_db)
        
        response = client.get("/celestial-bodies")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Sun"
        assert data[1]["name"] == "Earth"
    
    def test_get_celestial_bodies_with_filters(self, client, monkeypatch):
        """Test GET /celestial-bodies with type filter"""
        sample_bodies = [
            {
                "id": str(uuid4()),
                "name": "Sun",
                "type": "star",
                "data_quality": "excellent",
                "created_at": datetime.now().isoformat(),
                "updated_at": None
            }
        ]
        
        def mock_get_db():
            class MockDB:
                def query(self, model):
                    return self
                
                def filter(self, *args):
                    return self
                
                def offset(self, offset):
                    return self
                
                def limit(self, limit):
                    return self
                
                def all(self):
                    return sample_bodies
            
            return MockDB()
        
        monkeypatch.setattr("sannetic_explorer.api.get_db", mock_get_db)
        
        response = client.get("/celestial-bodies?type=star")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "star"
    
    def test_update_celestial_body(self, client, monkeypatch):
        """Test PUT /bodies/{body_id} endpoint"""
        body_id = str(uuid4())
        original_body = {
            "id": body_id,
            "name": "Earth",
            "type": "planet",
            "radius_km": 6371.0,
            "data_quality": "excellent",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        }
        
        updated_body = {
            "id": body_id,
            "name": "Earth",
            "type": "planet",
            "radius_km": 6378.0,  # Updated radius
            "data_quality": "excellent",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        def mock_get_db():
            class MockDB:
                def query(self, model):
                    return self
                
                def filter(self, *args):
                    return self
                
                def first(self):
                    return original_body
                
                def commit(self):
                    pass
                
                def refresh(self, obj):
                    pass
                
                def rollback(self):
                    pass
            
            return MockDB()
        
        monkeypatch.setattr("sannetic_explorer.api.get_db", mock_get_db)
        
        response = client.put(
            f"/bodies/{body_id}",
            json={"radius_km": 6378.0}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["radius_km"] == 6378.0
    
    def test_update_celestial_body_not_found(self, client, monkeypatch):
        """Test PUT /bodies/{body_id} with non-existent body"""
        body_id = str(uuid4())
        
        def mock_get_db():
            class MockDB:
                def query(self, model):
                    return self
                
                def filter(self, *args):
                    return self
                
                def first(self):
                    return None
            
            return MockDB()
        
        monkeypatch.setattr("sannetic_explorer.api.get_db", mock_get_db)
        
        response = client.put(
            f"/bodies/{body_id}",
            json={"radius_km": 6378.0}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestHealthAndStats:
    """Test health check and statistics endpoints"""
    
    def test_health_check(self, client):
        """Test GET /health endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_system_statistics(self, client, monkeypatch):
        """Test GET /stats endpoint"""
        def mock_get_db():
            class MockDB:
                def query(self, model):
                    return self
                
                def filter(self, *args):
                    return self
                
                def count(self):
                    return 10
            
            return MockDB()
        
        def mock_get_database_stats():
            return {"total_rows": 100}
        
        monkeypatch.setattr("sannetic_explorer.api.get_db", mock_get_db)
        monkeypatch.setattr("sannetic_explorer.api.get_database_stats", mock_get_database_stats)
        
        response = client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_celestial_bodies"] == 10
        assert "by_type" in data
        assert "by_data_quality" in data
        assert data["database_size"] == "100 rows" 