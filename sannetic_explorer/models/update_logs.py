"""
Update Log model for Sannetic Explorer

Model for tracking update script executions and their results.
"""

from typing import Optional
from uuid import uuid4
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, Text, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base


class UpdateLog(Base):
    """Log of update script executions and their results"""
    __tablename__ = "update_logs"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    timestamp: datetime = Column(DateTime(timezone=True), nullable=False, default=func.now())
    script_name: str = Column(String(255), nullable=False, index=True)
    status: str = Column(String(50), nullable=False, index=True)
    message: Optional[str] = Column(Text, nullable=True)
    duration_sec: Optional[float] = Column(Float, nullable=True)
    
    # Additional metadata
    log_level: Optional[str] = Column(String(20), nullable=True)
    source_file: Optional[str] = Column(String(255), nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('success', 'error', 'warning', 'info')", name="valid_update_status"),
        CheckConstraint("duration_sec IS NULL OR duration_sec >= 0", name="non_negative_duration"),
        Index("idx_update_log_timestamp", "timestamp"),
        Index("idx_update_log_script_status", "script_name", "status"),
    )

    def __repr__(self) -> str:
        return f"<UpdateLog(script='{self.script_name}', status='{self.status}', timestamp='{self.timestamp}')>" 