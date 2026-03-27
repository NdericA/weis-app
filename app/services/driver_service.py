from uuid import uuid4

from app.core.enums import DriverStatus
from app.schemas.driver import DriverAvailabilityUpdate, DriverOnboardingRequest, DriverProfileResponse


class DriverService:
    def submit_onboarding(self, payload: DriverOnboardingRequest) -> DriverProfileResponse:
        return DriverProfileResponse(
            driver_id=str(uuid4()),
            user_id=str(uuid4()),
            full_name=payload.full_name,
            phone_number=payload.phone_number,
            status=DriverStatus.UNDER_REVIEW,
            approval_status="pending",
            rating=5.0,
            vehicle_summary=f"{payload.vehicle_color} {payload.vehicle_make} {payload.vehicle_model} ({payload.plate_number})",
        )

    def update_availability(self, payload: DriverAvailabilityUpdate) -> DriverProfileResponse:
        profile = self.get_driver_profile()
        return profile.model_copy(update={"status": payload.status})

    def get_driver_profile(self) -> DriverProfileResponse:
        return DriverProfileResponse(
            driver_id="demo-driver-001",
            user_id="demo-user-driver-001",
            full_name="Demo Driver",
            phone_number="+237670000002",
            status=DriverStatus.ONLINE,
            approval_status="approved",
            rating=4.86,
            vehicle_summary="Silver Toyota Corolla (LT-234-AB)",
        )
