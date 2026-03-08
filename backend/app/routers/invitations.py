"""
AssignMind — Invitations Router
"""

from uuid import UUID
from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.workspace_member import WorkspaceMember
from app.dependencies import get_current_user, require_team_leader
from app.schemas.invitation import (
    InvitationCreate, InvitationResponse, InvitationWithWorkspaceResponse
)
from app.services import invitation_service

router = APIRouter(prefix="/api", tags=["invitations"])

@router.post(
    "/workspaces/{workspace_id}/invitations", 
    response_model=dict,
    status_code=status.HTTP_201_CREATED
)
async def invite_to_workspace(
    workspace_id: UUID,
    data: InvitationCreate,
    background_tasks: BackgroundTasks,
    membership: WorkspaceMember = Depends(require_team_leader),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Send an invitation email to potential members (Team Leader only)."""
    await invitation_service.invite_user(db, workspace_id, user, data.email, background_tasks)
    return {"message": "If viable, invitation dispatched."}

@router.get(
    "/workspaces/{workspace_id}/invitations", 
    response_model=list[InvitationResponse]
)
async def list_workspace_invitations(
    workspace_id: UUID,
    membership: WorkspaceMember = Depends(require_team_leader),
    db: AsyncSession = Depends(get_db)
) -> list[InvitationResponse]:
    """List pending invitations (Team Leader only)."""
    invites = await invitation_service.get_workspace_invitations(db, workspace_id)
    return [InvitationResponse.model_validate(i) for i in invites]

@router.get(
    "/invitations/pending", 
    response_model=list[InvitationWithWorkspaceResponse]
)
async def list_my_invitations(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> list[InvitationWithWorkspaceResponse]:
    """Retrieve all pending invitations for the current user."""
    invites = await invitation_service.get_pending_user_invitations(db, user.email)
    return [InvitationWithWorkspaceResponse.model_validate(i) for i in invites]

@router.post("/invitations/{invitation_id}/accept", status_code=status.HTTP_200_OK)
async def accept_invitation(
    invitation_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Accept an invite & join the workspace."""
    await invitation_service.accept_invitation(db, invitation_id, user)
    return {"message": "Invitation accepted. Welcome to the workspace."}

@router.post("/invitations/{invitation_id}/decline", status_code=status.HTTP_200_OK)
async def decline_invitation(
    invitation_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Decline an invite explicitly."""
    await invitation_service.decline_invitation(db, invitation_id, user)
    return {"message": "Invitation declined."}
