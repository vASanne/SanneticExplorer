"""
Celestial Body model for Sannetic Explorer

Main model for celestial bodies with hierarchical relationships and physical properties.
"""

from typing import Optional, List
from uuid import uuid4
from datetime import datetime

from sqlalchemy import (
    Column, String, Float, Boolean, DateTime, JSON, ForeignKey, 
    UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from .base import Base


class CelestialBody(Base):
    """Main celestial body model with hierarchical relationships"""
    __tablename__ = "celestial_bodies"

    # Primary identification
    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: str = Column(String(255), unique=True, nullable=False, index=True)
    alternative_names: Optional[List[str]] = Column(ARRAY(String), nullable=True)
    
    # Classification
    type: str = Column(String(50), nullable=False, index=True)
    subtype: Optional[str] = Column(String(100), nullable=True)
    
    # Hierarchical relationships
    parent_id: Optional[UUID] = Column(UUID(as_uuid=True), ForeignKey("celestial_bodies.id"), nullable=True, index=True)
    
    # Basic physical properties
    mass_kg: Optional[float] = Column(Float, nullable=True)
    radius_km: Optional[float] = Column(Float, nullable=True)
    density_kg_m3: Optional[float] = Column(Float, nullable=True)
    surface_gravity_ms2: Optional[float] = Column(Float, nullable=True)
    escape_velocity_kms: Optional[float] = Column(Float, nullable=True)
    
    # Orbital properties
    mean_distance_au: Optional[float] = Column(Float, nullable=True)
    orbital_speed_kms: Optional[float] = Column(Float, nullable=True)
    
    # Visual properties
    color_hex: Optional[str] = Column(String(7), nullable=True)
    texture_url: Optional[str] = Column(String(500), nullable=True)
    albedo: Optional[float] = Column(Float, nullable=True)
    
    # Discovery information
    discovery_date: Optional[str] = Column(String(100), nullable=True)
    discoverer: Optional[str] = Column(String(255), nullable=True)
    discovery_method: Optional[str] = Column(String(100), nullable=True)
    
    # Metadata
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=func.now())
    data_quality: str = Column(String(20), default="unknown")
    data_sources: Optional[dict] = Column(JSON, nullable=True)
    
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

    def __repr__(self) -> str:
        return f"<CelestialBody(name='{self.name}', type='{self.type}')>" 