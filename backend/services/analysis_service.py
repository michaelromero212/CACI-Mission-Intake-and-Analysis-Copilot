"""
Analysis service - orchestrates AI analysis workflow.
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.mission import Mission, MissionStatus
from models.analysis import AnalysisResult, RiskLevel
from services.mission_service import get_mission, update_mission_status
import logging

logger = logging.getLogger(__name__)


async def run_analysis(
    session: AsyncSession,
    mission_id: str,
    llm_client=None,
    rag_service=None
) -> Optional[AnalysisResult]:
    """
    Execute AI analysis on a mission.
    
    Args:
        session: Database session
        mission_id: Mission to analyze
        llm_client: LLM client for AI analysis
        rag_service: RAG service for context retrieval
        
    Returns:
        AnalysisResult if successful, None otherwise
    """
    mission = await get_mission(session, mission_id)
    if not mission:
        logger.error(f"Mission {mission_id} not found")
        return None
    
    if not mission.normalized_content:
        logger.error(f"Mission {mission_id} has no content to analyze")
        return None
    
    # Update status to analyzing
    await update_mission_status(session, mission_id, MissionStatus.ANALYZING.value)
    
    try:
        # Import here to avoid circular imports
        from ai.analyzer import analyze_content
        
        # Run analysis
        analysis_data = await analyze_content(
            content=mission.normalized_content,
            llm_client=llm_client,
            rag_service=rag_service
        )
        
        # Create analysis result
        result = AnalysisResult(
            mission_id=mission_id,
            summary_text=analysis_data.get("summary", ""),
            extracted_entities=analysis_data.get("entities", []),
            risk_level=analysis_data.get("risk_level", "medium"),
            explanation=analysis_data.get("explanation", ""),
            llm_model_used=analysis_data.get("model", ""),
            input_tokens=analysis_data.get("input_tokens", 0),
            output_tokens=analysis_data.get("output_tokens", 0),
            total_tokens=analysis_data.get("total_tokens", 0),
            estimated_cost=analysis_data.get("estimated_cost", 0.0),
            confidence_score=analysis_data.get("confidence_score", 0.75)
        )
        
        session.add(result)
        await update_mission_status(session, mission_id, MissionStatus.ANALYZED.value)
        await session.commit()
        await session.refresh(result)
        
        logger.info(f"Completed analysis for mission {mission_id}")
        return result
        
    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        logger.error(f"Mission {mission_id}: {error_msg}")
        await update_mission_status(session, mission_id, MissionStatus.ERROR.value, error_msg)
        return None


async def get_analysis_result(
    session: AsyncSession,
    mission_id: str
) -> Optional[AnalysisResult]:
    """Get the latest analysis result for a mission."""
    result = await session.execute(
        select(AnalysisResult)
        .where(AnalysisResult.mission_id == mission_id)
        .order_by(AnalysisResult.created_at.desc())
    )
    return result.scalar_one_or_none()


async def get_all_analysis_results(
    session: AsyncSession,
    mission_id: str
) -> list:
    """Get all analysis results for a mission."""
    result = await session.execute(
        select(AnalysisResult)
        .where(AnalysisResult.mission_id == mission_id)
        .order_by(AnalysisResult.created_at.desc())
    )
    return result.scalars().all()
