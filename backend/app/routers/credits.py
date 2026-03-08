"""
AssignMind — Credits Router

Provides balance checks, transaction history, and checkout links.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import structlog
import hashlib
import hmac
import urllib.parse
from uuid import UUID

from app.database import get_db
from app.config import get_settings
from app.dependencies import get_current_user
from app.models.user import User, Credit
from app.models.credit_transaction import CreditTransaction
from app.schemas.user import UserWithCreditsResponse
from app.schemas.credit import CreditTransactionResponse, CheckoutUrlResponse
from app.services import user_service

logger = structlog.get_logger()
settings = get_settings()
router = APIRouter(prefix="/api/credits", tags=["credits"])

@router.get("/balance", response_model=UserWithCreditsResponse)
async def get_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserWithCreditsResponse:
    """Retrieve current user balance and reservation status."""
    cr_stmt = select(Credit).where(Credit.user_id == current_user.id)
    cr = (await db.execute(cr_stmt)).scalar_one_or_none()
    
    # Dump it into a combined dictionary dict mimicking UserWithCreditsResponse
    data = {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "phone": current_user.phone,
        "phone_verified": current_user.phone_verified,
        "timezone": current_user.timezone,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "credit_balance": cr.balance if cr else 0,
        "credit_reserved": cr.reserved if cr else 0
    }
    return UserWithCreditsResponse.model_validate(data)

@router.get("/transactions", response_model=list[CreditTransactionResponse])
async def list_transactions(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> list[CreditTransactionResponse]:
    """Paginated list of credit ledger logs."""
    stmt = (
        select(CreditTransaction)
        .where(CreditTransaction.user_id == current_user.id)
        .order_by(CreditTransaction.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    res = (await db.execute(stmt)).scalars().all()
    return [CreditTransactionResponse.model_validate(tx) for tx in res]

@router.post("/checkout/{package}", response_model=CheckoutUrlResponse)
async def checkout(
    package: str,
    current_user: User = Depends(get_current_user)
) -> CheckoutUrlResponse:
    """Generate Lemon Squeezy checkout URL dynamically passing custom user_id mapping."""
    store_id = settings.lemon_squeezy_store_id
    
    mapping = {
        "starter": settings.lemon_squeezy_starter_variant_id,
        "standard": settings.lemon_squeezy_standard_variant_id,
        "pro": settings.lemon_squeezy_pro_variant_id
    }
    variant_id = mapping.get(package.lower())
    if not variant_id:
        raise HTTPException(status_code=400, detail="Invalid package selection")

    base_url = f"https://sandbox.lemonsqueezy.com/buy/{variant_id}" if not settings.is_production else f"https://app.lemonsqueezy.com/buy/{variant_id}"
    
    query = urllib.parse.urlencode({
        "checkout[email]": current_user.email,
        "checkout[name]": current_user.full_name,
        "checkout[custom][user_id]": str(current_user.id),
        "embed": 0
    })
    
    return CheckoutUrlResponse(checkout_url=f"{base_url}?{query}")
