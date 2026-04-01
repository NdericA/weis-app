from uuid import uuid4

from app.core.enums import DriverStatus
from app.schemas.driver import (
    DriverApplicationDecision,
    DriverApplicationInfoUpdate,
    DriverAvailabilityUpdate,
    DriverOnboardingRequest,
    DriverProfileResponse,
)


class DriverService:
    def __init__(self) -> None:
        self._applications: dict[str, DriverProfileResponse] = {}

    def submit_onboarding(self, payload: DriverOnboardingRequest) -> DriverProfileResponse:
        existing = self._applications.get(payload.phone_number)
        driver_id = existing.driver_id if existing else str(uuid4())
        user_id = existing.user_id if existing else str(uuid4())
        profile = DriverProfileResponse(
            driver_id=driver_id,
            user_id=user_id,
            full_name=payload.full_name,
            phone_number=payload.phone_number,
            status=DriverStatus.UNDER_REVIEW,
            approval_status="pending",
            rating=5.0,
            vehicle_summary=f"{payload.vehicle_color} {payload.vehicle_make} {payload.vehicle_model} ({payload.plate_number})",
            license_number=payload.license_number,
            national_id_number=payload.national_id_number,
            rejection_reason="",
            additional_info_required=False,
            additional_info=existing.additional_info if existing else "",
        )
        self._applications[payload.phone_number] = profile
        return profile

    def list_applications(self) -> list[DriverProfileResponse]:
        return list(self._applications.values())

    def get_application(self, phone_number: str) -> DriverProfileResponse | None:
        return self._applications.get(phone_number)

    def approve_application(self, payload: DriverApplicationDecision) -> DriverProfileResponse | None:
        profile = self._applications.get(payload.phone_number)
        if not profile:
            return None
        approved = profile.model_copy(
            update={
                "approval_status": "approved",
                "status": DriverStatus.OFFLINE,
                "rejection_reason": "",
                "additional_info_required": False,
            }
        )
        self._applications[payload.phone_number] = approved
        return approved

    def reject_application(self, payload: DriverApplicationDecision) -> DriverProfileResponse | None:
        profile = self._applications.get(payload.phone_number)
        if not profile:
            return None
        rejected = profile.model_copy(
            update={
                "approval_status": "rejected",
                "status": DriverStatus.UNDER_REVIEW,
                "rejection_reason": payload.reason,
                "additional_info_required": payload.additional_info_required,
            }
        )
        self._applications[payload.phone_number] = rejected
        return rejected

    def submit_additional_info(self, payload: DriverApplicationInfoUpdate) -> DriverProfileResponse | None:
        profile = self._applications.get(payload.phone_number)
        if not profile:
            return None
        updated = profile.model_copy(
            update={
                "approval_status": "pending",
                "status": DriverStatus.UNDER_REVIEW,
                "rejection_reason": "",
                "additional_info": payload.additional_info,
            }
        )
        self._applications[payload.phone_number] = updated
        return updated

    def update_availability(self, phone_number: str, payload: DriverAvailabilityUpdate) -> DriverProfileResponse:
        profile = self._applications.get(phone_number)
        if not profile:
            return self.get_driver_profile()
        updated = profile.model_copy(update={"status": payload.status})
        self._applications[phone_number] = updated
        return updated

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
            license_number="DL-CM-20481",
            national_id_number="CMR-1987745",
        )


driver_service = DriverService()
