"""
TLE Elements model for Sannetic Explorer

Two-Line Element sets for satellites and spacecraft.
"""

from typing import Optional
from uuid import uuid4
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from .base import Base


class TLEElements(Base):
    """Two-Line Element sets for satellites and spacecraft"""
    __tablename__ = "tle_elements"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    celestial_body_id: UUID = Column(UUID(as_uuid=True), ForeignKey("celestial_bodies.id"), nullable=False)
    
    # TLE identification
    norad_id: Optional[str] = Column(String(20), nullable=True, index=True)
    international_designator: Optional[str] = Column(String(20), nullable=True)
    
    # TLE data
    line1: str = Column(String(69), nullable=False)
    line2: str = Column(String(69), nullable=False)
    
    # Epoch information
    epoch: datetime = Column(DateTime(timezone=True), nullable=False)
    mean_motion_ddot: Optional[float] = Column(Float, nullable=True)
    mean_motion_ddot2: Optional[float] = Column(Float, nullable=True)
    b_star: Optional[float] = Column(Float, nullable=True)
    ephemeris_type: Optional[int] = Column(Integer, nullable=True)
    element_set_number: Optional[int] = Column(Integer, nullable=True)
    checksum_line1: Optional[int] = Column(Integer, nullable=True)
    checksum_line2: Optional[int] = Column(Integer, nullable=True)
    
    # Derived orbital elements
    inclination_degrees: Optional[float] = Column(Float, nullable=True)
    right_ascension_degrees: Optional[float] = Column(Float, nullable=True)
    eccentricity: Optional[float] = Column(Float, nullable=True)
    argument_perigee_degrees: Optional[float] = Column(Float, nullable=True)
    mean_anomaly_degrees: Optional[float] = Column(Float, nullable=True)
    mean_motion_revs_per_day: Optional[float] = Column(Float, nullable=True)
    revolution_number: Optional[int] = Column(Integer, nullable=True)
    
    # Data quality
    data_source: Optional[str] = Column(String(50), nullable=True)
    data_quality: str = Column(String(20), default="unknown")
    
    # Metadata
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    celestial_body = relationship("CelestialBody", backref=backref("tle_elements", lazy="dynamic"))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("eccentricity IS NULL OR (eccentricity >= 0 AND eccentricity < 1)", name="valid_tle_eccentricity"),
        CheckConstraint("inclination_degrees IS NULL OR (inclination_degrees >= 0 AND inclination_degrees <= 180)", name="valid_tle_inclination"),
        Index("idx_tle_epoch", "epoch"),
    )

    def __repr__(self) -> str:
        return f"<TLEElements(norad_id='{self.norad_id}', celestial_body_id='{self.celestial_body_id}')>" 