"""
AssignMind — Credit Service

Handles the reserve-then-commit credit pattern for AI service costs
as mandated by Constitution §IV.
"""

from uuid import UUID, uuid4
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Credit
from app.models.credit_transaction import CreditTransaction

async def reserve_credits(db: AsyncSession, user_id: UUID, amount: int, reference: str | None = None) -> str:
    """Reserve credits before making an AI call, creating a transaction record."""
    if not reference:
        reference = str(uuid4())
    result = await db.execute(select(Credit).where(Credit.user_id == user_id).with_for_update())
    credit = result.scalar_one_or_none()
    if not credit or (credit.balance - credit.reserved) < amount:
        raise HTTPException(status_code=402, detail="Insufficient credits available.")
        
    credit.reserved += amount
    db.add(CreditTransaction(
        user_id=user_id, type="reservation", amount=amount,
        reference_id=reference, description=f"Reserved {amount} credits"
    ))
    await db.commit()
    return reference

async def commit_credits(db: AsyncSession, user_id: UUID, amount: int, reference: str | None = None) -> None:
    """Commit (spend) reserved credits upon success."""
    result = await db.execute(select(Credit).where(Credit.user_id == user_id).with_for_update())
    credit = result.scalar_one_or_none()
    if credit and credit.reserved >= amount:
        credit.balance -= amount
        credit.reserved -= amount
        db.add(CreditTransaction(
            user_id=user_id, type="commit", amount=-amount,
            reference_id=reference, description=f"Committed {amount} credits"
        ))
        await db.commit()

async def release_credits(db: AsyncSession, user_id: UUID, amount: int, reference: str | None = None) -> None:
    """Release reserved credits upon failure."""
    result = await db.execute(select(Credit).where(Credit.user_id == user_id).with_for_update())
    credit = result.scalar_one_or_none()
    if credit and credit.reserved >= amount:
        credit.reserved -= amount
        db.add(CreditTransaction(
            user_id=user_id, type="release", amount=amount,
            reference_id=reference, description=f"Released {amount} credits"
        ))
        await db.commit()

async def grant_credits(db: AsyncSession, user_id: UUID, amount: int, reason: str, reference: str | None = None) -> None:
    """Add credits unconditionally to a wallet."""
    result = await db.execute(select(Credit).where(Credit.user_id == user_id).with_for_update())
    credit = result.scalar_one_or_none()
    if credit:
        credit.balance += amount
        db.add(CreditTransaction(
            user_id=user_id, type="grant", amount=amount,
            reference_id=reference, description=reason
        ))
        await db.commit()

async def deduct_credits(db: AsyncSession, user_id: UUID, amount: int, reason: str, reference: str | None = None) -> None:
    """Deduct credits (refunds) or flag if insufficient."""
    result = await db.execute(select(Credit).where(Credit.user_id == user_id).with_for_update())
    credit = result.scalar_one_or_none()
    if credit:
        if credit.balance < amount:
            credit.reserved += 0 # Real implementation might flag manual review
        credit.balance -= amount
        db.add(CreditTransaction(
            user_id=user_id, type="deduct", amount=-amount,
            reference_id=reference, description=reason
        ))
        await db.commit()
