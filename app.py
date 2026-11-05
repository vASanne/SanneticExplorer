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

# Import database and models
from database import get_db, init_database, get_database_stats
from models import (
    CelestialBody, OrbitalParameters, PhysicalCharacteristics,
    StellarCharacteristics, SpacecraftMission, TLEElements,
    ExplorationHistory, SimulationState, UpdateLog
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
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

# Update model for PUT requests
class CelestialBodyUpdate(BaseModel):
    """Model for updating celestial body properties"""
    radius_km: Optional[float] = Field(None, ge=0, description="Radius in kilometers")
    mean_distance_au: Optional[float] = Field(None, ge=0, description="Mean distance in AU")
    orbital_speed_kms: Optional[float] = Field(None, ge=0, description="Orbital speed in km/s")
    color_hex: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$', description="Color in hex format")
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
    
    class Config:
        from_attributes = True

class OrbitalParametersResponse(BaseModel):
    id: UUID
    celestial_body_id: UUID
    semi_major_axis_km: Optional[float] = None
    eccentricity: Optional[float] = None
    inclination_degrees: Optional[float] = None
    longitude_ascending_node_degrees: Optional[float] = None
    argument_periapsis_degrees: Optional[float] = None
    mean_anomaly_degrees: Optional[float] = None
    orbital_period_days: Optional[float] = None
    orbital_speed_kms: Optional[float] = None
    synodic_period_days: Optional[float] = None
    rotation_period_hours: Optional[float] = None
    axial_tilt_degrees: Optional[float] = None
    distance_from_parent_km: Optional[float] = None
    aphelion_km: Optional[float] = None
    perihelion_km: Optional[float] = None
    epoch: Optional[str] = None
    equinox: Optional[str] = None
    mutual_perturbations: Optional[List[str]] = None
    orbital_stability_score: Optional[float] = None
    
    class Config:
        from_attributes = True

class PhysicalCharacteristicsResponse(BaseModel):
    id: UUID
    celestial_body_id: UUID
    surface_temperature_k: Optional[float] = None
    surface_temperature_min_k: Optional[float] = None
    surface_temperature_max_k: Optional[float] = None
    core_temperature_k: Optional[float] = None
    has_atmosphere: bool
    atmospheric_pressure_pa: Optional[float] = None
    atmospheric_composition: Optional[Dict[str, Any]] = None
    has_magnetic_field: bool
    magnetic_field_strength_t: Optional[float] = None
    magnetic_dipole_moment_tm3: Optional[float] = None
    internal_structure: Optional[Dict[str, Any]] = None
    surface_type: Optional[str] = None
    surface_features: Optional[List[str]] = None
    has_rings: bool
    ring_system: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class StellarCharacteristicsResponse(BaseModel):
    id: UUID
    celestial_body_id: UUID
    spectral_type: Optional[str] = None
    luminosity_class: Optional[str] = None
    luminosity_lsun: Optional[float] = None
    effective_temperature_k: Optional[float] = None
    absolute_magnitude: Optional[float] = None
    apparent_magnitude: Optional[float] = None
    color_index_bv: Optional[float] = None
    fusion_type: Optional[str] = None
    core_temperature_k: Optional[float] = None
    core_pressure_pa: Optional[float] = None
    core_density_kgm3: Optional[float] = None
    age_years: Optional[float] = None
    evolutionary_stage: Optional[str] = None
    expected_lifetime_years: Optional[float] = None
    activity_cycle_period_years: Optional[float] = None
    last_solar_maximum: Optional[str] = None
    last_solar_minimum: Optional[str] = None
    
    class Config:
        from_attributes = True

class SpacecraftMissionResponse(BaseModel):
    id: UUID
    celestial_body_id: UUID
    mission_name: Optional[str] = None
    agency: Optional[str] = None
    mission_type: Optional[str] = None
    launch_date: Optional[datetime] = None
    launch_site: Optional[str] = None
    launch_vehicle: Optional[str] = None
    status: Optional[str] = None
    mission_duration_days: Optional[int] = None
    mass_kg: Optional[float] = None
    dimensions_m: Optional[str] = None
    power_watts: Optional[float] = None
    propulsion_type: Optional[str] = None
    payload: Optional[List[str]] = None
    instruments: Optional[List[str]] = None
    ground_stations: Optional[List[str]] = None
    communication_band: Optional[str] = None
    
    class Config:
        from_attributes = True

class TLEElementsResponse(BaseModel):
    id: UUID
    celestial_body_id: UUID
    norad_id: Optional[str] = None
    international_designator: Optional[str] = None
    line1: str
    line2: str
    epoch: datetime
    mean_motion_ddot: Optional[float] = None
    mean_motion_ddot2: Optional[float] = None
    b_star: Optional[float] = None
    ephemeris_type: Optional[int] = None
    element_set_number: Optional[int] = None
    checksum_line1: Optional[int] = None
    checksum_line2: Optional[int] = None
    inclination_degrees: Optional[float] = None
    right_ascension_degrees: Optional[float] = None
    eccentricity: Optional[float] = None
    argument_perigee_degrees: Optional[float] = None
    mean_anomaly_degrees: Optional[float] = None
    mean_motion_revs_per_day: Optional[float] = None
    revolution_number: Optional[int] = None
    data_source: Optional[str] = None
    data_quality: str
    
    class Config:
        from_attributes = True

class SimulationStateResponse(BaseModel):
    id: UUID
    celestial_body_id: UUID
    position_x_km: Optional[float] = None
    position_y_km: Optional[float] = None
    position_z_km: Optional[float] = None
    velocity_x_kms: Optional[float] = None
    velocity_y_kms: Optional[float] = None
    velocity_z_kms: Optional[float] = None
    rotation_angle_degrees: Optional[float] = None
    axial_tilt_degrees: Optional[float] = None
    simulation_time: datetime
    time_step_seconds: Optional[float] = None
    position_accuracy_km: Optional[float] = None
    velocity_accuracy_kms: Optional[float] = None
    confidence_score: Optional[float] = None
    
    class Config:
        from_attributes = True

class CelestialBodyDetailResponse(BaseModel):
    celestial_body: CelestialBodyResponse
    orbital_parameters: Optional[OrbitalParametersResponse] = None
    physical_characteristics: Optional[PhysicalCharacteristicsResponse] = None
    stellar_characteristics: Optional[StellarCharacteristicsResponse] = None
    spacecraft_missions: List[SpacecraftMissionResponse] = []
    tle_elements: List[TLEElementsResponse] = []
    children: List[CelestialBodyResponse] = []

class SystemStatisticsResponse(BaseModel):
    total_celestial_bodies: int
    by_type: Dict[str, int]
    by_data_quality: Dict[str, int]
    database_size: str
    last_updated: datetime

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

class BuildInfoResponse(BaseModel):
    """Response model for build information"""
    build_time: str
    component: str
    build_timestamp: datetime
    
    class Config:
        from_attributes = True

# Rate limiting dependency
async def rate_limit(request: Request):
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
async def startup_event():
    """Initialize database on startup"""
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/build-info", response_model=BuildInfoResponse, tags=["System"])
async def get_build_info(
    component: str = Query("frontend", description="Component to get build info for"),
    db: Session = Depends(get_db)
):
    """Get build information from database"""
    try:
        # Query build_info table using SQLAlchemy
        result = db.execute(
            "SELECT build_time, component, build_timestamp FROM build_info WHERE component = :component ORDER BY build_timestamp DESC LIMIT 1",
            {"component": component}
        ).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail=f"No build info found for component: {component}")
        
        return BuildInfoResponse(
            build_time=result[0],
            component=result[1],
            build_timestamp=result[2]
        )
    except Exception as e:
        logger.error(f"Error getting build info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get build info")

