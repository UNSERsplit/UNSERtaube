from starlette.websockets import WebSocket

class WebsocketManager:
    def __init__(self) -> None:
        self.connections = []
    
    async def connnect(self, ws: WebSocket):
        self.connections.append(ws)
    
    async def on_message(self, data: dict):
        pass