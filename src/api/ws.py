"""
WebSocket API endpoints for real-time communication.
"""

from typing import Optional

from fastapi import status
from fastapi import Query
from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from src.managers.websocket import WebSocketConnectionManager

router = APIRouter(
    prefix="/ws",
    tags=["WebSocket"]
)


@router.websocket("/chat/{room}")
async def websocket_endpoint(
    websocket: WebSocket,
    room: str,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time chat in a specific room.

    :param websocket: The WebSocket connection for the client.
    :param room: Identifier for the chat room.
    :param token: Optional authentication token passed as query parameter.
    :return: None
    """
    username = "guest"
    if token:
        try:
            # Import your auth function here
            # from src.api.dependencies.auth import verify_token
            # user = await verify_token(token)
            # username = user.email
            pass
        except Exception:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    await WebSocketConnectionManager.connect(room, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            await WebSocketConnectionManager.broadcast(
                room,
                f"{username}: {data}"
            )
    except WebSocketDisconnect:
        WebSocketConnectionManager.disconnect(room, websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        WebSocketConnectionManager.disconnect(room, websocket)