# Database statistics endpoint
@app.get("/stats", response_model=SystemStatisticsResponse, tags=["System"])
async def get_system_statistics(db: Session = Depends(get_db)):
    """Get system statistics"""
    try:
        # Get counts by type
        type_counts = db.query(
            CelestialBody.type,
            func.count(CelestialBody.id).label('count')
        ).group_by(CelestialBody.type).all()
        
        by_type = {row.type: row.count for row in type_counts}
        
        # Get counts by data quality
        quality_counts = db.query(
            CelestialBody.data_quality,
            func.count(CelestialBody.id).label('count')
        ).group_by(CelestialBody.data_quality).all()
        
        by_data_quality = {row.data_quality: row.count for row in quality_counts}
        
        # Get total count
        total_count = db.query(func.count(CelestialBody.id)).scalar()
        
        # Get database info
        db_info = get_database_stats()
        
        return SystemStatisticsResponse(
            total_celestial_bodies=total_count,
            by_type=by_type,
            by_data_quality=by_data_quality,
            database_size=db_info.get('database_size', 'Unknown'),
            last_updated=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error getting system statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system statistics")

# Celestial body endpoints
@app.get("/celestial-bodies", response_model=List[CelestialBodyResponse], tags=["Celestial Bodies"])
async def get_celestial_bodies(
    db: Session = Depends(get_db),
    type: Optional[str] = Query(None, description="Filter by celestial body type"),
    parent_id: Optional[str] = Query(None, description="Filter by parent ID"),
    limit: int = Query(100, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """Get list of celestial bodies with optional filtering"""
    try:
        query = db.query(CelestialBody)
        
        if type:
            query = query.filter(CelestialBody.type == type)
        
        if parent_id:
            query = query.filter(CelestialBody.parent_id == parent_id)
        
        celestial_bodies = query.offset(offset).limit(limit).all()
        return celestial_bodies
    except Exception as e:
        logger.error(f"Error getting celestial bodies: {e}")
        raise HTTPException(status_code=500, detail="Failed to get celestial bodies")

@app.get("/celestial-bodies/{body_id}", response_model=CelestialBodyDetailResponse, tags=["Celestial Bodies"])
async def get_celestial_body_detail(
    body_id: UUID = Path(..., description="Celestial body ID"),
    db: Session = Depends(get_db)
):
    """Get detailed information about a celestial body"""
    try:
        # Get celestial body
        celestial_body = db.query(CelestialBody).filter(CelestialBody.id == body_id).first()
        if not celestial_body:
            raise HTTPException(status_code=404, detail="Celestial body not found")
        
        # Get related data
        orbital_parameters = db.query(OrbitalParameters).filter(
            OrbitalParameters.celestial_body_id == body_id
        ).first()
        
        physical_characteristics = db.query(PhysicalCharacteristics).filter(
            PhysicalCharacteristics.celestial_body_id == body_id
        ).first()
        
        stellar_characteristics = db.query(StellarCharacteristics).filter(
            StellarCharacteristics.celestial_body_id == body_id
        ).first()
        
        spacecraft_missions = db.query(SpacecraftMission).filter(
            SpacecraftMission.celestial_body_id == body_id
        ).all()
        
        tle_elements = db.query(TLEElements).filter(
            TLEElements.celestial_body_id == body_id
        ).order_by(TLEElements.epoch.desc()).limit(10).all()
        
        children = db.query(CelestialBody).filter(
            CelestialBody.parent_id == body_id
        ).all()
        
        return CelestialBodyDetailResponse(
            celestial_body=celestial_body,
            orbital_parameters=orbital_parameters,
            physical_characteristics=physical_characteristics,
            stellar_characteristics=stellar_characteristics,
            spacecraft_missions=spacecraft_missions,
            tle_elements=tle_elements,
            children=children
        )
    except Exception as e:
        logger.error(f"Error getting celestial body detail: {e}")
        raise HTTPException(status_code=500, detail="Failed to get celestial body detail")

@app.put("/bodies/{body_id}", response_model=CelestialBodyResponse, tags=["Celestial Bodies"])
async def update_celestial_body(
    body_id: UUID = Path(..., description="Celestial body ID"),
    update_data: CelestialBodyUpdate = Body(..., description="Update data"),
    db: Session = Depends(get_db)
):
    """Update a celestial body with new properties"""
    try:
        # Get the celestial body
        celestial_body = db.query(CelestialBody).filter(CelestialBody.id == body_id).first()
        if not celestial_body:
            raise HTTPException(status_code=404, detail="Celestial body not found")
        
        # Update only the fields that are provided
        update_dict = update_data.dict(exclude_unset=True)
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        # Update the celestial body fields
        for field, value in update_dict.items():
            if hasattr(celestial_body, field):
                setattr(celestial_body, field, value)
        
        # Set the updated timestamp
        celestial_body.updated_at = datetime.utcnow()
        
        # Commit the changes
        db.commit()
        db.refresh(celestial_body)
        
        logger.info(f"Updated celestial body {celestial_body.name} (ID: {body_id})")
        
        return celestial_body
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating celestial body {body_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update celestial body")

@app.get("/celestial-bodies/search/{name}", response_model=List[CelestialBodyResponse], tags=["Celestial Bodies"])
async def search_celestial_bodies(
    name: str = Path(..., description="Name to search for"),
    db: Session = Depends(get_db),
    limit: int = Query(50, le=200, description="Maximum number of results")
):
    """Search celestial bodies by name"""
    try:
        celestial_bodies = db.query(CelestialBody).filter(
            or_(
                CelestialBody.name.ilike(f"%{name}%"),
                CelestialBody.alternative_names.any(name)
            )
        ).limit(limit).all()
        
        return celestial_bodies
    except Exception as e:
        logger.error(f"Error searching celestial bodies: {e}")
        raise HTTPException(status_code=500, detail="Failed to search celestial bodies")

# Orbital parameters endpoints
@app.get("/orbital-parameters/{body_id}", response_model=OrbitalParametersResponse, tags=["Orbital Parameters"])
async def get_orbital_parameters(
    body_id: UUID = Path(..., description="Celestial body ID"),
    db: Session = Depends(get_db)
):
    """Get orbital parameters for a celestial body"""
    try:
        orbital_params = db.query(OrbitalParameters).filter(
            OrbitalParameters.celestial_body_id == body_id
        ).first()
        
        if not orbital_params:
            raise HTTPException(status_code=404, detail="Orbital parameters not found")
        
        return orbital_params
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting orbital parameters: {e}")
        raise HTTPException(status_code=500, detail="Failed to get orbital parameters")

# Physical characteristics endpoints
@app.get("/physical-characteristics/{body_id}", response_model=PhysicalCharacteristicsResponse, tags=["Physical Characteristics"])
async def get_physical_characteristics(
    body_id: UUID = Path(..., description="Celestial body ID"),
    db: Session = Depends(get_db)
):
    """Get physical characteristics for a celestial body"""
    try:
        physical_chars = db.query(PhysicalCharacteristics).filter(
            PhysicalCharacteristics.celestial_body_id == body_id
        ).first()
        
        if not physical_chars:
            raise HTTPException(status_code=404, detail="Physical characteristics not found")
        
        return physical_chars
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting physical characteristics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get physical characteristics")

# Stellar characteristics endpoints
@app.get("/stellar-characteristics/{body_id}", response_model=StellarCharacteristicsResponse, tags=["Stellar Characteristics"])
async def get_stellar_characteristics(
    body_id: UUID = Path(..., description="Celestial body ID"),
    db: Session = Depends(get_db)
):
    """Get stellar characteristics for a star"""
    try:
        stellar_chars = db.query(StellarCharacteristics).filter(
            StellarCharacteristics.celestial_body_id == body_id
        ).first()
        
        if not stellar_chars:
            raise HTTPException(status_code=404, detail="Stellar characteristics not found")
        
        return stellar_chars
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stellar characteristics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stellar characteristics")

# Spacecraft mission endpoints
@app.get("/spacecraft-missions/{body_id}", response_model=List[SpacecraftMissionResponse], tags=["Spacecraft Missions"])
async def get_spacecraft_missions(
    body_id: UUID = Path(..., description="Celestial body ID"),
    db: Session = Depends(get_db)
):
    """Get spacecraft missions for a celestial body"""
    try:
        missions = db.query(SpacecraftMission).filter(
            SpacecraftMission.celestial_body_id == body_id
        ).all()
        
        return missions
    except Exception as e:
        logger.error(f"Error getting spacecraft missions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get spacecraft missions")

# TLE elements endpoints
@app.get("/tle-elements/{body_id}", response_model=List[TLEElementsResponse], tags=["TLE Elements"])
async def get_tle_elements(
    body_id: UUID = Path(..., description="Celestial body ID"),
    db: Session = Depends(get_db),
    limit: int = Query(10, le=100, description="Maximum number of TLE elements")
):
    """Get TLE elements for a celestial body"""
    try:
        tle_elements = db.query(TLEElements).filter(
            TLEElements.celestial_body_id == body_id
        ).order_by(TLEElements.epoch.desc()).limit(limit).all()
        
        return tle_elements
    except Exception as e:
        logger.error(f"Error getting TLE elements: {e}")
        raise HTTPException(status_code=500, detail="Failed to get TLE elements")

# Simulation state endpoints
@app.get("/simulation-state/{body_id}", response_model=List[SimulationStateResponse], tags=["Simulation"])
async def get_simulation_state(
    body_id: UUID = Path(..., description="Celestial body ID"),
    db: Session = Depends(get_db),
    limit: int = Query(10, le=100, description="Maximum number of simulation states")
):
    """Get simulation states for a celestial body"""
    try:
        simulation_states = db.query(SimulationState).filter(
            SimulationState.celestial_body_id == body_id
        ).order_by(SimulationState.simulation_time.desc()).limit(limit).all()
        
        return simulation_states
    except Exception as e:
        logger.error(f"Error getting simulation states: {e}")
        raise HTTPException(status_code=500, detail="Failed to get simulation states")

# Solar system hierarchy endpoint
@app.get("/solar-system", tags=["Solar System"])
async def get_solar_system_hierarchy(db: Session = Depends(get_db)):
    """Get the complete solar system hierarchy"""
    try:
        # Get the Sun
        sun = db.query(CelestialBody).filter(CelestialBody.name == "Sun").first()
        if not sun:
            raise HTTPException(status_code=404, detail="Sun not found in database")
        
        # Build hierarchy recursively
        def build_hierarchy(body_id: UUID) -> Dict[str, Any]:
            body = db.query(CelestialBody).filter(CelestialBody.id == body_id).first()
            if not body:
                return None
            
            children = db.query(CelestialBody).filter(CelestialBody.parent_id == body_id).all()
            
            return {
                "id": str(body.id),
                "name": body.name,
                "type": body.type,
                "subtype": body.subtype,
                "mass_kg": body.mass_kg,
                "radius_km": body.radius_km,
                "children": [build_hierarchy(child.id) for child in children if build_hierarchy(child.id)]
            }
        
        hierarchy = build_hierarchy(sun.id)
        return {"solar_system": hierarchy}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting solar system hierarchy: {e}")
        raise HTTPException(status_code=500, detail="Failed to get solar system hierarchy")

# Update management endpoints
@app.get("/updates/latest", response_model=List[UpdateLogResponse], tags=["Updates"])
async def get_latest_updates(
    limit: int = Query(50, le=200, description="Number of latest updates to return"),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit)
):
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
):
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
):
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
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 