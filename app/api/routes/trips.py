from fastapi import APIRouter

from app.schemas.trip import FareEstimateRequest, FareEstimateResponse, TripCreateRequest, TripResponse, TripStatusUpdate
from app.services.trip_service import TripService

router = APIRouter()
service = TripService()


@router.post("/estimate", response_model=FareEstimateResponse)
def estimate_fare(payload: FareEstimateRequest) -> FareEstimateResponse:
    return service.estimate_trip(payload)


@router.post("", response_model=TripResponse)
def create_trip(payload: TripCreateRequest) -> TripResponse:
    return service.create_trip(payload)


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: str) -> TripResponse:
    return service.get_trip(trip_id)


@router.post("/{trip_id}/status", response_model=TripResponse)
def update_trip_status(trip_id: str, payload: TripStatusUpdate) -> TripResponse:
    return service.update_status(trip_id, payload)
