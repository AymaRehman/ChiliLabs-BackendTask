from typing import Dict, List
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        # user_id: [WebSocket, ...]
        self.active: Dict[int, List[WebSocket]] = {}

    async def connect(self, user_id: int, ws: WebSocket):
        await ws.accept()
        self.active.setdefault(user_id, []).append(ws)

    async def disconnect(self, user_id: int, ws: WebSocket):
        if user_id in self.active and ws in self.active[user_id]:
            self.active[user_id].remove(ws)
            if not self.active[user_id]:
                del self.active[user_id]

    async def send_user(self, user_id: int, message: str):
        """Send a message to all sockets of a user."""
        if user_id not in self.active:
            return

        dead = []

        for ws in self.active[user_id]:
            try:
                await ws.send_text(message)
            except:
                dead.append(ws)

        # cleanup disconnected sockets
        for ws in dead:
            self.active[user_id].remove(ws)

        if not self.active[user_id]:
            del self.active[user_id]

    async def broadcast(self, message: str):
        """Send to everyone."""
        dead = []
        for user_id, sockets in self.active.items():
            for ws in sockets:
                try:
                    await ws.send_text(message)
                except:
                    dead.append((user_id, ws))

        # cleanup
        for user_id, ws in dead:
            self.active[user_id].remove(ws)
            if not self.active[user_id]:
                del self.active[user_id]
