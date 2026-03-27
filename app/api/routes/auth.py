from fastapi import APIRouter

from app.schemas.auth import OTPVerificationRequest, PhoneRegistrationRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter()
service = AuthService()


@router.post("/register/phone", response_model=TokenResponse)
def register_by_phone(payload: PhoneRegistrationRequest) -> TokenResponse:
    return service.register_phone_user(payload)


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(payload: OTPVerificationRequest) -> TokenResponse:
    return service.verify_otp(payload)
