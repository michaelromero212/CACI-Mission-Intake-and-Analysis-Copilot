"""
Analytics API endpoints for dashboard data.
Provides aggregated mission statistics, trends, and risk distribution.
"""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, case, extract
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_session
from models.mission import Mission
from models.analysis import AnalysisResult

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# ============== Response Models ==============

class AnalyticsSummary(BaseModel):
    """Overall analytics summary."""
    total_missions: int
    total_analyzed: int
    total_pending: int
    total_errors: int
    total_tokens_used: int
    total_estimated_cost: float
    avg_processing_time_ms: Optional[float]
    avg_confidence_score: Optional[float]


class RiskDistribution(BaseModel):
    """Risk level distribution."""
    low: int
    medium: int
    high: int
    critical: int
    unknown: int


class DailyTrend(BaseModel):
    """Daily trend data point."""
    date: str
    mission_count: int
    tokens_used: int
    estimated_cost: float
    avg_processing_time_ms: Optional[float]


class TrendsResponse(BaseModel):
    """Trends response with daily data."""
    days: List[DailyTrend]
    period_start: str
    period_end: str


# ============== Endpoints ==============

@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    session: AsyncSession = Depends(get_session)
):
    """
    Get overall analytics summary.
    Returns aggregated stats across all missions and analyses.
    """
    # Count missions by status
    from sqlalchemy import select
    
    total_query = select(func.count(Mission.mission_id))
    total_result = await session.execute(total_query)
    total_missions = total_result.scalar() or 0
    
    analyzed_query = select(func.count(Mission.mission_id)).where(Mission.status == 'ANALYZED')
    analyzed_result = await session.execute(analyzed_query)
    total_analyzed = analyzed_result.scalar() or 0
    
    pending_query = select(func.count(Mission.mission_id)).where(
        Mission.status.in_(['PENDING', 'INGESTED', 'ANALYZING'])
    )
    pending_result = await session.execute(pending_query)
    total_pending = pending_result.scalar() or 0
    
    error_query = select(func.count(Mission.mission_id)).where(Mission.status == 'ERROR')
    error_result = await session.execute(error_query)
    total_errors = error_result.scalar() or 0
    
    # Aggregate analysis stats
    analysis_stats = select(
        func.coalesce(func.sum(AnalysisResult.total_tokens), 0).label('total_tokens'),
        func.coalesce(func.sum(AnalysisResult.estimated_cost), 0.0).label('total_cost'),
        func.avg(AnalysisResult.processing_time_ms).label('avg_processing_time'),
        func.avg(AnalysisResult.confidence_score).label('avg_confidence')
    )
    stats_result = await session.execute(analysis_stats)
    stats = stats_result.first()
    
    return AnalyticsSummary(
        total_missions=total_missions,
        total_analyzed=total_analyzed,
        total_pending=total_pending,
        total_errors=total_errors,
        total_tokens_used=int(stats.total_tokens) if stats.total_tokens else 0,
        total_estimated_cost=float(stats.total_cost) if stats.total_cost else 0.0,
        avg_processing_time_ms=float(stats.avg_processing_time) if stats.avg_processing_time else None,
        avg_confidence_score=float(stats.avg_confidence) if stats.avg_confidence else None
    )


@router.get("/risk-distribution", response_model=RiskDistribution)
async def get_risk_distribution(
    session: AsyncSession = Depends(get_session)
):
    """
    Get distribution of missions by risk level.
    """
    from sqlalchemy import select
    
    # Count by risk level
    query = select(
        AnalysisResult.risk_level,
        func.count(AnalysisResult.analysis_id).label('count')
    ).group_by(AnalysisResult.risk_level)
    
    result = await session.execute(query)
    rows = result.all()
    
    # Build distribution
    distribution = {
        'low': 0,
        'medium': 0,
        'high': 0,
        'critical': 0,
        'unknown': 0
    }
    
    for row in rows:
        risk_level = (row.risk_level or 'unknown').lower()
        if risk_level in distribution:
            distribution[risk_level] = row.count
        else:
            distribution['unknown'] += row.count
    
    return RiskDistribution(**distribution)


@router.get("/trends", response_model=TrendsResponse)
async def get_analytics_trends(
    days: int = Query(default=30, ge=1, le=365),
    session: AsyncSession = Depends(get_session)
):
    """
    Get daily trends for the specified number of days.
    """
    from sqlalchemy import select, cast, Date
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Query missions grouped by date
    query = select(
        func.date(Mission.ingestion_timestamp).label('date'),
        func.count(Mission.mission_id).label('mission_count')
    ).where(
        Mission.ingestion_timestamp >= start_date
    ).group_by(
        func.date(Mission.ingestion_timestamp)
    ).order_by(
        func.date(Mission.ingestion_timestamp)
    )
    
    mission_result = await session.execute(query)
    mission_rows = mission_result.all()
    
    # Query analysis stats grouped by date
    analysis_query = select(
        func.date(AnalysisResult.created_at).label('date'),
        func.coalesce(func.sum(AnalysisResult.total_tokens), 0).label('tokens'),
        func.coalesce(func.sum(AnalysisResult.estimated_cost), 0.0).label('cost'),
        func.avg(AnalysisResult.processing_time_ms).label('avg_processing_time')
    ).where(
        AnalysisResult.created_at >= start_date
    ).group_by(
        func.date(AnalysisResult.created_at)
    )
    
    analysis_result = await session.execute(analysis_query)
    analysis_rows = {str(row.date): row for row in analysis_result.all()}
    
    # Combine data
    daily_trends = []
    for row in mission_rows:
        date_str = str(row.date)
        analysis_data = analysis_rows.get(date_str)
        
        daily_trends.append(DailyTrend(
            date=date_str,
            mission_count=row.mission_count,
            tokens_used=int(analysis_data.tokens) if analysis_data else 0,
            estimated_cost=float(analysis_data.cost) if analysis_data else 0.0,
            avg_processing_time_ms=float(analysis_data.avg_processing_time) if analysis_data and analysis_data.avg_processing_time else None
        ))
    
    return TrendsResponse(
        days=daily_trends,
        period_start=start_date.strftime('%Y-%m-%d'),
        period_end=end_date.strftime('%Y-%m-%d')
    )


