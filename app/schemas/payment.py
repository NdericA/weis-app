from decimal import Decimal

from pydantic import BaseModel


class PaymentInitiationRequest(BaseModel):
    trip_id: str | None = None
    amount: Decimal
    method: str


class PaymentResponse(BaseModel):
    payment_id: str
    amount: Decimal
    currency_code: str = "XAF"
    method: str
    status: str
    provider_reference: str


class WalletResponse(BaseModel):
    wallet_id: str
    currency_code: str = "XAF"
    balance: Decimal
    ledger_hold: Decimal
