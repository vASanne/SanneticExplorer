#!/usr/bin/env python3
"""
SQLAlchemy Models for Solar System Simulation
Comprehensive database models for celestial bodies, orbits, and physical properties
"""

from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, Text, JSON,
    ForeignKey, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from uuid import uuid4
from datetime import datetime
from typing import Optional, List

Base = declarative_base()

class CelestialBody(Base):
    """Main celestial body model with hierarchical relationships"""
    __tablename__ = "celestial_bodies"

    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    alternative_names = Column(ARRAY(String), nullable=True)  # Alternative names/designations
    
    # Classification
    type = Column(String(50), nullable=False, index=True)  # "star", "planet", "moon", "satellite", "spacecraft", "asteroid", "comet"
    subtype = Column(String(100), nullable=True)  # "terrestrial", "gas_giant", "ice_giant", "dwarf_planet", etc.
    
    # Hierarchical relationships
    parent_id = Column(UUID(as_uuid=True), ForeignKey("celestial_bodies.id"), nullable=True, index=True)
    
    # Basic physical properties
    mass_kg = Column(Float, nullable=True)
    radius_km = Column(Float, nullable=True)
    density_kg_m3 = Column(Float, nullable=True)
    surface_gravity_ms2 = Column(Float, nullable=True)
    escape_velocity_kms = Column(Float, nullable=True)
    
    # Orbital properties
    mean_distance_au = Column(Float, nullable=True)  # Mean distance from parent in AU
    orbital_speed_kms = Column(Float, nullable=True)  # Orbital speed in km/s
    
    # Visual properties
    color_hex = Column(String(7), nullable=True)  # #RRGGBB format
    texture_url = Column(String(500), nullable=True)
    albedo = Column(Float, nullable=True)  # Surface reflectivity (0-1)
    
    # Discovery information
    discovery_date = Column(String(100), nullable=True)
    discoverer = Column(String(255), nullable=True)
    discovery_method = Column(String(100), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    data_quality = Column(String(20), default="unknown")  # "excellent", "good", "fair", "poor", "unknown"
    data_sources = Column(JSON, nullable=True)  # Sources of data
    
    # Relationships
    parent = relationship("CelestialBody", remote_side=[id], backref=backref("children", lazy="dynamic"))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("type IN ('star', 'planet', 'moon', 'satellite', 'spacecraft', 'asteroid', 'comet', 'dwarf_planet')", name="valid_celestial_type"),
        CheckConstraint("mass_kg IS NULL OR mass_kg > 0", name="positive_mass"),
        CheckConstraint("radius_km IS NULL OR radius_km > 0", name="positive_radius"),
        CheckConstraint("albedo IS NULL OR (albedo >= 0 AND albedo <= 1)", name="valid_albedo"),
        Index("idx_celestial_body_type_parent", "type", "parent_id"),
    )

class OrbitalParameters(Base):
    """Detailed orbital parameters for celestial bodies"""
    __tablename__ = "orbital_parameters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    celestial_body_id = Column(UUID(as_uuid=True), ForeignKey("celestial_bodies.id"), nullable=False, unique=True)
    
    # Orbital elements
    semi_major_axis_km = Column(Float, nullable=True)
    eccentricity = Column(Float, nullable=True)
    inclination_degrees = Column(Float, nullable=True)
    longitude_ascending_node_degrees = Column(Float, nullable=True)
    argument_periapsis_degrees = Column(Float, nullable=True)
    mean_anomaly_degrees = Column(Float, nullable=True)
    
    # Orbital periods and speeds
    orbital_period_days = Column(Float, nullable=True)
    orbital_speed_kms = Column(Float, nullable=True)
    synodic_period_days = Column(Float, nullable=True)
    
    # Rotation
    rotation_period_hours = Column(Float, nullable=True)
    axial_tilt_degrees = Column(Float, nullable=True)
    
    # Distance measurements
    distance_from_parent_km = Column(Float, nullable=True)
    aphelion_km = Column(Float, nullable=True)
    perihelion_km = Column(Float, nullable=True)
    
    # Epoch and reference frame
    epoch = Column(String(50), nullable=True)  # e.g., "J2000"
    equinox = Column(String(50), nullable=True)
    
    # Perturbations and stability
    mutual_perturbations = Column(ARRAY(String), nullable=True)  # Names of bodies that perturb this orbit
    orbital_stability_score = Column(Float, nullable=True)  # 0-1 scale
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    celestial_body = relationship("CelestialBody", backref=backref("orbital_parameters", uselist=False))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("eccentricity IS NULL OR (eccentricity >= 0 AND eccentricity < 1)", name="valid_eccentricity"),
        CheckConstraint("inclination_degrees IS NULL OR (inclination_degrees >= 0 AND inclination_degrees <= 180)", name="valid_inclination"),
        CheckConstraint("orbital_period_days IS NULL OR orbital_period_days > 0", name="positive_orbital_period"),
    )

