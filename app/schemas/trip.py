from decimal import Decimal

from pydantic import BaseModel


class FareEstimateRequest(BaseModel):
    city: str = "Douala"
    ride_type: str = "economy"
    pickup_address: str
    destination_address: str
    distance_km: Decimal
    duration_minutes: Decimal
    surge_multiplier: Decimal = Decimal("1.00")


class FareEstimateResponse(BaseModel):
    currency_code: str = "XAF"
    ride_type: str
    estimated_fare: Decimal
    base_fare: Decimal
    distance_fare: Decimal
    time_fare: Decimal
    surge_multiplier: Decimal


class TripCreateRequest(BaseModel):
    rider_id: str
    city: str = "Douala"
    ride_type: str = "economy"
    pickup_address: str
    destination_address: str
    distance_km: Decimal
    duration_minutes: Decimal
    payment_method: str = "cash"
    notes: str | None = None


class TripStatusUpdate(BaseModel):
    status: str
    actor_role: str = "system"
    note: str | None = None


class TripResponse(BaseModel):
    trip_id: str
    rider_id: str
    driver_id: str | None = None
    status: str
    pickup_address: str
    destination_address: str
    estimated_fare: Decimal
    final_fare: Decimal | None = None
    payment_method: str
    driver_eta_minutes: int | None = None
