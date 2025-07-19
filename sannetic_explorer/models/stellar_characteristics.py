"""
Stellar Characteristics model for Sannetic Explorer

Specific characteristics for stars.
"""

from typing import Optional
from uuid import uuid4
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from .base import Base


class StellarCharacteristics(Base):
    """Specific characteristics for stars"""
    __tablename__ = "stellar_characteristics"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    celestial_body_id: UUID = Column(UUID(as_uuid=True), ForeignKey("celestial_bodies.id"), nullable=False, unique=True)
    
    # Stellar classification
    spectral_type: Optional[str] = Column(String(10), nullable=True)
    luminosity_class: Optional[str] = Column(String(10), nullable=True)
    
    # Stellar parameters
    luminosity_lsun: Optional[float] = Column(Float, nullable=True)
    effective_temperature_k: Optional[float] = Column(Float, nullable=True)
    absolute_magnitude: Optional[float] = Column(Float, nullable=True)
    apparent_magnitude: Optional[float] = Column(Float, nullable=True)
    color_index_bv: Optional[float] = Column(Float, nullable=True)
    
    # Nuclear characteristics
    fusion_type: Optional[str] = Column(String(100), nullable=True)
    core_temperature_k: Optional[float] = Column(Float, nullable=True)
    core_pressure_pa: Optional[float] = Column(Float, nullable=True)
    core_density_kgm3: Optional[float] = Column(Float, nullable=True)
    
    # Stellar evolution
    age_years: Optional[float] = Column(Float, nullable=True)
    evolutionary_stage: Optional[str] = Column(String(50), nullable=True)
    expected_lifetime_years: Optional[float] = Column(Float, nullable=True)
    
    # Activity
    activity_cycle_period_years: Optional[float] = Column(Float, nullable=True)
    last_solar_maximum: Optional[str] = Column(String(20), nullable=True)
    last_solar_minimum: Optional[str] = Column(String(20), nullable=True)
    
    # Metadata
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    celestial_body = relationship("CelestialBody", backref=backref("stellar_characteristics", uselist=False))

    def __repr__(self) -> str:
        return f"<StellarCharacteristics(celestial_body_id='{self.celestial_body_id}')>" 