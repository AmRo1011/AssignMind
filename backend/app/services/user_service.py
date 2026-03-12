"""
AssignMind — User Service

Business logic for user creation, phone verification, and credits.
All database writes use ORM (Constitution §III).
"""

from uuid import UUID

import structlog
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Credit, User
from app.utils.sanitize import sanitize_and_trim

logger = structlog.get_logger()

FREE_CREDIT_AMOUNT = 30


async def create_or_update_user(
    db: AsyncSession,
    supabase_id: UUID,
    email: str,
    full_name: str,
    avatar_url: str | None = None,
) -> tuple[User, bool]:
    """
    Upsert a user from Supabase OAuth data.

    Returns (user, is_new). Sanitizes full_name.
    Handles race conditions by catching IntegrityError on duplicate insert.
    """
    clean_name = sanitize_and_trim(full_name, max_length=200)

    existing = await _find_user_by_supabase_or_email(db, supabase_id, email)
    if existing:
        return await _update_existing_user(db, existing, supabase_id, email, clean_name, avatar_url)

    return await _insert_new_user(db, supabase_id, email, clean_name, avatar_url)


async def _find_user_by_supabase_or_email(
    db: AsyncSession, supabase_id: UUID, email: str
) -> User | None:
    """Look up a user by Supabase ID or email."""
    result = await db.execute(
        select(User).where(or_(User.supabase_id == supabase_id, User.email == email))
    )
    return result.scalar_one_or_none()


async def _update_existing_user(
    db: AsyncSession,
    existing: User,
    supabase_id: UUID,
    email: str,
    clean_name: str,
    avatar_url: str | None,
) -> tuple[User, bool]:
    """Update mutable fields on an existing user row."""
    existing.supabase_id = supabase_id
    existing.email = email
    existing.full_name = clean_name
    if avatar_url:
        existing.avatar_url = avatar_url
    await db.commit()
    await db.refresh(existing)
    return existing, False


async def _insert_new_user(
    db: AsyncSession,
    supabase_id: UUID,
    email: str,
    clean_name: str,
    avatar_url: str | None,
) -> tuple[User, bool]:
    """Insert a new User row, guarding against race-condition duplicates."""
    from sqlalchemy.exc import IntegrityError

    user = User(
        supabase_id=supabase_id,
        email=email,
        full_name=clean_name,
        avatar_url=avatar_url,
    )
    db.add(user)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        existing = await _find_user_by_supabase_or_email(db, supabase_id, email)
        if existing:
            logger.warning("user_insert_race_condition_recovered", email=email)
            return existing, False
        raise

    _init_credits(db, user.id)
    count = await _auto_accept_invites(db, user.id, email)
    await db.commit()
    await db.refresh(user)
    logger.info("user_created", id=str(user.id), auto_accepted_invites=count)
    return user, True

async def _auto_accept_invites(db: AsyncSession, user_id: UUID, email: str) -> int:
    """Accept pending invitations explicitly on new registrations."""
    from app.models.invitation import Invitation
    from app.models.workspace_member import WorkspaceMember
    from sqlalchemy import update, func
    
    stmt = (
        update(Invitation)
        .where(func.lower(Invitation.email) == email.lower(), Invitation.status == "pending")
        .values(status="accepted", responded_at=func.now())
        .returning(Invitation.workspace_id)
    )
    accepted = await db.execute(stmt)
    workspace_ids = accepted.scalars().all()
    for wid in workspace_ids:
        db.add(WorkspaceMember(workspace_id=wid, user_id=user_id, role="member"))
        
    return len(workspace_ids)


def _init_credits(db: AsyncSession, user_id: UUID) -> None:
    """Create a zero-balance credit row for a new user."""
    credit = Credit(user_id=user_id, balance=0, reserved=0)
    db.add(credit)


async def get_user_by_id(
    db: AsyncSession, user_id: UUID
) -> User | None:
    """Fetch a user by their internal UUID."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_phone_owner(db: AsyncSession, phone: str) -> User | None:
    """Return the user who owns the given phone number, or None."""
    result = await db.execute(
        select(User).where(User.phone == phone)
    )
    return result.scalar_one_or_none()


async def check_phone_unique(
    db: AsyncSession, phone: str, exclude_user_id: UUID | None = None
) -> bool:
    """Check if a phone number is not already registered (verified)."""
    query = select(User).where(
        User.phone == phone, User.phone_verified.is_(True)
    )
    if exclude_user_id:
        query = query.where(User.id != exclude_user_id)

    result = await db.execute(query)
    return result.scalar_one_or_none() is None


async def verify_phone(
    db: AsyncSession, user: User, phone: str
) -> User:
    """
    Mark user's phone as verified.

    Assumes OTP has already been validated by Supabase.
    Grants free credits if not already granted.
    """
    user.phone = phone
    user.phone_verified = True
    await _grant_free_credits_if_eligible(db, user)
    await db.commit()
    await db.refresh(user)

    logger.info(
        "phone_verified", user_id=str(user.id), phone=phone
    )
    return user


async def _grant_free_credits_if_eligible(
    db: AsyncSession, user: User
) -> bool:
    """Grant one-time free credits on phone verification."""
    result = await db.execute(
        select(Credit).where(Credit.user_id == user.id)
    )
    credit = result.scalar_one_or_none()

    if credit is None:
        _init_credits(db, user.id)
        await db.flush()
        result = await db.execute(
            select(Credit).where(Credit.user_id == user.id)
        )
        credit = result.scalar_one_or_none()

    if credit is None or credit.free_credits_granted:
        return False

    credit.balance = credit.balance + FREE_CREDIT_AMOUNT
    credit.free_credits_granted = True

    logger.info(
        "free_credits_granted",
        user_id=str(user.id),
        amount=FREE_CREDIT_AMOUNT,
    )
    return True


async def get_user_credit(
    db: AsyncSession, user_id: UUID
) -> Credit | None:
    """Fetch a user's credit record."""
    result = await db.execute(
        select(Credit).where(Credit.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_user_profile(
    db: AsyncSession,
    user: User,
    full_name: str | None = None,
    timezone_str: str | None = None,
) -> User:
    """Update user profile fields."""
    if full_name is not None:
        user.full_name = sanitize_and_trim(full_name, max_length=200)
    if timezone_str is not None:
        user.timezone = sanitize_and_trim(timezone_str, max_length=50)

    await db.commit()
    await db.refresh(user)
    return user


async def deactivate_user(
    db: AsyncSession,
    user: User,
) -> User:
    """
    Deactivate a user account (starts 14-day grace period).
    Sets is_active to False.
    """
    user.is_active = False
    user.deactivated_at = func.now()
    
    await db.commit()
    await db.refresh(user)
    
    logger.info("user_deactivated", user_id=str(user.id))
    return user

async def reactivate_user(
    db: AsyncSession,
    user: User,
) -> User:
    """
    Reactivate a user account within the 14-day grace period.
    """
    user.is_active = True
    user.deactivated_at = None
    
    await db.commit()
    await db.refresh(user)
    
    logger.info("user_reactivated", user_id=str(user.id))
    return user
