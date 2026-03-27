from fastapi import APIRouter

from app.schemas.driver import DriverAvailabilityUpdate, DriverOnboardingRequest, DriverProfileResponse
from app.services.driver_service import DriverService

router = APIRouter()
service = DriverService()


@router.post("/onboarding", response_model=DriverProfileResponse)
def submit_onboarding(payload: DriverOnboardingRequest) -> DriverProfileResponse:
    return service.submit_onboarding(payload)


@router.post("/availability", response_model=DriverProfileResponse)
def update_availability(payload: DriverAvailabilityUpdate) -> DriverProfileResponse:
    return service.update_availability(payload)


@router.get("/me", response_model=DriverProfileResponse)
def get_my_driver_profile() -> DriverProfileResponse:
    return service.get_driver_profile()
