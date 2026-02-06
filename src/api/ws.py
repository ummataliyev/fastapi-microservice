"""
WebSocket API endpoints for real-time communication.
"""

import re

from fastapi import status
from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from src.core.observability.logging import logger

from src.managers.websocket import WebSocketConnectionManager

from src.security.exceptions.token import TokenError
from src.security.implementations.jwt_service import JWTTokenService

router = APIRouter(
    prefix="/ws",
    tags=["WebSocket"]
)

ROOM_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


@router.websocket("/chat/{room}")
async def websocket_endpoint(
    websocket: WebSocket,
    room: str,
):
    """
    WebSocket endpoint for real-time chat in a specific room.

    :param websocket: The WebSocket connection for the client.
    :param room: Identifier for the chat room.
    :return: None
    """
    if not ROOM_PATTERN.fullmatch(room):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    token = websocket.query_params.get("token")
    username = "guest"

    if token:
        try:
            payload = JWTTokenService().decode(token)
            if payload.get("type") != "access":
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
            username = str(payload.get("email") or payload.get("sub") or "guest")
        except TokenError:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    await WebSocketConnectionManager.connect(room, websocket)
    logger.info("WebSocket connected room=%s user=%s", room, username)

    try:
        while True:
            data = await websocket.receive_text()
            await WebSocketConnectionManager.broadcast(
                room,
                f"{username}: {data}"
            )
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected room=%s user=%s", room, username)
        WebSocketConnectionManager.disconnect(room, websocket)
    except Exception:
        logger.exception("WebSocket error room=%s user=%s", room, username)
        WebSocketConnectionManager.disconnect(room, websocket)
