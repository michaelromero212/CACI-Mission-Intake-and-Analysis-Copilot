"""
Mission model - stores ingested mission records.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.orm import relationship
import uuid
import enum

from db.database import Base


class SourceType(str, enum.Enum):
    """Source type for mission intake."""
    PDF = "pdf"
    CSV = "csv"
    TEXT = "text"


class MissionStatus(str, enum.Enum):
    """Status of mission processing."""
    PENDING = "pending"
    INGESTED = "ingested"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    ERROR = "error"


class Mission(Base):
    """
    Mission intake records.
    
    Stores metadata about ingested mission inputs (PDFs, CSVs, text).
    """
    __tablename__ = "missions"
    
    # Use String for UUID to ensure SQLite compatibility
    mission_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_type = Column(String(10), nullable=False)
    filename = Column(String(255), nullable=True)
    source_label = Column(String(255), nullable=True)
    raw_content = Column(Text, nullable=True)
    normalized_content = Column(Text, nullable=True)
    ingestion_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(20), default="pending")
    mission_metadata = Column(JSON, default=dict)  # Renamed to avoid SQLAlchemy reserved name
    error_message = Column(Text, nullable=True)
    
    # Relationships
    analysis_results = relationship("AnalysisResult", back_populates="mission", cascade="all, delete-orphan")
    reviews = relationship("AnalystReview", back_populates="mission", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Mission {self.mission_id} - {self.source_type}>"
