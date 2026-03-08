"""
AssignMind — Assignments Router

Upload endpoint requiring Team Leader role and rate limit checks.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_team_leader
from app.models.workspace_member import WorkspaceMember
from app.schemas.assignment import AssignmentResponse
from app.services import assignment_service
from app.utils.rate_limit import rate_limiter, RateLimitExceeded
from app.config import get_settings, Settings
from app.services.ai_service import AIService, AIServiceError
from app.utils.pdf_parser import DocumentParserError

router = APIRouter(prefix="/api/workspaces/{workspace_id}/assignments", tags=["assignments"])


def get_ai_service(settings: Settings = Depends(get_settings)) -> AIService:
    """Dependency for injecting AI Service."""
    return AIService(api_key=settings.anthropic_api_key)


@router.post("", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_assignment(
    workspace_id: UUID,
    file: UploadFile = File(...),
    membership: WorkspaceMember = Depends(require_team_leader),
    db: AsyncSession = Depends(get_db),
    ai: AIService = Depends(get_ai_service)
) -> AssignmentResponse:
    """
    Upload PDF/TXT, parse text, extract AI summary, and push new version.
    Only permitted for Team Leaders.
    """
    user_id = membership.user_id
    rate_key = f"upload_assign_{user_id}"
    
    try:
        rate_limiter.check(
            rate_key, "upload_assignment", max_calls=5, window_seconds=3600
        )
    except RateLimitExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=e.message
        )
        
    try:
        assignment = await assignment_service.upload_and_analyze_assignment(
            db=db, workspace_id=workspace_id, user_id=user_id, file=file, ai_service=ai
        )
    except DocumentParserError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AIServiceError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    return AssignmentResponse.model_validate(assignment)


@router.get("/latest", response_model=AssignmentResponse)
async def get_latest_assignment(
    workspace_id: UUID,
    membership: WorkspaceMember = Depends(require_team_leader),
    db: AsyncSession = Depends(get_db)
) -> AssignmentResponse:
    """Return the latest assignment analysis summary for the workspace."""
    assignment = await assignment_service.get_latest_assignment(db, workspace_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No assignments found for this workspace"
        )
    return AssignmentResponse.model_validate(assignment)


@router.get("", response_model=list[AssignmentResponse])
async def list_assignments(
    workspace_id: UUID,
    membership: WorkspaceMember = Depends(require_team_leader),
    db: AsyncSession = Depends(get_db)
) -> list[AssignmentResponse]:
    """List all previous versions of an assignment."""
    assignments = await assignment_service.get_assignments(db, workspace_id)
    return [AssignmentResponse.model_validate(a) for a in assignments]
