from decimal import Decimal

from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class MoneyBreakdown(BaseModel):
    currency_code: str = "XAF"
    amount: Decimal
