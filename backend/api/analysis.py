"""
Analysis API - endpoints for executing and retrieving AI analysis.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

from db import get_session
from services import get_mission, run_analysis, get_analysis_result, get_all_analysis_results

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


# Response models
class AnalysisResponse(BaseModel):
    analysis_id: str
    mission_id: str
    summary_text: Optional[str]
    extracted_entities: List[Any]
    risk_level: Optional[str]
    explanation: Optional[str]
    llm_model_used: Optional[str]
    total_tokens: int
    estimated_cost: float
    confidence_score: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisCostInfo(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
    model: str


class AnalysisDetailResponse(AnalysisResponse):
    cost_info: AnalysisCostInfo


class AnalysisRequest(BaseModel):
    use_rag: bool = True


@router.post("/{mission_id}", response_model=AnalysisResponse)
async def execute_analysis(
    mission_id: str,
    request: AnalysisRequest = AnalysisRequest(),
    session: AsyncSession = Depends(get_session)
):
    """
    Execute AI analysis on a mission.
    
    This endpoint runs:
    - Summarization
    - Entity extraction
    - Risk classification
    - Natural language explanation
    
    Cost transparency: Token usage and cost estimates are included in the response.
    """
    # Verify mission exists
    mission = await get_mission(session, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    # Import AI components
    from ai.llm_client import get_llm_client
    from ai.rag_service import get_rag_service
    
    llm_client = get_llm_client()
    rag_service = get_rag_service() if request.use_rag else None
    
    # Run analysis
    result = await run_analysis(
        session=session,
        mission_id=mission_id,
        llm_client=llm_client,
        rag_service=rag_service
    )
    
    if not result:
        raise HTTPException(
            status_code=500,
            detail="Analysis failed. Check mission status for details."
        )
    
    return AnalysisResponse(
        analysis_id=str(result.analysis_id),
        mission_id=str(result.mission_id),
        summary_text=result.summary_text,
        extracted_entities=result.extracted_entities or [],
        risk_level=result.risk_level if isinstance(result.risk_level, str) else (result.risk_level.value if result.risk_level else None),
        explanation=result.explanation,
        llm_model_used=result.llm_model_used,
        total_tokens=result.total_tokens,
        estimated_cost=result.estimated_cost,
        confidence_score=result.confidence_score,
        created_at=result.created_at
    )


@router.get("/{mission_id}", response_model=AnalysisDetailResponse)
async def get_analysis(
    mission_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get the latest analysis result for a mission.
    
    Includes detailed cost transparency information.
    """
    result = await get_analysis_result(session, mission_id)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="No analysis found for this mission"
        )
    
    return AnalysisDetailResponse(
        analysis_id=str(result.analysis_id),
        mission_id=str(result.mission_id),
        summary_text=result.summary_text,
        extracted_entities=result.extracted_entities or [],
        risk_level=result.risk_level if isinstance(result.risk_level, str) else (result.risk_level.value if result.risk_level else None),
        explanation=result.explanation,
        llm_model_used=result.llm_model_used,
        total_tokens=result.total_tokens,
        estimated_cost=result.estimated_cost,
        confidence_score=result.confidence_score,
        created_at=result.created_at,
        cost_info=AnalysisCostInfo(
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            total_tokens=result.total_tokens,
            estimated_cost=result.estimated_cost,
            model=result.llm_model_used or "unknown"
        )
    )


@router.get("/{mission_id}/history", response_model=List[AnalysisResponse])
async def get_analysis_history(
    mission_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get all analysis runs for a mission (supports re-analysis).
    """
    results = await get_all_analysis_results(session, mission_id)
    
    return [
        AnalysisResponse(
            analysis_id=str(r.analysis_id),
            mission_id=str(r.mission_id),
            summary_text=r.summary_text,
            extracted_entities=r.extracted_entities or [],
            risk_level=r.risk_level if isinstance(r.risk_level, str) else (r.risk_level.value if r.risk_level else None),
            explanation=r.explanation,
            llm_model_used=r.llm_model_used,
            total_tokens=r.total_tokens,
            estimated_cost=r.estimated_cost,
            confidence_score=r.confidence_score,
            created_at=r.created_at
        )
        for r in results
    ]
