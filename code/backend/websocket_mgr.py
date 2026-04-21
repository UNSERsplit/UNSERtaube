import traceback
import av, av.error
import uuid
import threading

from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState
from video_writer import VideoWriter
from vision.VisionWorker import VisionWorker
from dronemaster.connection import PathCalculation, CanvasWaypoints
from websocket.ws_messages import *
from websocket.webrtc import offer
from dronemaster import Drone, State
from dronemaster.utils import log
from database import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_
import numpy as np
import struct
from typing import Optional
import datetime
import math

from models.drone import Drone as DBDrone
from models.route import Route, RouteEntry

class FrameReader:
    def __init__(self, port, mock=False) -> None:
        self.mock = mock
        if mock:
            return
        self.container = av.open(f"udp://0.0.0.0:{port}", timeout=(5, None))
        self.frame = None
        self.raw_frame = None
        self.stopped = False

        self.thread = threading.Thread(target=self._update_frame, daemon=True)
    
    def start(self):
        if self.mock:
            self._update_frame()
            return
        self.thread.start()
    
    def close(self):
        if self.mock:
            return
        self.container.close()
    
    def _update_frame(self):
        if self.mock:
            self.frame = np.full((1080, 720, 3), 100, dtype=np.uint8)
            self.on_frame(self.frame)
            return
        try:
            for frame in self.container.decode(video=0):
                self.raw_frame = frame
                self.on_frame(frame)
                self.frame = np.array(frame.to_image())
                if self.stopped:
                    self.container.close()
                    break
        except av.error.ExitError | av.error.ValueError:
            print('Do not have enough frames for decoding, please try again or increase video fps before get_frame_read()')
    
    def on_frame(self, frame):
        pass


