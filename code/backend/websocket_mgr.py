from starlette.websockets import WebSocket
from websocket.ws_messages import messages

class WebsocketManager:
    def __init__(self) -> None:
        self.connections = []
    
    async def connnect(self, ws: WebSocket):
        self.connections.append(ws)
    
    async def on_message(self, ws: WebSocket, data: messages):
        pass