from fastapi import APIRouter

from app.schemas.live import (
    DriverActionRequest,
    DriverStageRequest,
    DriverStatusRequest,
    LiveRideRequest,
    LiveStateResponse,
    ReplyRequest,
    TipRequest,
)
from app.services.live_ops_service import live_ops_service

router = APIRouter()


@router.get("/state", response_model=LiveStateResponse)
def get_live_state() -> LiveStateResponse:
    return live_ops_service.state()


@router.post("/driver-status", response_model=LiveStateResponse)
def set_driver_status(payload: DriverStatusRequest) -> LiveStateResponse:
    return live_ops_service.set_driver_status(payload)


@router.post("/request", response_model=LiveStateResponse)
def create_live_request(payload: LiveRideRequest) -> LiveStateResponse:
    return live_ops_service.create_request(payload)


@router.post("/accept", response_model=LiveStateResponse)
def accept_request(payload: DriverActionRequest) -> LiveStateResponse:
    return live_ops_service.accept_request(payload)


@router.post("/decline", response_model=LiveStateResponse)
def decline_request(payload: DriverStageRequest) -> LiveStateResponse:
    return live_ops_service.decline_request(payload)


@router.post("/arrived", response_model=LiveStateResponse)
def mark_arrived(payload: DriverStageRequest) -> LiveStateResponse:
    return live_ops_service.mark_arrived(payload)


@router.post("/start", response_model=LiveStateResponse)
def start_trip(payload: DriverStageRequest) -> LiveStateResponse:
    return live_ops_service.start_trip(payload)


@router.post("/complete", response_model=LiveStateResponse)
def complete_trip(payload: DriverStageRequest) -> LiveStateResponse:
    return live_ops_service.complete_trip(payload)


@router.post("/tip", response_model=LiveStateResponse)
def confirm_tip(payload: TipRequest) -> LiveStateResponse:
    return live_ops_service.confirm_tip(payload)


@router.post("/reply", response_model=LiveStateResponse)
def send_reply(payload: ReplyRequest) -> LiveStateResponse:
    return live_ops_service.send_reply(payload)
