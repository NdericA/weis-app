from decimal import Decimal
from uuid import uuid4

from app.core.enums import TripStatus
from app.schemas.trip import FareEstimateRequest, FareEstimateResponse, TripCreateRequest, TripResponse, TripStatusUpdate
from app.services.dispatch_service import DispatchService
from app.services.pricing_service import PricingService


class TripService:
    def __init__(self) -> None:
        self.pricing_service = PricingService()
        self.dispatch_service = DispatchService()
        self._trips: dict[str, TripResponse] = {}

    def estimate_trip(self, payload: FareEstimateRequest) -> FareEstimateResponse:
        return self.pricing_service.estimate_fare(payload)

    def create_trip(self, payload: TripCreateRequest) -> TripResponse:
        estimate = self.estimate_trip(
            FareEstimateRequest(
                city=payload.city,
                ride_type=payload.ride_type,
                pickup_address=payload.pickup_address,
                destination_address=payload.destination_address,
                distance_km=payload.distance_km,
                duration_minutes=payload.duration_minutes,
            )
        )
        dispatch = self.dispatch_service.assign_driver(payload.city, payload.ride_type)
        trip = TripResponse(
            trip_id=str(uuid4()),
            rider_id=payload.rider_id,
            driver_id=str(dispatch["driver_id"]),
            status=TripStatus.DRIVER_ASSIGNED,
            pickup_address=payload.pickup_address,
            destination_address=payload.destination_address,
            estimated_fare=estimate.estimated_fare,
            final_fare=None,
            payment_method=payload.payment_method,
            driver_eta_minutes=int(dispatch["driver_eta_minutes"]),
        )
        self._trips[trip.trip_id] = trip
        return trip

    def get_trip(self, trip_id: str) -> TripResponse:
        return self._trips.get(
            trip_id,
            TripResponse(
                trip_id=trip_id,
                rider_id="demo-rider-001",
                driver_id="demo-driver-001",
                status=TripStatus.DRIVER_ASSIGNED,
                pickup_address="Bonamoussadi, Douala",
                destination_address="Akwa, Douala",
                estimated_fare=Decimal("3250.00"),
                final_fare=None,
                payment_method="cash",
                driver_eta_minutes=6,
            ),
        )

    def update_status(self, trip_id: str, payload: TripStatusUpdate) -> TripResponse:
        trip = self.get_trip(trip_id)
        final_fare = trip.final_fare
        if payload.status == TripStatus.TRIP_COMPLETED:
            final_fare = trip.estimated_fare
        updated = trip.model_copy(update={"status": payload.status, "final_fare": final_fare})
        self._trips[trip_id] = updated
        return updated
