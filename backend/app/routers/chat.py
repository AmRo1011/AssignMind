"""
AssignMind — Chat Router

Mounts HTTP logic securely executing workspace interactions onto paginated bounds explicitly.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.workspace_member import WorkspaceMember
from app.dependencies import get_current_user, require_workspace_member
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse
from app.services import chat_service

router = APIRouter(prefix="/api/workspaces/{workspace_id}/chat", tags=["chat"])

@router.get("", response_model=list[ChatMessageResponse])
async def list_messages(
    workspace_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    membership: WorkspaceMember = Depends(require_workspace_member),
    db: AsyncSession = Depends(get_db)
) -> list[dict]:
    """Retrieve workspace chat log natively paginated and formatted."""
    return await chat_service.get_workspace_messages(db, workspace_id, limit, offset)

@router.post("", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    workspace_id: UUID,
    req: ChatMessageCreate,
    membership: WorkspaceMember = Depends(require_workspace_member),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ChatMessageResponse:
    """Send a human message globally tracked parsing explicit rules securely."""
    msg = await chat_service.send_human_message(db, workspace_id, user, req)
    return ChatMessageResponse.model_validate(msg)
