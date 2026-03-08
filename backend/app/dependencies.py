"""
AssignMind — FastAPI Dependency Injection

All route-level dependencies for auth, DB sessions, and role checks.
Every endpoint MUST validate authentication (Constitution §V).
"""

from uuid import UUID

from fastapi import Depends, Header, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.workspace_member import WorkspaceMember
from app.utils.auth import (
    AuthError,
    extract_bearer_token,
    get_supabase_user_id,
)


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extract JWT from Authorization header and return the User.

    Raises 401 if token is missing, invalid, or user not found.
    """
    try:
        token = extract_bearer_token(authorization)
        supabase_id = get_supabase_user_id(token)
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "auth_error", "message": exc.message},
        )

    result = await db.execute(
        select(User).where(User.supabase_id == supabase_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "user_not_found",
                "message": "User account not found",
            },
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "account_deactivated",
                "message": "Account is deactivated",
            },
        )

    return user

async def get_deactivated_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Allow fetching a user even if they are deactivated (for reactivation)."""
    try:
        token = extract_bearer_token(authorization)
        supabase_id = get_supabase_user_id(token)
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "auth_error", "message": exc.message},
        )

    result = await db.execute(
        select(User).where(User.supabase_id == supabase_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "user_not_found", "message": "User not found"},
        )
        
    return user


async def require_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure the current user has verified their phone number.

    Raises 403 if phone is not verified.
    """
    if not current_user.phone_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "phone_not_verified",
                "message": "Phone verification required",
            },
        )
    return current_user


async def _get_membership(
    workspace_id: UUID,
    user_id: UUID,
    db: AsyncSession,
) -> WorkspaceMember:
    """
    Fetch workspace membership for a given user.

    Raises 403 if the user is not a member.
    """
    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
    )
    membership = result.scalar_one_or_none()

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "not_a_member",
                "message": "You are not a member of this workspace",
            },
        )

    return membership


async def require_workspace_member(
    workspace_id: UUID = Path(...),
    current_user: User = Depends(require_verified_user),
    db: AsyncSession = Depends(get_db),
) -> WorkspaceMember:
    """
    Ensure the current user is a member of the workspace.

    Extracts workspace_id from path parameter.
    Returns the WorkspaceMember record.
    """
    return await _get_membership(
        workspace_id, current_user.id, db
    )


async def require_team_leader(
    workspace_id: UUID = Path(...),
    current_user: User = Depends(require_verified_user),
    db: AsyncSession = Depends(get_db),
) -> WorkspaceMember:
    """
    Ensure the current user is the Team Leader of the workspace.

    Raises 403 if the user is not a member or not a leader.
    """
    membership = await _get_membership(
        workspace_id, current_user.id, db
    )

    if membership.role != "leader":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "not_team_leader",
                "message": "Only the Team Leader can perform this action",
            },
        )

    return membership
