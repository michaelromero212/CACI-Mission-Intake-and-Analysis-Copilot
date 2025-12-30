"""
Missions API - endpoints for file upload, text submission, and mission retrieval.
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from db import get_session
from models.mission import SourceType, MissionStatus
from services import (
    create_mission_from_file,
    create_mission_from_text,
    get_mission,
    get_all_missions,
    delete_mission
)

router = APIRouter(prefix="/api/missions", tags=["missions"])


# Pydantic response models
class MissionResponse(BaseModel):
    mission_id: str
    source_type: str
    filename: Optional[str]
    source_label: Optional[str]
    status: str
    ingestion_timestamp: datetime
    metadata: dict
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class MissionDetailResponse(MissionResponse):
    normalized_content: Optional[str]


class TextSubmissionRequest(BaseModel):
    content: str
    source_label: Optional[str] = "text_input"


class MissionListResponse(BaseModel):
    missions: List[MissionResponse]
    total: int


@router.post("/upload", response_model=MissionResponse)
async def upload_file(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Upload a PDF, CSV, or TXT file for mission intake.
    """
    # Validate file type
    filename = file.filename or "unknown"
    if filename.lower().endswith(".pdf"):
        source_type = SourceType.PDF
    elif filename.lower().endswith(".csv"):
        source_type = SourceType.CSV
    elif filename.lower().endswith(".txt"):
        source_type = SourceType.TEXT
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload PDF, CSV, or TXT files."
        )
    
    # Read file content
    content = await file.read()
    
    # Create mission
    mission = await create_mission_from_file(
        session=session,
        file_content=content,
        filename=filename,
        source_type=source_type
    )
    
    return MissionResponse(
        mission_id=str(mission.mission_id),
        source_type=mission.source_type,
        filename=mission.filename,
        source_label=mission.source_label,
        status=mission.status,
        ingestion_timestamp=mission.ingestion_timestamp,
        metadata=mission.mission_metadata or {},
        error_message=mission.error_message
    )


@router.post("/text", response_model=MissionResponse)
async def submit_text(
    request: TextSubmissionRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Submit free-text content for mission intake.
    """
    if not request.content.strip():
        raise HTTPException(
            status_code=400,
            detail="Text content cannot be empty."
        )
    
    mission = await create_mission_from_text(
        session=session,
        text_content=request.content,
        source_label=request.source_label
    )
    
    return MissionResponse(
        mission_id=str(mission.mission_id),
        source_type=mission.source_type,
        filename=mission.filename,
        source_label=mission.source_label,
        status=mission.status,
        ingestion_timestamp=mission.ingestion_timestamp,
        metadata=mission.mission_metadata or {},
        error_message=mission.error_message
    )


@router.get("", response_model=MissionListResponse)
async def list_missions(
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session)
):
    """
    Get all missions with pagination.
    """
    missions = await get_all_missions(session, limit=limit, offset=offset)
    
    return MissionListResponse(
        missions=[
            MissionResponse(
                mission_id=str(m.mission_id),
                source_type=m.source_type,
                filename=m.filename,
                source_label=m.source_label,
                status=m.status,
                ingestion_timestamp=m.ingestion_timestamp,
                metadata=m.mission_metadata or {},
                error_message=m.error_message
            )
            for m in missions
        ],
        total=len(missions)
    )


@router.get("/{mission_id}", response_model=MissionDetailResponse)
async def get_mission_detail(
    mission_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get a specific mission by ID with full content.
    """
    mission = await get_mission(session, mission_id)
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    return MissionDetailResponse(
        mission_id=str(mission.mission_id),
        source_type=mission.source_type,
        filename=mission.filename,
        source_label=mission.source_label,
        status=mission.status,
        ingestion_timestamp=mission.ingestion_timestamp,
        metadata=mission.mission_metadata or {},
        error_message=mission.error_message,
        normalized_content=mission.normalized_content
    )


@router.delete("/{mission_id}")
async def delete_mission_endpoint(
    mission_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a mission and all associated records.
    """
    success = await delete_mission(session, mission_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    return {"message": "Mission deleted successfully"}
