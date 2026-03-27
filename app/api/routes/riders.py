from fastapi import APIRouter

from app.schemas.rider import RiderProfileResponse, RiderProfileUpdate
from app.services.user_service import UserService

router = APIRouter()
service = UserService()


@router.get("/me", response_model=RiderProfileResponse)
def get_my_profile() -> RiderProfileResponse:
    return service.get_rider_profile()


@router.put("/me", response_model=RiderProfileResponse)
def update_my_profile(payload: RiderProfileUpdate) -> RiderProfileResponse:
    return service.update_rider_profile(payload)
