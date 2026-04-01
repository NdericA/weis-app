from decimal import Decimal

from pydantic import BaseModel


class DriverStatusRequest(BaseModel):
    driver_user_id: str
    status: str


class LiveRideRequest(BaseModel):
    rider_id: str
    rider_name: str
    pickup_address: str
    destination_address: str
    ride_type: str
    distance_km: Decimal
    duration_minutes: Decimal
    payment_method: str
    notes: str | None = None
    estimated_fare: Decimal


class DriverActionRequest(BaseModel):
    driver_user_id: str
    driver_name: str
    vehicle_summary: str


class DriverStageRequest(BaseModel):
    driver_user_id: str


class TipRequest(BaseModel):
    amount: Decimal


class ReplyRequest(BaseModel):
    driver_user_id: str
    message: str


class MessageRequest(BaseModel):
    sender_id: str
    sender_role: str
    sender_name: str
    message: str


class LiveStateResponse(BaseModel):
    driver_statuses: dict[str, str]
    request: dict | None = None
    trip: dict | None = None
    estimate: dict | None = None
    messages: list[dict] = []
    arrival_ready: bool = False
    selected_tip_amount: Decimal | None = None
    confirmed_tip_amount: Decimal | None = None
    driver_reply_sent: str = ""
    rider_position: dict
    pickup_position: dict
    dropoff_position: dict
    driver_position: dict
    driver_base_total: Decimal
    driver_running_total: Decimal
