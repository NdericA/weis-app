from random import randint


class DispatchService:
    def assign_driver(self, city: str, ride_type: str) -> dict[str, str | int]:
        return {
            "driver_id": f"{city.lower()}-{ride_type}-driver-001",
            "driver_eta_minutes": randint(3, 9),
        }
