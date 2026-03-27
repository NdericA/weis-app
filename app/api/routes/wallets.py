from fastapi import APIRouter

from app.schemas.payment import WalletResponse
from app.services.payment_service import PaymentService

router = APIRouter()
service = PaymentService()


@router.get("/me", response_model=WalletResponse)
def get_wallet() -> WalletResponse:
    return service.get_wallet_snapshot()
