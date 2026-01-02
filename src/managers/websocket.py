"""
WebSocket connection manager for handling real-time communication.
"""

from typing import Set
from typing import Dict

from fastapi import WebSocket


class WebSocketConnectionManager:
    active_connections: Dict[str, Set[WebSocket]] = {}

    @classmethod
    async def connect(cls, room: str, websocket: WebSocket):
        """
        Accepts and registers a new WebSocket connection under a room.

        :param room: Logical room/channel identifier.
        :param websocket: FastAPI WebSocket instance for the client.
        :return: None
        """
        await websocket.accept()
        cls.active_connections.setdefault(room, set()).add(websocket)

    @classmethod
    def disconnect(cls, room: str, websocket: WebSocket):
        """
        Removes a WebSocket connection from a room. Cleans up empty rooms.

        :param room: Room/channel identifier.
        :param websocket: WebSocket to remove.
        :return: None
        """
        if room in cls.active_connections:
            cls.active_connections[room].discard(websocket)
            if not cls.active_connections[room]:
                del cls.active_connections[room]

    @classmethod
    async def send_personal(cls, websocket: WebSocket, message: str):
        """
        Sends a direct message to a WebSocket connection.

        :param websocket: Target WebSocket.
        :param message: Text message to send.
        :return: None
        """
        await websocket.send_text(message)

    @classmethod
    async def broadcast(cls, room: str, message: str):
        """
        Broadcasts a message to all WebSockets in a room.

        Removes any connections that fail to send.

        :param room: Room identifier.
        :param message: Message to broadcast.
        :return: None
        """
        if room not in cls.active_connections:
            return

        for connection in list(cls.active_connections[room]):
            try:
                await connection.send_text(message)
            except Exception:
                cls.disconnect(room, connection)
