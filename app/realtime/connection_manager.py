from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.trip_connections: dict[str, list[WebSocket]] = defaultdict(list)
        self.driver_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect_trip(self, trip_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.trip_connections[trip_id].append(websocket)

    async def connect_driver(self, driver_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.driver_connections[driver_id].append(websocket)

    def disconnect_trip(self, trip_id: str, websocket: WebSocket) -> None:
        if websocket in self.trip_connections[trip_id]:
            self.trip_connections[trip_id].remove(websocket)

    def disconnect_driver(self, driver_id: str, websocket: WebSocket) -> None:
        if websocket in self.driver_connections[driver_id]:
            self.driver_connections[driver_id].remove(websocket)

    async def broadcast_trip(self, trip_id: str, payload: dict) -> None:
        for connection in self.trip_connections[trip_id]:
            await connection.send_json(payload)


manager = ConnectionManager()
