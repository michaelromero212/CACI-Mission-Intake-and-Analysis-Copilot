"""
Analysis result model - stores AI analysis outputs.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, JSON, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
import uuid
import enum

from db.database import Base


class RiskLevel(str, enum.Enum):
    """Risk/priority classification levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnalysisResult(Base):
    """
    AI analysis results.
    
    Stores LLM-generated analysis including summaries, entities,
    classifications, and cost transparency data.
    """
    __tablename__ = "analysis_results"
    
    # Use String for UUID to ensure SQLite compatibility
    analysis_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mission_id = Column(String(36), ForeignKey("missions.mission_id", ondelete="CASCADE"), nullable=False)
    
    # AI-generated content
    summary_text = Column(Text, nullable=True)
    extracted_entities = Column(JSON, default=list)
    risk_level = Column(String(20), nullable=True)
    explanation = Column(Text, nullable=True)
    
    # Model metadata
    llm_model_used = Column(String(100), nullable=True)
    
    # Cost transparency
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    
    # Confidence indicator (heuristic-based)
    confidence_score = Column(Float, nullable=True)
    
    # Processing time in milliseconds
    processing_time_ms = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    mission = relationship("Mission", back_populates="analysis_results")
    
    def __repr__(self):
        return f"<AnalysisResult {self.analysis_id} for Mission {self.mission_id}>"
