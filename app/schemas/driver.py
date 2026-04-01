from pydantic import BaseModel


class DriverOnboardingRequest(BaseModel):
    full_name: str
    phone_number: str
    license_number: str
    national_id_number: str
    vehicle_make: str
    vehicle_model: str
    vehicle_color: str
    plate_number: str


class DriverAvailabilityUpdate(BaseModel):
    status: str


class DriverProfileResponse(BaseModel):
    driver_id: str
    user_id: str
    full_name: str
    phone_number: str
    status: str
    approval_status: str
    rating: float
    vehicle_summary: str | None = None
    license_number: str | None = None
    national_id_number: str | None = None
    rejection_reason: str = ""
    additional_info_required: bool = False
    additional_info: str = ""


class DriverApplicationDecision(BaseModel):
    phone_number: str
    reason: str = ""
    additional_info_required: bool = False


class DriverApplicationInfoUpdate(BaseModel):
    phone_number: str
    additional_info: str
