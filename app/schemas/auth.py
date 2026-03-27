from pydantic import BaseModel, EmailStr, Field


class PhoneRegistrationRequest(BaseModel):
    phone_number: str = Field(..., examples=["+237670000000"])
    full_name: str
    role: str = "rider"
    email: EmailStr | None = None


class OTPVerificationRequest(BaseModel):
    phone_number: str
    otp_code: str = Field(..., min_length=4, max_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user_id: str