class WebsocketManager:
    def __init__(self) -> None:
        self.connections: dict[WebSocket, WsConnection] = {}
    def stop(self):
        for ws, conn in self.connections.items():
            conn.end_capture(None)
            conn.drone = None #type: ignore
    
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
        self.db_drone: Optional[DBDrone] = None
        self.pathcalculation = PathCalculation()
        self.video_writer = VideoWriter()
        self.vision_worker = VisionWorker()
        self.reader = None

    async def connect(self):
        pass

    async def disconnect(self, reason: str):
        if self.drone:
            drone = self.drone
            self.drone = None # type: ignore
            log("Disconnect", reason)
            try:
                await drone.ext.led_set(255,0,0)
            except Exception:
                pass
            try:
                self.end_capture(None)
            except Exception:
                pass
            try:
                await drone.stopstream()
            except Exception:
                pass
            try:
                await drone.disconnect()
            except Exception:
                pass
            if self.reader:
                self.reader.close()

        await self.trysend(DroneDisconnected(reason=reason))


    async def send(self, data: ClientBoundMessage):
        await self.mngr.send(self.ws, data)
    
    async def send_bytes(self, data: bytes):
        await self.mngr.send_bytes(self.ws, data)

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

    def on_frame(self, frame):
        self.video_writer.feed(frame)


    def start_capture(self):
        self.drone.start_recording()
        name = self.video_writer.start(uuid.uuid4().hex) # TODO insert into db
        print("Recording to " + name)
        return name

    def end_capture(self, session: Optional[Session], name: str = "NAME"):
        ts_start, raw_data = self.drone.stop_recording()
        if self.drone.connection.sdk_version == -1:
            filename = "NOTEXISTING.MP4" # mocking drone
        else:
            filename = self.video_writer.end()

        if not session or name == "":
            return
        assert self.db_drone is not None

        route = Route()
        route.name = name # pyright: ignore[reportAttributeAccessIssue]
        route.video = filename # pyright: ignore[reportAttributeAccessIssue]
        route.drone_id = self.db_drone.id
        route.distance = 20
        route.duration = -1 # pyright: ignore[reportAttributeAccessIssue]
        session.add(route)
        session.commit()

        duration = 0

        for data in raw_data:
            ts, row = data

            if isinstance(row, str):
                if row == "land":
                    row = (-999, -999, -999, -999)
                if row == "takeoff":
                    row = (999, 999, 999, 999)

            roll, pitch, throttle, yaw = row
            entry = RouteEntry()
            entry.route_id = route.id
            if (ts - ts_start) / 1e9 > duration:
                duration = (ts - ts_start) / 1e9
            entry.Timestamp = datetime.datetime.fromtimestamp((ts - ts_start) / 1e9)
            entry.Pitch = pitch
            entry.Roll = roll
            entry.Throttle = throttle
            entry.Yaw = yaw
            session.add(entry)
        
        route.duration = math.ceil(duration)
        

        session.commit()

        return filename

    async def replayRoute(self, session: Session, id: str):
        stmt = select(Route).where(Route.id == id)
        route = session.execute(stmt).scalar_one()
        
        stmt = select(RouteEntry).where(RouteEntry.route_id == id)
        routeEntries = session.execute(stmt).all()

        entries = []

        prev = 0

        for row in routeEntries:
            entry = row.tuple()[0]

            _ts = entry.Timestamp.timestamp()
            ts = _ts - prev
            prev = _ts
            log("DEBUG", ts)
            pitch = entry.Pitch
            roll = entry.Roll
            throttle = entry.Throttle
            yaw = entry.Yaw
            

            if pitch == -999:
                entries.append((ts, "land"))
            elif pitch == 999:
                entries.append((ts, "takeoff"))
            else:
                entries.append((ts, (roll, pitch, throttle, yaw)))
        
        self.drone.replay_route(entries)


    async def on_state(self, state: State):
        await self.pathcalculation.incoming_callback(state=state)
        await self.send(StateMessage(state=state))
        await self.sendpathpoints()
        if self.reader:
            frame = self.reader.frame
            if frame is not None:
                #print(np.average(frame))
                frame = self.vision_worker.on_frame(frame)

                h, w, _ = frame.shape
                #print(len(frame.tobytes()), w * h * 3)
                header = struct.pack("III", w, h, 3)
                await self.send_bytes(header + frame.tobytes())
                #self.on_frame(self.reader.raw_frame)

    async def _disconnect_from_timeout(self):
        await self.disconnect("Drone stopped sending state messages")
    
    def get_drone(self, name: str, ip: str, session: Session):
        stmt = select(DBDrone).where(and_(
            func.lower(DBDrone.name) == func.lower(name),
            DBDrone.ip == ip))
        
        drones = session.scalars(stmt).fetchall()

        if len(drones) > 0:
            return drones[0]
        
        drone = DBDrone()
        drone.ip = ip # pyright: ignore[reportAttributeAccessIssue]
        drone.name = name # pyright: ignore[reportAttributeAccessIssue]

        session.add(drone)
        session.commit()
        session.refresh(drone)

        return drone

    async def on_message(self, data: messages):
        session = SessionLocal()

        try:
            match data:
                case DebugFineTuneVision():
                    self.vision_worker.hue_lower = data.hue_lower
                    self.vision_worker.hue_upper = data.hue_upper
                    self.vision_worker.saturation_lower = data.saturation_lower
                    self.vision_worker.saturation_upper = data.saturation_upper
                    self.vision_worker.value_lower = data.value_lower
                    self.vision_worker.value_upper = data.value_upper
                    self.vision_worker.show_filtered_frame = data.show_processed_output

                case ConnectToDrone():
                    self.db_drone = self.get_drone(data.name, data.ip, session)
                    self.drone = Drone(data.ip)
                    await self.drone.connect()
                    await self.drone.startstream()
                    
                    self.drone.set_state_callback(self.on_state)
                    self.drone.set_disconnect_callback(self._disconnect_from_timeout)
                    await self.drone.ext.led_set(0, 0, 255)
                    self.reader = FrameReader(self.drone.get_video_port(), mock=self.drone.connection.sdk_version == -1)
                    self.reader.start()
                    self.reader.on_frame = self.on_frame
                    
                    await self.send(DroneConnected())
                case TakeOff():
                    self.assertDrone()
                    await self.drone.takeoff()
                    await self.send(Accepted())
                case Land():
                    self.assertDrone()
                    await self.drone.land()
                    await self.send(Accepted())
                case FunkiMessage():
                    self.assertDrone()
                    self.drone.rc(data.roll, data.pitch, data.throttle, data.yaw)
                case DisconnectFromDrone():
                    await self.disconnect(reason="User")
                case StartRecording():
                    self.assertDrone()
                    self.start_capture()
                case StopRecording():
                    self.assertDrone()
                    filename = self.end_capture(session, name=data.route_name)
                    assert filename is not None
                    await self.send(RecordingResult(name=filename))
                case SetStartupMatrix():
                    self.assertDrone()
                    await self.drone.ext.matrix_set_startup_pattern(colorstr=data.data)
                case SetMatrix():
                    self.assertDrone()
                    await self.drone.ext.matrix_set_pattern(colorstr=data.data)
                case SetStaticLed():
                    self.assertDrone()
                    await self.drone.ext.led_set(data.red, data.green, data.blue)
                case SetPulsingLed():
                    self.assertDrone()
                    await self.drone.ext.led_pulse(data.red, data.green, data.blue, data.freq)
                case SetFlashingLed():
                    self.assertDrone()
                    await self.drone.ext.led_flash(data.red1, data.green1, data.blue1, data.freq, data.red2, data.green2, data.blue2)
                case Emergency():
                    self.assertDrone()
                    await self.drone.emergency_stop()
                case ReplayRoute():
                    self.assertDrone()
                    await self.replayRoute(session, data.id)
                    await self.send(Accepted())
                case DebugSendRawCommand():
                    self.assertDrone()
                    if data.wait_for_response:
                        response = await self.drone.connection.send_raw_message(data.command, timeout=data.timeout)
                        await self.send(DebugCommandAnswer(answer=response))
                    else:
                        self.drone.connection.send_message_noanswer(data.command)


        except TimeoutError as e:
            await self.disconnect(reason=" ".join(e.args))
        except ConnectionError as e:
            await self.send(Error(context=list(e.args), traceback=e.args[0]))
        except BaseException as e:
            tr = traceback.format_exc()
            print(tr)
            await self.send(Error(context=list(e.args), traceback=tr))
        finally:
            session.close()

    def assertDrone(self):
        if not self.drone:
            raise ConnectionError("drone not available")