from copy import deepcopy
from decimal import Decimal
from threading import Lock

from app.schemas.live import (
    DriverActionRequest,
    DriverStageRequest,
    DriverStatusRequest,
    LiveRideRequest,
    LiveStateResponse,
    MessageRequest,
    ReplyRequest,
    TipRequest,
)


class LiveOpsService:
    def __init__(self) -> None:
        self._lock = Lock()
        self._state = self._default_state()

    def _default_state(self) -> dict:
        return {
            "driver_statuses": {},
            "request": None,
            "trip": None,
            "estimate": None,
            "messages": [],
            "arrival_ready": False,
            "selected_tip_amount": None,
            "confirmed_tip_amount": None,
            "driver_reply_sent": "",
            "rider_position": {"x": 22, "y": 62},
            "pickup_position": {"x": 22, "y": 62},
            "dropoff_position": {"x": 78, "y": 28},
            "driver_position": {"x": 78, "y": 76},
            "driver_base_total": Decimal("28500"),
            "driver_running_total": Decimal("28500"),
        }

    def reset(self) -> None:
        with self._lock:
            self._state = self._default_state()

    def state(self) -> LiveStateResponse:
        with self._lock:
            self._advance_positions()
            return LiveStateResponse(**deepcopy(self._state))

    def _interpolate(self, current: dict[str, float], target: dict[str, float], step: float) -> dict[str, float]:
        return {
            "x": round(current["x"] + ((target["x"] - current["x"]) * step), 2),
            "y": round(current["y"] + ((target["y"] - current["y"]) * step), 2),
        }

    def _distance(self, a: dict[str, float], b: dict[str, float]) -> float:
        dx = a["x"] - b["x"]
        dy = a["y"] - b["y"]
        return ((dx * dx) + (dy * dy)) ** 0.5

    def _advance_positions(self) -> None:
        trip = self._state["trip"]
        if not trip:
            return
        if trip["stage"] == "accepted":
            self._state["driver_position"] = self._interpolate(
                self._state["driver_position"],
                self._state["pickup_position"],
                0.22,
            )
            if self._distance(self._state["driver_position"], self._state["pickup_position"]) <= 1.25:
                self._state["driver_position"] = deepcopy(self._state["pickup_position"])
                self._state["arrival_ready"] = True
        elif trip["stage"] == "on_trip":
            self._state["driver_position"] = self._interpolate(
                self._state["driver_position"],
                self._state["dropoff_position"],
                0.18,
            )
            self._state["rider_position"] = deepcopy(self._state["driver_position"])

    def set_driver_status(self, payload: DriverStatusRequest) -> LiveStateResponse:
        with self._lock:
            self._state["driver_statuses"][payload.driver_user_id] = payload.status
            return LiveStateResponse(**deepcopy(self._state))

    def create_request(self, payload: LiveRideRequest) -> LiveStateResponse:
        with self._lock:
            self._state["trip"] = None
            self._state["arrival_ready"] = False
            self._state["selected_tip_amount"] = None
            self._state["confirmed_tip_amount"] = None
            self._state["driver_reply_sent"] = ""
            self._state["messages"] = []
            self._state["estimate"] = {
                "estimated_fare": payload.estimated_fare,
                "ride_type": payload.ride_type,
            }
            self._state["request"] = payload.model_dump()
            return LiveStateResponse(**deepcopy(self._state))

    def accept_request(self, payload: DriverActionRequest) -> LiveStateResponse:
        with self._lock:
            request = self._state["request"]
            if not request or self._state["driver_statuses"].get(payload.driver_user_id) != "online":
                return LiveStateResponse(**deepcopy(self._state))
            self._state["trip"] = {
                "trip_id": f"live-{payload.driver_user_id[-6:]}",
                "driver_user_id": payload.driver_user_id,
                "driver_name": payload.driver_name,
                "vehicle_summary": payload.vehicle_summary,
                "payment_method": request["payment_method"],
                "base_fare": request["estimated_fare"],
                "stage": "accepted",
                "stage_label": "Driver accepted",
            }
            self._state["request"] = None
            self._state["arrival_ready"] = False
            return LiveStateResponse(**deepcopy(self._state))

    def decline_request(self, _: DriverStageRequest) -> LiveStateResponse:
        with self._lock:
            self._state["trip"] = None
            self._state["arrival_ready"] = False
            return LiveStateResponse(**deepcopy(self._state))

    def mark_arrived(self, payload: DriverStageRequest) -> LiveStateResponse:
        with self._lock:
            trip = self._state["trip"]
            if trip and trip["driver_user_id"] == payload.driver_user_id and trip["stage"] == "accepted":
                trip["stage"] = "driver_arrived"
                trip["stage_label"] = "Driver arrived"
                self._state["arrival_ready"] = False
                self._state["driver_position"] = deepcopy(self._state["pickup_position"])
            return LiveStateResponse(**deepcopy(self._state))

    def start_trip(self, payload: DriverStageRequest) -> LiveStateResponse:
        with self._lock:
            trip = self._state["trip"]
            if trip and trip["driver_user_id"] == payload.driver_user_id and trip["stage"] == "driver_arrived":
                trip["stage"] = "on_trip"
                trip["stage_label"] = "Trip in progress"
                self._state["rider_position"] = deepcopy(self._state["driver_position"])
            return LiveStateResponse(**deepcopy(self._state))

    def complete_trip(self, payload: DriverStageRequest) -> LiveStateResponse:
        with self._lock:
            trip = self._state["trip"]
            if trip and trip["driver_user_id"] == payload.driver_user_id and trip["stage"] == "on_trip":
                trip["stage"] = "completed"
                trip["stage_label"] = "Trip completed"
                self._state["driver_position"] = deepcopy(self._state["dropoff_position"])
                self._state["rider_position"] = deepcopy(self._state["dropoff_position"])
                if not self._state["confirmed_tip_amount"]:
                    self._state["driver_running_total"] = self._state["driver_base_total"] + Decimal(str(trip["base_fare"]))
            return LiveStateResponse(**deepcopy(self._state))

    def confirm_tip(self, payload: TipRequest) -> LiveStateResponse:
        with self._lock:
            self._state["selected_tip_amount"] = payload.amount
            self._state["confirmed_tip_amount"] = payload.amount
            trip = self._state["trip"]
            if trip:
                self._state["driver_running_total"] = self._state["driver_base_total"] + Decimal(str(trip["base_fare"])) + payload.amount
            return LiveStateResponse(**deepcopy(self._state))

    def send_reply(self, payload: ReplyRequest) -> LiveStateResponse:
        with self._lock:
            trip = self._state["trip"]
            if trip and trip["driver_user_id"] == payload.driver_user_id:
                self._state["driver_reply_sent"] = payload.message
            return LiveStateResponse(**deepcopy(self._state))

    def send_message(self, payload: MessageRequest) -> LiveStateResponse:
        with self._lock:
            request = self._state["request"]
            trip = self._state["trip"]
            trip_allows_chat = trip and trip["stage"] in {"accepted", "driver_arrived"}
            if not request and not trip_allows_chat:
                return LiveStateResponse(**deepcopy(self._state))
            self._state["messages"].append(
                {
                    "sender_id": payload.sender_id,
                    "sender_role": payload.sender_role,
                    "sender_name": payload.sender_name,
                    "message": payload.message,
                }
            )
            self._state["messages"] = self._state["messages"][-30:]
            return LiveStateResponse(**deepcopy(self._state))


live_ops_service = LiveOpsService()
