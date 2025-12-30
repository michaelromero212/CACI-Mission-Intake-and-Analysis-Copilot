"""
Reviews API - endpoints for analyst review workflow.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from db import get_session
from models.review import AnalystReview
from services import get_mission

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


class ReviewRequest(BaseModel):
    analyst_notes: Optional[str] = None
    approved: bool = False


class ReviewResponse(BaseModel):
    review_id: str
    mission_id: str
    analyst_notes: Optional[str]
    approved: bool
    reviewed_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/{mission_id}", response_model=ReviewResponse)
async def submit_review(
    mission_id: str,
    request: ReviewRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Submit or update analyst review for a mission.
    
    Supports human-in-the-loop workflow by allowing analysts to:
    - Add notes to the analysis
    - Approve or reject AI-generated results
    """
    # Verify mission exists
    mission = await get_mission(session, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    # Check for existing review
    result = await session.execute(
        select(AnalystReview).where(AnalystReview.mission_id == mission_id)
    )
    existing_review = result.scalar_one_or_none()
    
    if existing_review:
        # Update existing review
        existing_review.analyst_notes = request.analyst_notes
        existing_review.approved = request.approved
        existing_review.reviewed_at = datetime.utcnow()
        review = existing_review
    else:
        # Create new review
        review = AnalystReview(
            mission_id=mission_id,
            analyst_notes=request.analyst_notes,
            approved=request.approved
        )
        session.add(review)
    
    await session.commit()
    await session.refresh(review)
    
    return ReviewResponse(
        review_id=str(review.review_id),
        mission_id=str(review.mission_id),
        analyst_notes=review.analyst_notes,
        approved=review.approved,
        reviewed_at=review.reviewed_at
    )


@router.get("/{mission_id}", response_model=ReviewResponse)
async def get_review(
    mission_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get the analyst review for a mission.
    """
    result = await session.execute(
        select(AnalystReview).where(AnalystReview.mission_id == mission_id)
    )
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=404,
            detail="No review found for this mission"
        )
    
    return ReviewResponse(
        review_id=str(review.review_id),
        mission_id=str(review.mission_id),
        analyst_notes=review.analyst_notes,
        approved=review.approved,
        reviewed_at=review.reviewed_at
    )
