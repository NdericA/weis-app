from fastapi import APIRouter

from app.schemas.payment import PaymentInitiationRequest, PaymentResponse
from app.services.payment_service import PaymentService

router = APIRouter()
service = PaymentService()


@router.post("", response_model=PaymentResponse)
def initiate_payment(payload: PaymentInitiationRequest) -> PaymentResponse:
    return service.initiate_payment(payload)
