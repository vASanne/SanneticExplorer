#!/usr/bin/env python3
"""
FastAPI Backend for Solar System Simulation
Provides REST API endpoints for celestial body data and simulation
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import json
import subprocess
import redis
import os

# Import from new package structure
from ..services.database import get_db, init_database, get_database_stats
from ..models import (
    CelestialBody, OrbitalParameters, PhysicalCharacteristics,
    StellarCharacteristics, SpacecraftMission, TLEElements,
    UpdateLog
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sannetic Explorer Solar System API",
    description="Comprehensive API for solar system simulation and celestial body data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def _cors_origins():
    """Origins allowed to call the API from a browser.

    Docker publishes the UI on port 13300. Local Vite stays on port 3000.
    Set CORS_ORIGINS to a comma-separated list to override both.
    """
    configured = os.getenv("CORS_ORIGINS", "").strip()
    if configured:
        return [origin.strip() for origin in configured.split(",") if origin.strip()]
    origins = []
    for origin in (
        os.getenv("FRONTEND_URL", "http://localhost:13300"),
        "http://localhost:13300",
        "http://localhost:3000",
    ):
        if origin and origin not in origins:
            origins.append(origin)
    return origins


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Redis connection for rate limiting and job queue
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

# Pydantic models for API responses
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

# Update model for PUT requests
class CelestialBodyUpdate(BaseModel):
    """Model for updating celestial body properties"""
    radius_km: Optional[float] = Field(None, ge=0, description="Radius in kilometers")
    mean_distance_au: Optional[float] = Field(None, ge=0, description="Mean distance in AU")
    orbital_speed_kms: Optional[float] = Field(None, ge=0, description="Orbital speed in km/s")
    color_hex: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Color in hex format")
    mass_kg: Optional[float] = Field(None, ge=0, description="Mass in kilograms")
    density_kg_m3: Optional[float] = Field(None, ge=0, description="Density in kg/m³")
    surface_gravity_ms2: Optional[float] = Field(None, description="Surface gravity in m/s²")
    escape_velocity_kms: Optional[float] = Field(None, ge=0, description="Escape velocity in km/s")
    albedo: Optional[float] = Field(None, ge=0, le=1, description="Albedo (0-1)")
    discovery_date: Optional[str] = Field(None, description="Discovery date")
    discoverer: Optional[str] = Field(None, description="Discoverer name")
    discovery_method: Optional[str] = Field(None, description="Discovery method")
    data_quality: Optional[str] = Field(None, description="Data quality rating")

class CelestialBodyResponse(BaseModel):
    id: UUID
    name: str
    type: str
    body_type: Optional[str] = None
    subtype: Optional[str] = None
    parent_id: Optional[UUID] = None
    mass_kg: Optional[float] = None
    radius_km: Optional[float] = None
    density_kg_m3: Optional[float] = None
    surface_gravity_ms2: Optional[float] = None
    escape_velocity_kms: Optional[float] = None
    color_hex: Optional[str] = None
    texture_url: Optional[str] = None
    albedo: Optional[float] = None
    discovery_date: Optional[str] = None
    discoverer: Optional[str] = None
    discovery_method: Optional[str] = None
    data_quality: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @model_validator(mode="after")
    def fill_body_type(self):
        """Frontend reads body_type; the column is type."""
        if not self.body_type:
            self.body_type = self.type
        return self

    class Config:
        from_attributes = True

class UpdateLogResponse(BaseModel):
    """Response model for update log entries"""
    id: UUID
    timestamp: datetime
    script_name: str
    status: str
    message: Optional[str] = None
    duration_sec: Optional[float] = None
    log_level: Optional[str] = None
    source_file: Optional[str] = None
    
    class Config:
        from_attributes = True

class ScriptStatusResponse(BaseModel):
    """Response model for script status"""
    script_name: str
    last_run: Optional[datetime] = None
    status: str  # "OK", "FAIL", "UNKNOWN"
    duration_sec: Optional[float] = None
    message: Optional[str] = None

class TriggerScriptRequest(BaseModel):
    """Request model for triggering scripts"""
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Script parameters")

class PlanetResponse(BaseModel):
    """Response model for planet data with orbital and physical characteristics"""
    id: UUID
    name: str
    type: str
    subtype: Optional[str] = None
    mass_kg: Optional[float] = None
    radius_km: Optional[float] = None
    mean_distance_au: Optional[float] = None
    orbital_speed_kms: Optional[float] = None
    surface_gravity_ms2: Optional[float] = None
    color_hex: Optional[str] = None
    data_quality: str
    
    # Orbital parameters
    orbital_period_days: Optional[float] = None
    semi_major_axis_km: Optional[float] = None
    eccentricity: Optional[float] = None
    inclination_degrees: Optional[float] = None
    
    # Physical characteristics
    has_atmosphere: Optional[bool] = None
    atmospheric_composition: Optional[Dict[str, Any]] = None
    has_rings: Optional[bool] = None
    surface_temperature_k: Optional[float] = None
    
    class Config:
        from_attributes = True

# Rate limiting dependency
async def rate_limit(request: Request) -> None:
    """Rate limiting middleware"""
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    # Get current count
    current = redis_client.get(key)
    if current is None:
        redis_client.setex(key, 60, 1)  # 1 request per minute
    else:
        count = int(current)
        if count >= 60:  # 60 requests per minute
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        redis_client.incr(key)

# Startup event
@app.on_event("startup")
async def startup_event() -> None:
    """Initialize application on startup"""
    try:
        init_database()
        from ..services.seed_planets import seed_solar_system

        added = seed_solar_system()
        logger.info("Solar-system seed finished (%s new bodies)", added)
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# System statistics endpoint
@app.get("/stats", tags=["System"])
async def get_system_statistics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get system statistics"""
    try:
        # Get basic counts
        total_bodies = db.query(CelestialBody).count()
        
        # Count by type
        type_counts = {}
        for body_type in ['star', 'planet', 'moon', 'satellite', 'spacecraft']:
            count = db.query(CelestialBody).filter(CelestialBody.type == body_type).count()
            type_counts[body_type] = count
        
        # Count by data quality
        quality_counts = {}
        for quality in ['excellent', 'good', 'fair', 'poor', 'unknown']:
            count = db.query(CelestialBody).filter(CelestialBody.data_quality == quality).count()
            quality_counts[quality] = count
        
        # Get database stats
        db_stats = get_database_stats()
        
        return {
            "total_celestial_bodies": total_bodies,
            "by_type": type_counts,
            "by_data_quality": quality_counts,
            "database_size": f"{db_stats.get('total_rows', 0)} rows",
            "last_updated": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error getting system statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system statistics")

def _list_celestial_bodies(
    db: Session,
    type_filter: Optional[str],
    parent_id: Optional[str],
    limit: int,
    offset: int,
) -> List[CelestialBody]:
    query = db.query(CelestialBody)
    if type_filter:
        query = query.filter(CelestialBody.type == type_filter)
    if parent_id:
        query = query.filter(CelestialBody.parent_id == parent_id)
    return query.offset(offset).limit(limit).all()


def _get_celestial_body(db: Session, body_id: UUID) -> CelestialBody:
    celestial_body = db.query(CelestialBody).filter(CelestialBody.id == body_id).first()
    if not celestial_body:
        raise HTTPException(status_code=404, detail="Celestial body not found")
    return celestial_body


# Celestial bodies endpoints.
# /bodies is the path the frontend already calls; /celestial-bodies is the canonical name.
@app.get("/celestial-bodies", response_model=List[CelestialBodyResponse], tags=["Celestial Bodies"])
@app.get("/bodies", response_model=List[CelestialBodyResponse], tags=["Celestial Bodies"])
async def get_celestial_bodies(
    db: Session = Depends(get_db),
    type: Optional[str] = Query(None, description="Filter by celestial body type"),
    body_type: Optional[str] = Query(None, description="Alias of type, used by the frontend"),
    parent_id: Optional[str] = Query(None, description="Filter by parent ID"),
    limit: int = Query(100, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
) -> List[CelestialBody]:
    """Get celestial bodies with optional filtering"""
    try:
        return _list_celestial_bodies(db, type or body_type, parent_id, limit, offset)
    except Exception as e:
        logger.error(f"Error getting celestial bodies: {e}")
        raise HTTPException(status_code=500, detail="Failed to get celestial bodies")


@app.get("/celestial-bodies/{body_id}", response_model=CelestialBodyResponse, tags=["Celestial Bodies"])
@app.get("/bodies/{body_id}", response_model=CelestialBodyResponse, tags=["Celestial Bodies"])
async def get_celestial_body(
    body_id: UUID = Path(..., description="Celestial body ID"),
    db: Session = Depends(get_db),
) -> CelestialBody:
    """Get one celestial body by id"""
    try:
        return _get_celestial_body(db, body_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting celestial body {body_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get celestial body")

@app.get("/planets", response_model=List[PlanetResponse], tags=["Celestial Bodies"])
async def get_planets(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get all planets with their orbital and physical characteristics"""
    try:
        # Query planets with their related data
        planets = db.query(CelestialBody).filter(CelestialBody.type == "planet").order_by(CelestialBody.mean_distance_au).all()
        
        result = []
        for planet in planets:
            # Get orbital parameters
            orbital_params = db.query(OrbitalParameters).filter(OrbitalParameters.celestial_body_id == planet.id).first()
            
            # Get physical characteristics
            physical_chars = db.query(PhysicalCharacteristics).filter(PhysicalCharacteristics.celestial_body_id == planet.id).first()
            
            # Build response
            planet_data = {
                "id": planet.id,
                "name": planet.name,
                "type": planet.type,
                "subtype": planet.subtype,
                "mass_kg": planet.mass_kg,
                "radius_km": planet.radius_km,
                "mean_distance_au": planet.mean_distance_au,
                "orbital_speed_kms": planet.orbital_speed_kms,
                "surface_gravity_ms2": planet.surface_gravity_ms2,
                "color_hex": planet.color_hex,
                "data_quality": planet.data_quality,
                
                # Orbital parameters
                "orbital_period_days": orbital_params.orbital_period_days if orbital_params else None,
                "semi_major_axis_km": orbital_params.semi_major_axis_km if orbital_params else None,
                "eccentricity": orbital_params.eccentricity if orbital_params else None,
                "inclination_degrees": orbital_params.inclination_degrees if orbital_params else None,
                
                # Physical characteristics
                "has_atmosphere": physical_chars.has_atmosphere if physical_chars else None,
                "atmospheric_composition": physical_chars.atmospheric_composition if physical_chars else None,
                "has_rings": physical_chars.has_rings if physical_chars else None,
                "surface_temperature_k": physical_chars.surface_temperature_k if physical_chars else None,
            }
            
            result.append(planet_data)
        
        return result
    except Exception as e:
        logger.error(f"Error getting planets: {e}")
        raise HTTPException(status_code=500, detail="Failed to get planets")

@app.put("/bodies/{body_id}", response_model=CelestialBodyResponse, tags=["Celestial Bodies"])
async def update_celestial_body(
    body_id: UUID = Path(..., description="Celestial body ID"),
    update_data: CelestialBodyUpdate = Body(..., description="Update data"),
    db: Session = Depends(get_db)
) -> CelestialBody:
    """Update a celestial body"""
    try:
        celestial_body = db.query(CelestialBody).filter(CelestialBody.id == body_id).first()
        if not celestial_body:
            raise HTTPException(status_code=404, detail="Celestial body not found")
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(celestial_body, field, value)
        
        # Set updated timestamp
        celestial_body.updated_at = datetime.now()
        
        db.commit()
        db.refresh(celestial_body)
        return celestial_body
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating celestial body {body_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update celestial body")

# Update management endpoints
@app.get("/updates/latest", response_model=List[UpdateLogResponse], tags=["Updates"])
async def get_latest_updates(
    limit: int = Query(50, le=200, description="Number of latest updates to return"),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit)
) -> List[UpdateLog]:
    """Get the latest N update log entries"""
    try:
        updates = db.query(UpdateLog).order_by(
            desc(UpdateLog.timestamp)
        ).limit(limit).all()
        
        return updates
    except Exception as e:
        logger.error(f"Error getting latest updates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get latest updates")

@app.get("/updates/status", response_model=List[ScriptStatusResponse], tags=["Updates"])
async def get_script_status(
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit)
) -> List[ScriptStatusResponse]:
    """Get the last run status for each script"""
    try:
        # Get unique script names
        script_names = db.query(UpdateLog.script_name).distinct().all()
        script_names = [name[0] for name in script_names]
        
        status_list = []
        for script_name in script_names:
            # Get the latest entry for this script
            latest = db.query(UpdateLog).filter(
                UpdateLog.script_name == script_name
            ).order_by(desc(UpdateLog.timestamp)).first()
            
            if latest:
                # Determine status based on the latest entry
                if latest.status == "success":
                    status = "OK"
                elif latest.status == "error":
                    status = "FAIL"
                else:
                    status = "UNKNOWN"
                
                status_list.append(ScriptStatusResponse(
                    script_name=script_name,
                    last_run=latest.timestamp,
                    status=status,
                    duration_sec=latest.duration_sec,
                    message=latest.message
                ))
            else:
                status_list.append(ScriptStatusResponse(
                    script_name=script_name,
                    last_run=None,
                    status="UNKNOWN",
                    duration_sec=None,
                    message=None
                ))
        
        return status_list
    except Exception as e:
        logger.error(f"Error getting script status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get script status")

@app.post("/updates/trigger/{script_name}", tags=["Updates"])
async def trigger_script(
    script_name: str = Path(..., description="Name of the script to trigger"),
    request: TriggerScriptRequest = Body(..., description="Script parameters"),
    _: None = Depends(rate_limit)
) -> Dict[str, Any]:
    """Manually trigger a script execution"""
    try:
        # Validate script name
        valid_scripts = [
            "update_critical.py",
            "update_data_optimized.py", 
            "enhanced_delta_manager.py",
            "ai_health_check.py",
            "sync.py"
        ]
        
        if script_name not in valid_scripts:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid script name. Valid scripts: {', '.join(valid_scripts)}"
            )
        
        # Create job in Redis queue
        job_id = f"script_{script_name}_{int(datetime.now().timestamp())}"
        job_data = {
            "script_name": script_name,
            "parameters": request.parameters,
            "triggered_at": datetime.now().isoformat(),
            "triggered_by": "api"
        }
        
        # Add to Redis queue
        redis_client.lpush("script_queue", json.dumps(job_data))
        
        # Log the trigger
        logger.info(f"Script {script_name} triggered via API with parameters: {request.parameters}")
        
        return {
            "job_id": job_id,
            "script_name": script_name,
            "status": "queued",
            "message": f"Script {script_name} has been queued for execution"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering script {script_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger script")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 