class PhysicalCharacteristics(Base):
    """Detailed physical characteristics and composition"""
    __tablename__ = "physical_characteristics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    celestial_body_id = Column(UUID(as_uuid=True), ForeignKey("celestial_bodies.id"), nullable=False, unique=True)
    
    # Temperature data
    surface_temperature_k = Column(Float, nullable=True)
    surface_temperature_min_k = Column(Float, nullable=True)
    surface_temperature_max_k = Column(Float, nullable=True)
    core_temperature_k = Column(Float, nullable=True)
    
    # Atmospheric data
    has_atmosphere = Column(Boolean, default=False)
    atmospheric_pressure_pa = Column(Float, nullable=True)
    atmospheric_composition = Column(JSON, nullable=True)  # Detailed composition as JSON
    
    # Magnetic field
    has_magnetic_field = Column(Boolean, default=False)
    magnetic_field_strength_t = Column(Float, nullable=True)
    magnetic_dipole_moment_tm3 = Column(Float, nullable=True)
    
    # Internal structure
    internal_structure = Column(JSON, nullable=True)  # Core, mantle, crust details
    
    # Surface features
    surface_type = Column(String(100), nullable=True)  # "rocky", "icy", "gaseous", etc.
    surface_features = Column(ARRAY(String), nullable=True)  # Craters, mountains, etc.
    
    # Rings (for planets like Saturn)
    has_rings = Column(Boolean, default=False)
    ring_system = Column(JSON, nullable=True)  # Ring details
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    celestial_body = relationship("CelestialBody", backref=backref("physical_characteristics", uselist=False))

