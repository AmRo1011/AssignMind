"""
AssignMind — Users Router

Endpoints for managing the current user's profile and account settings.
All endpoints require authentication (Constitution §V).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, get_deactivated_user
from app.models.user import User
from app.schemas.user import UpdateProfileRequest, UserResponse
from app.services import user_service

router = APIRouter(prefix="/api/users", tags=["users"])

@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Update profile information for the current user."""
    updated = await user_service.update_user_profile(
        db=db,
        user=current_user,
        full_name=body.full_name,
        timezone_str=body.timezone,
    )
    return UserResponse.model_validate(updated)

@router.post("/me/delete", response_model=dict[str, str])
async def delete_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Deactivate the current user account (14-day grace period)."""
    await user_service.deactivate_user(db=db, user=current_user)
    return {"message": "Account deactivated. 14-day grace period started."}

@router.post("/me/reactivate", response_model=UserResponse)
async def reactivate_me(
    current_user: User = Depends(get_deactivated_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Reactivate a soft-deleted account."""
    if current_user.is_active:
        return UserResponse.model_validate(current_user)
        
    updated = await user_service.reactivate_user(db=db, user=current_user)
    return UserResponse.model_validate(updated)
