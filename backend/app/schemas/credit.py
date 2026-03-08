"""
AssignMind — Credit Schemas

Data structures for credit balances, transactions, and checkouts.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class CreditTransactionResponse(BaseModel):
    id: UUID
    user_id: UUID
    type: str
    amount: int
    description: str | None
    reference_id: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True

class CheckoutUrlResponse(BaseModel):
    checkout_url: str
