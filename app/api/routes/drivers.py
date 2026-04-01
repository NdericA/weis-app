from fastapi import APIRouter, HTTPException

from app.schemas.driver import (
    DriverApplicationDecision,
    DriverApplicationInfoUpdate,
    DriverAvailabilityUpdate,
    DriverOnboardingRequest,
    DriverProfileResponse,
)
from app.services.driver_service import driver_service

router = APIRouter()


@router.post("/onboarding", response_model=DriverProfileResponse)
def submit_onboarding(payload: DriverOnboardingRequest) -> DriverProfileResponse:
    return driver_service.submit_onboarding(payload)


@router.get("/applications", response_model=list[DriverProfileResponse])
def list_applications() -> list[DriverProfileResponse]:
    return driver_service.list_applications()


@router.get("/applications/{phone_number}", response_model=DriverProfileResponse)
def get_application(phone_number: str) -> DriverProfileResponse:
    profile = driver_service.get_application(phone_number)
    if not profile:
        raise HTTPException(status_code=404, detail="Driver application not found")
    return profile


@router.post("/applications/approve", response_model=DriverProfileResponse)
def approve_application(payload: DriverApplicationDecision) -> DriverProfileResponse:
    profile = driver_service.approve_application(payload)
    if not profile:
        raise HTTPException(status_code=404, detail="Driver application not found")
    return profile


@router.post("/applications/reject", response_model=DriverProfileResponse)
def reject_application(payload: DriverApplicationDecision) -> DriverProfileResponse:
    profile = driver_service.reject_application(payload)
    if not profile:
        raise HTTPException(status_code=404, detail="Driver application not found")
    return profile


@router.post("/applications/additional-info", response_model=DriverProfileResponse)
def submit_additional_info(payload: DriverApplicationInfoUpdate) -> DriverProfileResponse:
    profile = driver_service.submit_additional_info(payload)
    if not profile:
        raise HTTPException(status_code=404, detail="Driver application not found")
    return profile


@router.post("/availability", response_model=DriverProfileResponse)
def update_availability(phone_number: str, payload: DriverAvailabilityUpdate) -> DriverProfileResponse:
    return driver_service.update_availability(phone_number, payload)


@router.get("/me", response_model=DriverProfileResponse)
def get_my_driver_profile() -> DriverProfileResponse:
    return driver_service.get_driver_profile()