class StellarCharacteristics(Base):
    """Specific characteristics for stars"""
    __tablename__ = "stellar_characteristics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    celestial_body_id = Column(UUID(as_uuid=True), ForeignKey("celestial_bodies.id"), nullable=False, unique=True)
    
    # Stellar classification
    spectral_type = Column(String(10), nullable=True)  # e.g., "G2V"
    luminosity_class = Column(String(10), nullable=True)  # e.g., "V", "III", "I"
    
    # Stellar parameters
    luminosity_lsun = Column(Float, nullable=True)  # Luminosity in solar units
    effective_temperature_k = Column(Float, nullable=True)
    absolute_magnitude = Column(Float, nullable=True)
    apparent_magnitude = Column(Float, nullable=True)
    color_index_bv = Column(Float, nullable=True)
    
    # Nuclear characteristics
    fusion_type = Column(String(100), nullable=True)  # "proton-proton chain", "CNO cycle", etc.
    core_temperature_k = Column(Float, nullable=True)
    core_pressure_pa = Column(Float, nullable=True)
    core_density_kgm3 = Column(Float, nullable=True)
    
    # Stellar evolution
    age_years = Column(Float, nullable=True)
    evolutionary_stage = Column(String(50), nullable=True)  # "main sequence", "red giant", etc.
    expected_lifetime_years = Column(Float, nullable=True)
    
    # Activity
    activity_cycle_period_years = Column(Float, nullable=True)
    last_solar_maximum = Column(String(20), nullable=True)
    last_solar_minimum = Column(String(20), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    celestial_body = relationship("CelestialBody", backref=backref("stellar_characteristics", uselist=False))

class SpacecraftMission(Base):
    """Mission information for spacecraft and satellites"""
    __tablename__ = "spacecraft_missions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    celestial_body_id = Column(UUID(as_uuid=True), ForeignKey("celestial_bodies.id"), nullable=False)
    
    # Mission details
    mission_name = Column(String(255), nullable=True)
    agency = Column(String(255), nullable=True)  # NASA, ESA, JAXA, etc.
    mission_type = Column(String(100), nullable=True)  # "orbiter", "lander", "rover", "flyby", etc.
    
    # Launch information
    launch_date = Column(DateTime(timezone=True), nullable=True)
    launch_site = Column(String(255), nullable=True)
    launch_vehicle = Column(String(255), nullable=True)
    
    # Mission status
    status = Column(String(50), nullable=True)  # "active", "inactive", "planned", "failed", "completed"
    mission_duration_days = Column(Integer, nullable=True)
    
    # Specifications
    mass_kg = Column(Float, nullable=True)
    dimensions_m = Column(String(100), nullable=True)  # "1.2x2.3x3.4"
    power_watts = Column(Float, nullable=True)
    propulsion_type = Column(String(100), nullable=True)
    
    # Payload and instruments
    payload = Column(ARRAY(String), nullable=True)
    instruments = Column(ARRAY(String), nullable=True)
    
    # Ground stations and communications
    ground_stations = Column(ARRAY(String), nullable=True)
    communication_band = Column(String(50), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    celestial_body = relationship("CelestialBody", backref=backref("spacecraft_missions", lazy="dynamic"))

class TLEElements(Base):
    """Two-Line Element sets for satellites and spacecraft"""
    __tablename__ = "tle_elements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    celestial_body_id = Column(UUID(as_uuid=True), ForeignKey("celestial_bodies.id"), nullable=False)
    
    # TLE identification
    norad_id = Column(String(20), nullable=True, index=True)
    international_designator = Column(String(20), nullable=True)
    
    # TLE data
    line1 = Column(String(69), nullable=False)
    line2 = Column(String(69), nullable=False)
    
    # Epoch information
    epoch = Column(DateTime(timezone=True), nullable=False)
    mean_motion_ddot = Column(Float, nullable=True)
    mean_motion_ddot2 = Column(Float, nullable=True)
    b_star = Column(Float, nullable=True)
    ephemeris_type = Column(Integer, nullable=True)
    element_set_number = Column(Integer, nullable=True)
    checksum_line1 = Column(Integer, nullable=True)
    checksum_line2 = Column(Integer, nullable=True)
    
    # Derived orbital elements
    inclination_degrees = Column(Float, nullable=True)
    right_ascension_degrees = Column(Float, nullable=True)
    eccentricity = Column(Float, nullable=True)
    argument_perigee_degrees = Column(Float, nullable=True)
    mean_anomaly_degrees = Column(Float, nullable=True)
    mean_motion_revs_per_day = Column(Float, nullable=True)
    revolution_number = Column(Integer, nullable=True)
    
    # Data quality
    data_source = Column(String(50), nullable=True)  # "celestrak", "space_track", "n2yo"
    data_quality = Column(String(20), default="unknown")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    celestial_body = relationship("CelestialBody", backref=backref("tle_elements", lazy="dynamic"))
    
    # Constraints
    __table_args__ = (
        Index("idx_tle_celestial_body_epoch", "celestial_body_id", "epoch"),
        Index("idx_tle_norad_epoch", "norad_id", "epoch"),
    )

class ExplorationHistory(Base):
    """Historical exploration and observation data"""
    __tablename__ = "exploration_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    celestial_body_id = Column(UUID(as_uuid=True), ForeignKey("celestial_bodies.id"), nullable=False)
    
    # Exploration events
    event_type = Column(String(50), nullable=False)  # "flyby", "orbit", "landing", "sample_return", "observation"
    event_date = Column(DateTime(timezone=True), nullable=True)
    
    # Mission details
    mission_name = Column(String(255), nullable=True)
    spacecraft_name = Column(String(255), nullable=True)
    agency = Column(String(255), nullable=True)
    
    # Event details
    distance_km = Column(Float, nullable=True)  # Closest approach distance
    duration_days = Column(Float, nullable=True)
    instruments_used = Column(ARRAY(String), nullable=True)
    
    # Results and discoveries
    discoveries = Column(Text, nullable=True)
    images_taken = Column(Integer, nullable=True)
    data_volume_gb = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    celestial_body = relationship("CelestialBody", backref=backref("exploration_history", lazy="dynamic"))
    
    # Constraints
    __table_args__ = (
        Index("idx_exploration_celestial_body_date", "celestial_body_id", "event_date"),
    )

class SimulationState(Base):
    """Current state for simulation purposes"""
    __tablename__ = "simulation_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    celestial_body_id = Column(UUID(as_uuid=True), ForeignKey("celestial_bodies.id"), nullable=False)
    
    # Position and velocity (in 3D space)
    position_x_km = Column(Float, nullable=True)
    position_y_km = Column(Float, nullable=True)
    position_z_km = Column(Float, nullable=True)
    velocity_x_kms = Column(Float, nullable=True)
    velocity_y_kms = Column(Float, nullable=True)
    velocity_z_kms = Column(Float, nullable=True)
    
    # Orientation
    rotation_angle_degrees = Column(Float, nullable=True)
    axial_tilt_degrees = Column(Float, nullable=True)
    
    # Simulation time
    simulation_time = Column(DateTime(timezone=True), nullable=False)
    time_step_seconds = Column(Float, nullable=True)
    
    # Accuracy and confidence
    position_accuracy_km = Column(Float, nullable=True)
    velocity_accuracy_kms = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0-1 scale
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    celestial_body = relationship("CelestialBody", backref=backref("simulation_states", lazy="dynamic"))
    
    # Constraints
    __table_args__ = (
        Index("idx_simulation_celestial_body_time", "celestial_body_id", "simulation_time"),
    )

class UpdateLog(Base):
    """Log of update script executions and their results"""
    __tablename__ = "update_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    script_name = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)  # "success", "error", "warning", "info"
    message = Column(Text, nullable=True)
    duration_sec = Column(Float, nullable=True)
    
    # Additional metadata
    log_level = Column(String(20), nullable=True)  # "DEBUG", "INFO", "WARNING", "ERROR"
    source_file = Column(String(255), nullable=True)  # Which log file this came from
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('success', 'error', 'warning', 'info')", name="valid_update_status"),
        CheckConstraint("duration_sec IS NULL OR duration_sec >= 0", name="non_negative_duration"),
        Index("idx_update_log_timestamp", "timestamp"),
        Index("idx_update_log_script_status", "script_name", "status"),
    )

# Additional indexes for performance
Index("idx_celestial_bodies_name_type", CelestialBody.name, CelestialBody.type)
Index("idx_celestial_bodies_parent_type", CelestialBody.parent_id, CelestialBody.type)
Index("idx_orbital_parameters_period", OrbitalParameters.orbital_period_days)
Index("idx_physical_characteristics_temperature", PhysicalCharacteristics.surface_temperature_k)
Index("idx_stellar_characteristics_spectral", StellarCharacteristics.spectral_type)
Index("idx_spacecraft_missions_status", SpacecraftMission.status)
Index("idx_tle_elements_quality", TLEElements.data_quality) 