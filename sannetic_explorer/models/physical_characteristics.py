"""
Physical Characteristics model for Sannetic Explorer

Detailed physical characteristics and composition for celestial bodies.
"""

from typing import Optional, List
from uuid import uuid4
from datetime import datetime

from sqlalchemy import (
    Column, String, Float, Boolean, DateTime, JSON, ForeignKey, 
    Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from .base import Base


class PhysicalCharacteristics(Base):
    """Detailed physical characteristics and composition"""
    __tablename__ = "physical_characteristics"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    celestial_body_id: UUID = Column(UUID(as_uuid=True), ForeignKey("celestial_bodies.id"), nullable=False, unique=True)
    
    # Temperature data
    surface_temperature_k: Optional[float] = Column(Float, nullable=True)
    surface_temperature_min_k: Optional[float] = Column(Float, nullable=True)
    surface_temperature_max_k: Optional[float] = Column(Float, nullable=True)
    core_temperature_k: Optional[float] = Column(Float, nullable=True)
    
    # Atmospheric data
    has_atmosphere: bool = Column(Boolean, default=False)
    atmospheric_pressure_pa: Optional[float] = Column(Float, nullable=True)
    atmospheric_composition: Optional[dict] = Column(JSON, nullable=True)
    
    # Magnetic field
    has_magnetic_field: bool = Column(Boolean, default=False)
    magnetic_field_strength_t: Optional[float] = Column(Float, nullable=True)
    magnetic_dipole_moment_tm3: Optional[float] = Column(Float, nullable=True)
    
    # Internal structure
    internal_structure: Optional[dict] = Column(JSON, nullable=True)
    
    # Surface features
    surface_type: Optional[str] = Column(String(100), nullable=True)
    surface_features: Optional[List[str]] = Column(ARRAY(String), nullable=True)
    
    # Rings (for planets like Saturn)
    has_rings: bool = Column(Boolean, default=False)
    ring_system: Optional[dict] = Column(JSON, nullable=True)
    
    # Metadata
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    celestial_body = relationship("CelestialBody", backref=backref("physical_characteristics", uselist=False))

    def __repr__(self) -> str:
        return f"<PhysicalCharacteristics(celestial_body_id='{self.celestial_body_id}')>" 