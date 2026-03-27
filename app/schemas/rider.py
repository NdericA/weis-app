from pydantic import BaseModel, EmailStr


class RiderProfileResponse(BaseModel):
    user_id: str
    full_name: str
    phone_number: str
    email: EmailStr | None = None
    preferred_language: str = "en"
    emergency_contact: str | None = None
    home_address: str | None = None
    work_address: str | None = None


class RiderProfileUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    preferred_language: str | None = None
    emergency_contact: str | None = None
    home_address: str | None = None
    work_address: str | None = None
