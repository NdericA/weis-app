from app.schemas.rider import RiderProfileResponse, RiderProfileUpdate


class UserService:
    def get_rider_profile(self) -> RiderProfileResponse:
        return RiderProfileResponse(
            user_id="demo-rider-001",
            full_name="Demo Rider",
            phone_number="+237670000001",
            email="rider@weis.cm",
            preferred_language="en",
            emergency_contact="+237680000001",
            home_address="Bonapriso, Douala",
            work_address="Akwa, Douala",
        )

    def update_rider_profile(self, payload: RiderProfileUpdate) -> RiderProfileResponse:
        current = self.get_rider_profile()
        updates = payload.model_dump(exclude_none=True)
        return current.model_copy(update=updates)
