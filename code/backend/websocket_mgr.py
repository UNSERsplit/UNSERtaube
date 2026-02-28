import traceback
from threading import Thread

from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState
from starlette.websockets import WebSocket, WebSocketDisconnect
from dronemaster.connection import PathCalculation, CanvasWaypoints
from websocket.ws_messages import *
from websocket.webrtc import offer
from dronemaster import Drone, State
from database import SessionLocal


class WebsocketManager:
    def __init__(self) -> None:
        self.connections: dict[WebSocket, WsConnection] = {}
    
    async def connnect(self, ws: WebSocket):
        self.connections[ws] = WsConnection(ws, self)
    
    async def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            await self.connections[ws].disconnect("WS disconnect")
            if ws in self.connections:
                del self.connections[ws]

    async def send(self, ws: WebSocket, data: ClientBoundMessage):
        try:
            if ws.client_state != WebSocketState.CONNECTED:
                raise WebSocketDisconnect()
            await ws.send_json(data.model_dump())
        except WebSocketDisconnect:
            await self.disconnect(ws)

    async def send_bytes(self, ws: WebSocket, data: bytes):
        try:
            if ws.client_state != WebSocketState.CONNECTED:
                raise WebSocketDisconnect()
            await ws.send_bytes(data)
        except WebSocketDisconnect:
            await self.disconnect(ws)


    async def on_message(self, ws: WebSocket, data: messages):
        await self.connections[ws].on_message(data)

class WsConnection:
    def __init__(self, ws: WebSocket, mngr: WebsocketManager) -> None:
        self.ws = ws
        self.mngr = mngr
        self.drone: Drone = None # type: ignore
        self.pathcalculation = PathCalculation()

    async def connect(self):
        pass

    async def disconnect(self, reason: str):
        if self.drone:
            try:
                await self.drone.stopstream()
            except Exception:
                pass
            try:
                await self.drone.disconnect()
            except Exception:
                pass

        await self.trysend(DroneDisconnected(reason=reason))

    async def send(self, data: ClientBoundMessage):
        await self.mngr.send(self.ws, data)

    async def trysend(self, data: ClientBoundMessage):
        try:
            await self.send(data)
        except Exception:
            pass

    async def sendpathpoints(self):
        try:
            await self.send(SendWaypoints(context=self.pathcalculation.canvas_waypoints.getwaypoints()))
        except Exception:
            pass


    async def on_frame(self, data: bytes):
        await self.mngr.send_bytes(self.ws, data)

    async def on_state(self, state: State):
        await self.pathcalculation.incoming_callback(state=state)
        await self.send(StateMessage(state=state))
        await self.sendpathpoints()

    async def on_message(self, data: messages):
        session = SessionLocal()

        try:
            match data:
                case ConnectToDrone():
                    self.drone = Drone(data.ip)
                    await self.drone.connect()
                    await self.drone.startstream()
                    rtc_server = await offer(data.rtc_sdp, data.rtc_type, self.drone.get_video_port())
                    self.drone.set_video_stream(rtc_server["track"])
                    self.drone.set_state_callback(self.on_state)
                    await self.send(DroneConnected(rtc_sdp=rtc_server["sdp"], rtc_type=rtc_server["type"]))
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
            tr = traceback.format_exc()
            print(tr)
            await self.send(Error(context=list(e.args), traceback=tr))
        finally:
            session.close()