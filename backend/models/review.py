"""
Analyst review model - stores human-in-the-loop feedback.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Boolean, DateTime, Text, String, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from db.database import Base


class AnalystReview(Base):
    """
    Analyst review state.
    
    Supports human-in-the-loop workflows by allowing analysts
    to add notes and approve/reject AI-generated analysis.
    """
    __tablename__ = "analyst_reviews"
    
    # Use String for UUID to ensure SQLite compatibility
    review_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mission_id = Column(String(36), ForeignKey("missions.mission_id", ondelete="CASCADE"), nullable=False)
    
    analyst_notes = Column(Text, nullable=True)
    approved = Column(Boolean, default=False)
    reviewed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    mission = relationship("Mission", back_populates="reviews")
    
    def __repr__(self):
        return f"<AnalystReview {self.review_id} - {'Approved' if self.approved else 'Pending'}>"
