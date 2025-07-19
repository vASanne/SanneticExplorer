"""
Orbital Parameters model for Sannetic Explorer

Detailed orbital parameters for celestial bodies.
"""

from typing import Optional, List
from uuid import uuid4
from datetime import datetime

from sqlalchemy import (
    Column, String, Float, DateTime, ForeignKey, 
    Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from .base import Base


class OrbitalParameters(Base):
    """Detailed orbital parameters for celestial bodies"""
    __tablename__ = "orbital_parameters"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    celestial_body_id: UUID = Column(UUID(as_uuid=True), ForeignKey("celestial_bodies.id"), nullable=False, unique=True)
    
    # Orbital elements
    semi_major_axis_km: Optional[float] = Column(Float, nullable=True)
    eccentricity: Optional[float] = Column(Float, nullable=True)
    inclination_degrees: Optional[float] = Column(Float, nullable=True)
    longitude_ascending_node_degrees: Optional[float] = Column(Float, nullable=True)
    argument_periapsis_degrees: Optional[float] = Column(Float, nullable=True)
    mean_anomaly_degrees: Optional[float] = Column(Float, nullable=True)
    
    # Orbital periods and speeds
    orbital_period_days: Optional[float] = Column(Float, nullable=True)
    orbital_speed_kms: Optional[float] = Column(Float, nullable=True)
    synodic_period_days: Optional[float] = Column(Float, nullable=True)
    
    # Rotation
    rotation_period_hours: Optional[float] = Column(Float, nullable=True)
    axial_tilt_degrees: Optional[float] = Column(Float, nullable=True)
    
    # Distance measurements
    distance_from_parent_km: Optional[float] = Column(Float, nullable=True)
    aphelion_km: Optional[float] = Column(Float, nullable=True)
    perihelion_km: Optional[float] = Column(Float, nullable=True)
    
    # Epoch and reference frame
    epoch: Optional[str] = Column(String(50), nullable=True)
    equinox: Optional[str] = Column(String(50), nullable=True)
    
    # Perturbations and stability
    mutual_perturbations: Optional[List[str]] = Column(ARRAY(String), nullable=True)
    orbital_stability_score: Optional[float] = Column(Float, nullable=True)
    
    # Metadata
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    celestial_body = relationship("CelestialBody", backref=backref("orbital_parameters", uselist=False))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("eccentricity IS NULL OR (eccentricity >= 0 AND eccentricity < 1)", name="valid_eccentricity"),
        CheckConstraint("inclination_degrees IS NULL OR (inclination_degrees >= 0 AND inclination_degrees <= 180)", name="valid_inclination"),
        CheckConstraint("orbital_period_days IS NULL OR orbital_period_days > 0", name="positive_orbital_period"),
    )

    def __repr__(self) -> str:
        return f"<OrbitalParameters(celestial_body_id='{self.celestial_body_id}')>" 