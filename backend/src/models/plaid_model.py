from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class PlaidItem:
    """Represents a Plaid item (bank connection)"""
    user_id: str
    item_id: str
    access_token: str
    institution_id: str
    institution_name: str
    created_at: datetime
    updated_at: datetime
    status: str = "active"

@dataclass
class PlaidTransaction:
    """Represents a transaction from Plaid"""
    transaction_id: str
    user_id: str
    account_id: str
    amount: float
    date: datetime
    name: str
    merchant_name: Optional[str] = None
    category: Optional[str] = None
    pending: bool = False
    payment_meta: Optional[dict] = None

@dataclass
class PlaidAccount:
    """Represents a bank account or card from Plaid"""
    account_id: str
    user_id: str
    item_id: str
    name: str
    type: str
    created_at: datetime
    updated_at: datetime
    official_name: Optional[str] = None
    subtype: Optional[str] = None
    mask: Optional[str] = None