"""
AssignMind — Assignment Service

Service layer logic for parsing uploaded documents and routing them
through the Prompt Engine to generate structured JSON summaries.
"""

from uuid import UUID
import structlog
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile

from app.models.assignment import Assignment
from app.utils.pdf_parser import extract_document_text
from app.services.ai_service import AIService
from app.schemas.ai import AssignmentSummary

logger = structlog.get_logger()

async def upload_and_analyze_assignment(
    db: AsyncSession,
    workspace_id: UUID,
    user_id: UUID,
    file: UploadFile,
    ai_service: AIService
) -> Assignment:
    """Parse upload, analyze via AI, store as new version."""
    content = await file.read()
    raw_text = extract_document_text(file.filename, content)
    
    lang = ai_service._detect_language(raw_text)
    
    summary: AssignmentSummary = await ai_service.analyze_assignment(
        db=db, user_id=user_id, content=raw_text
    )
    
    return await _store_new_assignment_version(
        db=db,
        workspace_id=workspace_id,
        user_id=user_id,
        filename=file.filename,
        raw_text=raw_text,
        summary=summary,
        lang=lang
    )

async def _store_new_assignment_version(
    db: AsyncSession,
    workspace_id: UUID,
    user_id: UUID,
    filename: str,
    raw_text: str,
    summary: AssignmentSummary,
    lang: str
) -> Assignment:
    """Find current version and increment to store new row safely."""
    result = await db.execute(
        select(func.max(Assignment.version))
        .where(Assignment.workspace_id == workspace_id)
    )
    max_version = result.scalar() or 0
    next_version = max_version + 1
    
    assignment = Assignment(
        workspace_id=workspace_id,
        version=next_version,
        original_filename=filename,
        raw_text=raw_text,
        structured_summary=summary.model_dump(),
        detected_language=lang,
        uploaded_by=user_id
    )
    
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    
    logger.info(
        "assignment_uploaded", 
        workspace_id=str(workspace_id), 
        version=next_version
    )
    return assignment

async def get_latest_assignment(
    db: AsyncSession, workspace_id: UUID
) -> Assignment | None:
    """Fetch the assignment with the highest version for a workspace."""
    result = await db.execute(
        select(Assignment)
        .where(Assignment.workspace_id == workspace_id)
        .order_by(Assignment.version.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()

async def get_assignments(
    db: AsyncSession, workspace_id: UUID
) -> list[Assignment]:
    """Fetch all assignments for a workspace, ordered by version descending."""
    result = await db.execute(
        select(Assignment)
        .where(Assignment.workspace_id == workspace_id)
        .order_by(Assignment.version.desc())
    )
    return list(result.scalars().all())
