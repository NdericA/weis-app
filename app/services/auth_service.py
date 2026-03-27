from uuid import uuid4

from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.auth import OTPVerificationRequest, PhoneRegistrationRequest, TokenResponse


class AuthService:
    def register_phone_user(self, payload: PhoneRegistrationRequest) -> TokenResponse:
        user_id = str(uuid4())
        return TokenResponse(
            access_token=create_access_token(user_id),
            expires_in_minutes=settings.access_token_expire_minutes,
            user_id=user_id,
        )

    def verify_otp(self, payload: OTPVerificationRequest) -> TokenResponse:
        user_id = f"verified-{payload.phone_number[-4:]}"
        return TokenResponse(
            access_token=create_access_token(user_id),
            expires_in_minutes=settings.access_token_expire_minutes,
            user_id=user_id,
        )
