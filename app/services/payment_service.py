from decimal import Decimal
from uuid import uuid4

from app.core.enums import PaymentStatus
from app.schemas.payment import PaymentInitiationRequest, PaymentResponse, WalletResponse


class PaymentService:
    def initiate_payment(self, payload: PaymentInitiationRequest) -> PaymentResponse:
        status = PaymentStatus.COMPLETED if payload.method == "cash" else PaymentStatus.PENDING
        return PaymentResponse(
            payment_id=str(uuid4()),
            amount=payload.amount,
            method=payload.method,
            status=status,
            provider_reference=f"pay-{uuid4().hex[:12]}",
        )

    def get_wallet_snapshot(self) -> WalletResponse:
        return WalletResponse(
            wallet_id="wallet-demo-001",
            balance=Decimal("25000.00"),
            ledger_hold=Decimal("0.00"),
        )
