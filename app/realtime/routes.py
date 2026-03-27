from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.realtime.connection_manager import manager

router = APIRouter()


@router.websocket("/ws/trips/{trip_id}")
async def trip_events(websocket: WebSocket, trip_id: str) -> None:
    await manager.connect_trip(trip_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast_trip(trip_id, {"trip_id": trip_id, "event": data})
    except WebSocketDisconnect:
        manager.disconnect_trip(trip_id, websocket)


@router.websocket("/ws/drivers/{driver_id}/location")
async def driver_location_stream(websocket: WebSocket, driver_id: str) -> None:
    await manager.connect_driver(driver_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await websocket.send_json({"driver_id": driver_id, "received": data, "status": "ok"})
    except WebSocketDisconnect:
        manager.disconnect_driver(driver_id, websocket)