# ============== New Command Center Endpoints ==============

class EntityTypeCount(BaseModel):
    """Entity type with count."""
    entity_type: str
    count: int


class EntityBreakdownResponse(BaseModel):
    """Entity type breakdown."""
    entities: List[EntityTypeCount]
    total_entities: int


class ReviewStatusResponse(BaseModel):
    """Review status counts."""
    pending_review: int
    approved: int
    not_reviewed: int
    total: int


class HighRiskMission(BaseModel):
    """High risk mission summary."""
    mission_id: str
    source_label: str
    risk_level: str
    summary: Optional[str]
    ingestion_timestamp: str
    confidence_score: Optional[float]


class HighRiskMissionsResponse(BaseModel):
    """High risk missions list."""
    missions: List[HighRiskMission]
    total_high_risk: int


@router.get("/entity-breakdown", response_model=EntityBreakdownResponse)
async def get_entity_breakdown(
    session: AsyncSession = Depends(get_session)
):
    """
    Get breakdown of extracted entities by type.
    Aggregates entity types across all analyses.
    """
    from sqlalchemy import select
    import json
    
    # Get all analyses with entities
    query = select(AnalysisResult.extracted_entities)
    result = await session.execute(query)
    rows = result.all()
    
    # Count entity types
    type_counts = {}
    total = 0
    
    for row in rows:
        entities = row.extracted_entities
        if entities:
            # Handle both JSON string and list
            if isinstance(entities, str):
                try:
                    entities = json.loads(entities)
                except:
                    continue
            
            for entity in entities:
                if isinstance(entity, dict) and 'type' in entity:
                    entity_type = entity['type'].upper()
                    type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
                    total += 1
    
    # Sort by count descending
    sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
    
    return EntityBreakdownResponse(
        entities=[EntityTypeCount(entity_type=t, count=c) for t, c in sorted_types],
        total_entities=total
    )


@router.get("/review-status", response_model=ReviewStatusResponse)
async def get_review_status(
    session: AsyncSession = Depends(get_session)
):
    """
    Get review status counts across all missions.
    """
    from sqlalchemy import select
    from models.review import AnalystReview
    
    # Get all missions
    total_query = select(func.count(Mission.mission_id))
    total_result = await session.execute(total_query)
    total = total_result.scalar() or 0
    
    # Get approved count
    approved_query = select(func.count(AnalystReview.review_id)).where(
        AnalystReview.approved == True
    )
    approved_result = await session.execute(approved_query)
    approved = approved_result.scalar() or 0
    
    # Get reviewed but not approved count
    pending_review_query = select(func.count(AnalystReview.review_id)).where(
        AnalystReview.approved == False
    )
    pending_result = await session.execute(pending_review_query)
    pending_review = pending_result.scalar() or 0
    
    # Calculate not reviewed
    reviewed_total = approved + pending_review
    not_reviewed = max(0, total - reviewed_total)
    
    return ReviewStatusResponse(
        pending_review=pending_review,
        approved=approved,
        not_reviewed=not_reviewed,
        total=total
    )


@router.get("/high-risk-missions", response_model=HighRiskMissionsResponse)
async def get_high_risk_missions(
    limit: int = Query(default=5, ge=1, le=20),
    session: AsyncSession = Depends(get_session)
):
    """
    Get recent high-risk and critical-risk missions.
    """
    from sqlalchemy import select
    from sqlalchemy.orm import joinedload
    
    # Query for high/critical risk analyses with their missions
    query = select(AnalysisResult, Mission).join(
        Mission, AnalysisResult.mission_id == Mission.mission_id
    ).where(
        AnalysisResult.risk_level.in_(['HIGH', 'CRITICAL', 'high', 'critical'])
    ).order_by(
        Mission.ingestion_timestamp.desc()
    ).limit(limit)
    
    result = await session.execute(query)
    rows = result.all()
    
    missions = []
    for analysis, mission in rows:
        # Truncate summary if too long
        summary = analysis.summary
        if summary and len(summary) > 150:
            summary = summary[:150] + '...'
        
        missions.append(HighRiskMission(
            mission_id=str(mission.mission_id),
            source_label=mission.source_label or 'Unknown',
            risk_level=analysis.risk_level.upper() if analysis.risk_level else 'UNKNOWN',
            summary=summary,
            ingestion_timestamp=mission.ingestion_timestamp.strftime('%Y-%m-%d %H:%M'),
            confidence_score=analysis.confidence_score
        ))
    
    # Count total high risk
    count_query = select(func.count(AnalysisResult.analysis_id)).where(
        AnalysisResult.risk_level.in_(['HIGH', 'CRITICAL', 'high', 'critical'])
    )
    count_result = await session.execute(count_query)
    total = count_result.scalar() or 0
    
    return HighRiskMissionsResponse(
        missions=missions,
        total_high_risk=total
    )

