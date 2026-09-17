import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

logger = logging.getLogger("shopsense.websocket")

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    """Manages active dashboard WebSocket clients with vendor and admin role isolation."""

    def __init__(self):
        # List of active connections: [{"ws": WebSocket, "role": str, "vendor_id": Optional[int]}]
        self.active_connections: List[Dict[str, Any]] = []

    async def connect(self, websocket: WebSocket, role: str = "Vendor", vendor_id: Optional[int] = None):
        await websocket.accept()
        self.active_connections.append({
            "ws": websocket,
            "role": role,
            "vendor_id": vendor_id
        })
        logger.info(f"WebSocket client connected: role={role}, vendor_id={vendor_id}. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections = [conn for conn in self.active_connections if conn["ws"] != websocket]
        logger.info(f"WebSocket client disconnected. Total active: {len(self.active_connections)}")

    async def broadcast_new_sale(self, sale_data: dict):
        """
        Broadcasts new sale event with strict role isolation:
        - Admin receives all sales across the marketplace.
        - Vendor only receives sales where vendor_id matches their own store.
        - Failure to broadcast to any client never raises an exception.
        """
        if not self.active_connections:
            logger.debug("No active WebSocket clients connected to receive sale broadcast.")
            return

        sale_vendor_id = sale_data.get("vendor_id")
        payload = {
            "event": "new_sale",
            "data": sale_data
        }

        dead_connections = []
        for client in list(self.active_connections):
            client_ws: WebSocket = client["ws"]
            client_role = client.get("role", "Vendor")
            client_vendor_id = client.get("vendor_id")

            # Route by authorization: Admin gets all, Vendor gets only their own
            should_send = False
            if client_role == "Admin":
                should_send = True
            elif client_role == "Vendor" and client_vendor_id is not None and sale_vendor_id is not None:
                if int(client_vendor_id) == int(sale_vendor_id):
                    should_send = True

            if should_send:
                try:
                    await client_ws.send_json(payload)
                except Exception as e:
                    logger.warning(f"Failed to send to client ({client_role}, {client_vendor_id}): {e}")
                    dead_connections.append(client_ws)

        for dead_ws in dead_connections:
            self.disconnect(dead_ws)


# Global singleton ConnectionManager
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    role: Optional[str] = Query("Vendor"),
    vendor_id: Optional[int] = Query(None)
):
    """
    WebSocket endpoint for real-time dashboard notifications:
    ws://<host>/ws?role=Vendor&vendor_id=9
    ws://<host>/ws?role=Admin
    """
    await manager.connect(websocket, role=role, vendor_id=vendor_id)
    try:
        while True:
            # Keep connection open and respond to heartbeats
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.debug(f"WebSocket error: {e}")
        manager.disconnect(websocket)
