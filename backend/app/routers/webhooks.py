"""
AssignMind — Webhooks Router

Lemon Squeezy integration for credit purchases.
"""

import hmac
import hashlib
from fastapi import APIRouter, BackgroundTasks, Depends, Request, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.database import get_db
from app.config import get_settings
from app.models.payment_transaction import PaymentTransaction
from app.models.user import User
from app.services import email_service
from app.services import credit_service
from app.utils.rate_limit import rate_limiter

logger = structlog.get_logger()
settings = get_settings()
router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

async def _handle_order_created(db, user_id, amount, order_id, var_id, attrs, payload, bt):
    await credit_service.grant_credits(db, user_id, amount, "purchased credits via LS", order_id)
    db.add(PaymentTransaction(
        user_id=user_id, lemon_squeezy_order_id=order_id, package_name=f"Variant {var_id}",
        credits_amount=amount, amount_usd=attrs.get("total", 0) / 100.0,
        status="completed", webhook_payload=payload
    ))
    bt.add_task(email_service.send_credits_purchased, attrs.get("user_email"), attrs.get("user_name", "User"), amount)

async def _handle_order_refunded(db, user_id, amount, order_id, var_id, attrs, payload):
    await credit_service.deduct_credits(db, user_id, amount, "refunded credits via LS", order_id)
    db.add(PaymentTransaction(
        user_id=user_id, lemon_squeezy_order_id=order_id + "_refund", package_name=f"Variant {var_id}",
        credits_amount=-amount, amount_usd=-attrs.get("total", 0) / 100.0,
        status="refunded", webhook_payload=payload
    ))

@router.post("/lemon-squeezy", status_code=status.HTTP_200_OK)
@rate_limiter(limit=100, window=60)
async def lemon_squeezy_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> dict:
    signature: str = request.headers.get("X-Signature", "")
    body = await request.body()
    mac = hmac.new(settings.lemon_squeezy_webhook_secret.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(mac, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    e_name = payload.get("meta", {}).get("event_name")
    attrs = payload.get("data", {}).get("attributes", {})
    order_id = str(attrs.get("order_identifier") or payload.get("data", {}).get("id"))
    
    exist = (await db.execute(select(PaymentTransaction).where(PaymentTransaction.lemon_squeezy_order_id == order_id))).scalar_one_or_none()
    if exist: return {"status": "idempotent_ok"}
    
    meta = payload.get("meta", {}).get("custom_data", {})
    user_id = meta.get("user_id")
    if not user_id:
        u = (await db.execute(select(User).where(User.email == attrs.get("user_email")))).scalar_one_or_none()
        if not u: return {"status": "user_not_found"}
        user_id = u.id

    var_id = str(attrs.get("first_order_item", {}).get("variant_id"))
    amount = {
        settings.lemon_squeezy_starter_variant_id: 100,
        settings.lemon_squeezy_standard_variant_id: 300,
        settings.lemon_squeezy_pro_variant_id: 700
    }.get(var_id, 100)

    if e_name == "order_created":
        await _handle_order_created(db, user_id, amount, order_id, var_id, attrs, payload, background_tasks)
    elif e_name == "order_refunded":
        await _handle_order_refunded(db, user_id, amount, order_id, var_id, attrs, payload)

    await db.commit()
    logger.info("webhook_processed", event=e_name, order_id=order_id)
    return {"status": "ok"}
