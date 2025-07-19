"""
Spacecraft Mission model for Sannetic Explorer

Mission information for spacecraft and satellites.
"""

from typing import Optional, List
from uuid import uuid4
from datetime import datetime

from sqlalchemy import Column, String, Float, Boolean, DateTime, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from .base import Base


class SpacecraftMission(Base):
    """Mission information for spacecraft and satellites"""
    __tablename__ = "spacecraft_missions"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    celestial_body_id: UUID = Column(UUID(as_uuid=True), ForeignKey("celestial_bodies.id"), nullable=False)
    
    # Mission details
    mission_name: Optional[str] = Column(String(255), nullable=True)
    agency: Optional[str] = Column(String(255), nullable=True)
    mission_type: Optional[str] = Column(String(100), nullable=True)
    
    # Launch information
    launch_date: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    launch_site: Optional[str] = Column(String(255), nullable=True)
    launch_vehicle: Optional[str] = Column(String(255), nullable=True)
    
    # Mission status
    status: Optional[str] = Column(String(50), nullable=True)
    mission_duration_days: Optional[int] = Column(Integer, nullable=True)
    
    # Specifications
    mass_kg: Optional[float] = Column(Float, nullable=True)
    dimensions_m: Optional[str] = Column(String(100), nullable=True)
    power_watts: Optional[float] = Column(Float, nullable=True)
    propulsion_type: Optional[str] = Column(String(100), nullable=True)
    
    # Payload and instruments
    payload: Optional[List[str]] = Column(ARRAY(String), nullable=True)
    instruments: Optional[List[str]] = Column(ARRAY(String), nullable=True)
    
    # Ground stations and communications
    ground_stations: Optional[List[str]] = Column(ARRAY(String), nullable=True)
    communication_band: Optional[str] = Column(String(50), nullable=True)
    
    # Metadata
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    celestial_body = relationship("CelestialBody", backref=backref("spacecraft_missions", lazy="dynamic"))

    def __repr__(self) -> str:
        return f"<SpacecraftMission(mission_name='{self.mission_name}', celestial_body_id='{self.celestial_body_id}')>" 