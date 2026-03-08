"""
AssignMind — Invitation Service

Logic for inviting users to workspaces and responding to standard invites.
"""

from uuid import UUID
from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.invitation import Invitation
from app.models.workspace_member import WorkspaceMember
from app.models.user import User

logger = structlog.get_logger()

async def _check_invite_viability(
    db: AsyncSession, workspace_id: UUID, current_user: User, raw_email: str
) -> tuple[bool, str]:
    """Validates self-invite, duplicate invites, and member limitations."""
    email = raw_email.strip().lower()
    if email == current_user.email.lower():
        return False, email  # Self invite -> silent skip

    ws_count = await db.scalar(
        select(func.count()).where(WorkspaceMember.workspace_id == workspace_id)
    )
    if ws_count and ws_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workspaces cannot exceed 10 members."
        )

    dup = await db.scalar(
        select(Invitation).where(
            Invitation.workspace_id == workspace_id,
            Invitation.email == email,
            Invitation.status == "pending"
        )
    )
    if dup:
        return False, email  # Silent duplicate skip
        
    return True, email

async def invite_user(
    db: AsyncSession, workspace_id: UUID, current_user: User, raw_email: str, background_tasks: BackgroundTasks
) -> Invitation | None:
    """Create a pending invitation and mock trigger the registration email."""
    is_viable, email = await _check_invite_viability(db, workspace_id, current_user, raw_email)
    if not is_viable:
        return None

    invitation = Invitation(
        workspace_id=workspace_id,
        email=email,
        invited_by=current_user.id
    )
    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)
    
    from app.models.workspace import Workspace
    ws = await db.get(Workspace, workspace_id)
    if ws:
        from app.services import email_service
        background_tasks.add_task(email_service.send_workspace_invitation, email, current_user.full_name, ws.title)
    
    logger.info("invitation_sent", email=email, workspace_id=str(workspace_id))
    
    return invitation

async def get_workspace_invitations(
    db: AsyncSession, workspace_id: UUID
) -> list[Invitation]:
    """Retrieve all pending invitations for a specific workspace (Leaders)."""
    result = await db.execute(
        select(Invitation)
        .where(
            Invitation.workspace_id == workspace_id,
            Invitation.status == "pending"
        )
    )
    return list(result.scalars().all())

async def get_pending_user_invitations(
    db: AsyncSession, email: str
) -> list[Invitation]:
    """Retrieve all open invites mapping directly to the current user email."""
    result = await db.execute(
        select(Invitation)
        .options(selectinload(Invitation.workspace))  # Needs relation on model
        .where(
            func.lower(Invitation.email) == email.lower(),
            Invitation.status == "pending"
        )
    )
    return list(result.scalars().all())

async def accept_invitation(db: AsyncSession, invitation_id: UUID, user: User) -> None:
    """Accept an invite, checking for max members, mapping relationship."""
    invitation = await db.get(Invitation, invitation_id)
    if not invitation or invitation.status != "pending" or invitation.email.lower() != user.email.lower():
        raise HTTPException(status_code=404, detail="Valid invitation not found.")
        
    # Check max limit again
    ws_count = await db.scalar(select(func.count()).where(WorkspaceMember.workspace_id == invitation.workspace_id))
    if ws_count and ws_count >= 10:
        raise HTTPException(status_code=400, detail="Workspace is full (10 members max).")

    # Enroll user
    member = WorkspaceMember(workspace_id=invitation.workspace_id, user_id=user.id, role="member")
    db.add(member)
    
    invitation.status = "accepted"
    invitation.responded_at = func.now()
    await db.commit()

async def decline_invitation(db: AsyncSession, invitation_id: UUID, user: User) -> None:
    """Decline an invite and update payload state."""
    invitation = await db.get(Invitation, invitation_id)
    if not invitation or invitation.status != "pending" or invitation.email.lower() != user.email.lower():
        raise HTTPException(status_code=404, detail="Valid invitation not found.")

    invitation.status = "declined"
    invitation.responded_at = func.now()
    await db.commit()
    
    # Placeholder: Notify leader
    logger.info("invitation_declined", invite_id=str(invitation_id), workspace_id=str(invitation.workspace_id))
