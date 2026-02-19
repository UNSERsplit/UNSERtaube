import threading
from threading import Thread

from starlette.websockets import WebSocket, WebSocketDisconnect
from websocket.ws_messages import messages, ConnectToDrone, Land, TakeOff, FunkiMessage, ClientBoundMessage, DroneConnected, DroneDisconnected, DisconnectFromDrone, Error, Accepted, StateMessage
from dronemaster import Drone, State
from database import SessionLocal


class WebsocketManager:
    def __init__(self) -> None:
        self.connections: dict[WebSocket, WsConnection] = {}
    
    async def connnect(self, ws: WebSocket):
        self.connections[ws] = WsConnection(ws, self)
    
    async def disconnect(self, ws: WebSocket):
        await self.connections[ws].disconnect("WS disconnect")
        del self.connections[ws]
    
    async def send(self, ws: WebSocket, data: ClientBoundMessage):
        try:
            await ws.send_json(data.model_dump())
        except WebSocketDisconnect:
            del self.connections[ws]
    
    async def send_bytes(self, ws: WebSocket, data: bytes):
        try:
            await ws.send_bytes(data)
        except WebSocketDisconnect:
            del self.connections[ws]
    
    async def on_message(self, ws: WebSocket, data: messages):
        await self.connections[ws].on_message(data)

class WsConnection:
    def __init__(self, ws: WebSocket, mngr: WebsocketManager) -> None:
        self.ws = ws
        self.mngr = mngr
        self.drone: Drone = None # type: ignore
    
    async def connect(self):
        pass

    async def disconnect(self, reason: str):
        if self.drone:
            await self.drone.stopstream()
        if self.drone:
            await self.drone.disconnect()

        await self.trysend(DroneDisconnected(reason=reason))

    async def send(self, data: ClientBoundMessage):
        await self.mngr.send(self.ws, data)
    
    async def trysend(self, data: ClientBoundMessage):
        try:
            await self.send(data)
        except Exception:
            pass
    
    async def on_frame(self, data: bytes):
        await self.mngr.send_bytes(self.ws, data)
    
    async def on_state(self, state: State):
        await self.send(StateMessage(state=state))

    async def on_message(self, data: messages):
        session = SessionLocal()

        try:
            match data:
                case ConnectToDrone():
                    self.drone = Drone(data.ip)
                    await self.drone.connect()
                    await self.drone.startstream(self.on_frame)
                    self.drone.set_state_callback(self.on_state)
                    await self.send(DroneConnected())
                case TakeOff():
                    await self.drone.takeoff()
                    await self.send(Accepted())
                case Land():
                    await self.drone.land()
                    await self.send(Accepted())
                case FunkiMessage():
                    self.drone.rc(data.roll, data.pitch, data.throttle, data.yaw)
                case DisconnectFromDrone():
                    await self.disconnect(reason="User")
        except TimeoutError as e:
            await self.disconnect(reason=" ".join(e.args))
        except BaseException as e:
            await self.send(Error(context=e.args))
        finally:
            session.close()