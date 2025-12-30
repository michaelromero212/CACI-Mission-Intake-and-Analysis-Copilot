"""
Mission service - business logic for mission CRUD operations.
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from models.mission import Mission, MissionStatus, SourceType
from ingestion import parse_pdf, parse_csv, parse_text, normalize_content
import logging

logger = logging.getLogger(__name__)


async def create_mission_from_file(
    session: AsyncSession,
    file_content: bytes,
    filename: str,
    source_type: SourceType
) -> Mission:
    """
    Create a mission from uploaded file content.
    """
    # Parse based on source type
    if source_type == SourceType.PDF:
        parsed = parse_pdf(file_content, filename)
    elif source_type == SourceType.CSV:
        parsed = parse_csv(file_content, filename)
    elif source_type == SourceType.TEXT:
        # For TXT files, decode bytes to string and parse as text
        text_content = file_content.decode('utf-8', errors='replace')
        parsed = parse_text(text_content, filename)
    else:
        raise ValueError(f"Unsupported file type: {source_type}")
    
    # Normalize content
    normalized = normalize_content(parsed, source_type, filename=filename)
    
    # Create mission record
    mission = Mission(
        source_type=source_type.value if hasattr(source_type, 'value') else source_type,
        filename=filename,
        raw_content=parsed.get("text", ""),
        normalized_content=normalized["content"],
        status=MissionStatus.INGESTED.value if normalized["is_valid"] else MissionStatus.ERROR.value,
        mission_metadata=normalized["metadata"],
        error_message="; ".join(normalized["errors"]) if normalized["errors"] else None
    )
    
    session.add(mission)
    await session.commit()
    await session.refresh(mission)
    
    logger.info(f"Created mission {mission.mission_id} from {filename}")
    return mission


async def create_mission_from_text(
    session: AsyncSession,
    text_content: str,
    source_label: str = "text_input"
) -> Mission:
    """
    Create a mission from free-text input.
    """
    parsed = parse_text(text_content, source_label)
    normalized = normalize_content(parsed, SourceType.TEXT, source_label=source_label)
    
    mission = Mission(
        source_type=SourceType.TEXT.value,
        source_label=source_label,
        raw_content=text_content,
        normalized_content=normalized["content"],
        status=MissionStatus.INGESTED.value if normalized["is_valid"] else MissionStatus.ERROR.value,
        mission_metadata=normalized["metadata"],
        error_message="; ".join(normalized["errors"]) if normalized["errors"] else None
    )
    
    session.add(mission)
    await session.commit()
    await session.refresh(mission)
    
    logger.info(f"Created mission {mission.mission_id} from text input")
    return mission


async def get_mission(session: AsyncSession, mission_id: str) -> Optional[Mission]:
    """Get a mission by ID."""
    result = await session.execute(
        select(Mission).where(Mission.mission_id == mission_id)
    )
    return result.scalar_one_or_none()


async def get_all_missions(
    session: AsyncSession,
    limit: int = 100,
    offset: int = 0
) -> List[Mission]:
    """Get all missions with pagination."""
    result = await session.execute(
        select(Mission)
        .order_by(Mission.ingestion_timestamp.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def update_mission_status(
    session: AsyncSession,
    mission_id: str,
    status: str,
    error_message: Optional[str] = None
) -> Optional[Mission]:
    """Update mission status."""
    mission = await get_mission(session, mission_id)
    if mission:
        mission.status = status
        if error_message:
            mission.error_message = error_message
        await session.commit()
        await session.refresh(mission)
    return mission


async def delete_mission(session: AsyncSession, mission_id: str) -> bool:
    """Delete a mission and all related records."""
    mission = await get_mission(session, mission_id)
    if mission:
        await session.delete(mission)
        await session.commit()
        return True
    return False
