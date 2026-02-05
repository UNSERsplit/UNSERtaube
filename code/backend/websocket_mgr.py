import threading
from threading import Thread

from starlette.websockets import WebSocket, WebSocketDisconnect
from websocket.ws_messages import messages, ConnectToDrone, Land, TakeOff, FunkiMessage, ClientBoundMessage, DroneConnected, DroneDisconnected
from dronemaster import Drone
from database import SessionLocal
from websocket.ws_stream import listenToStream


class WebsocketManager:
    def __init__(self) -> None:
        self.connections: dict[WebSocket, WsConnection] = {}
    
    async def connnect(self, ws: WebSocket):
        self.connections[ws] = WsConnection(ws, self)
    
    async def send(self, ws: WebSocket, data: ClientBoundMessage):
        try:
            await ws.send_json(data.model_dump())
        except WebSocketDisconnect:
            del self.connections[ws]
    
    async def on_message(self, ws: WebSocket, data: messages):
        await self.connections[ws].on_message(data)

class WsConnection:
    def __init__(self, ws: WebSocket, mngr: WebsocketManager) -> None:
        self.ws = ws
        self.mngr = mngr
        self.drone: Drone
        thread_stream = threading.Thread(target=listenToStream, args=(self.ws, self.stop_stream_event))
        self.stop_stream_event = threading.Event()
    
    async def connect(self):
        pass

    async def send(self, data: ClientBoundMessage):
        await self.mngr.send(self.ws, data)

    async def on_message(self, data: messages):
        session = SessionLocal()

        try:
            match data:
                case ConnectToDrone():
                    self.drone = Drone(data.ip)
                    await self.drone.connect()
                    self.stop_stream_event.clear()
                    await self.drone.startstream()
                    thread_stream.start()
                    await self.send(DroneConnected())
                case TakeOff():
                    await self.drone.takeoff()
                case Land():
                    await self.drone.land()
                case FunkiMessage():
                    self.drone.rc(data.roll, data.pitch, data.throttle, data.yaw)
                case DroneDisconnected():
                    await self.stop_stream_event.set()
                    tread_stream.join()
        except TimeoutError:
            await self.send(DroneDisconnected())
        finally:
            session.close()