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
import numpy as np
import struct
import cv2

class FrameReader:
    def __init__(self, port) -> None:
        self.container = av.open(f"udp://0.0.0.0:{port}", timeout=(5, None))
        self.frame = None
        self.raw_frame = None
        self.stopped = False

        self.thread = threading.Thread(target=self._update_frame, daemon=True)
    
    def start(self):
        self.thread.start()
    
    def _update_frame(self):
        try:
            for frame in self.container.decode(video=0):
                self.raw_frame = frame
                self.on_frame(frame)
                self.frame = np.array(frame.to_image())
                if self.stopped:
                    self.container.close()
                    break
        except av.error.ExitError:
            print('Do not have enough frames for decoding, please try again or increase video fps before get_frame_read()')
    
    def on_frame(self, frame):
        pass


class WebsocketManager:
    def __init__(self) -> None:
        self.connections: dict[WebSocket, WsConnection] = {}
    def stop(self):
        for ws, conn in self.connections.items():
            conn.end_capture()
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
                self.end_capture()
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
        name = self.video_writer.start(uuid.uuid4().hex) # TODO insert into db
        print("Recording to " + name)
        return name

    def end_capture(self):
        return self.video_writer.end()

    def modify_frame(self, frame):
        img = cv2.bilateralFilter(frame, 11, 75, 75)

        img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

        # Lower mask (0-10)
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        mask0 = cv2.inRange(img_hsv, lower_red, upper_red)

        # Upper mask (170-180)
        lower_red = np.array([170, 100, 100])
        upper_red = np.array([180, 255, 255])
        mask1 = cv2.inRange(img_hsv, lower_red, upper_red)

        # Join the masks
        raw_mask = mask0 | mask1

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))

        raw_mask = cv2.morphologyEx(raw_mask, cv2.MORPH_OPEN, kernel, iterations=2)
        raw_mask = cv2.morphologyEx(raw_mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        ctns = cv2.findContours(raw_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]  # Find contours

        final = cv2.drawContours(cv2.bitwise_and(img, img, mask=raw_mask), ctns, -1, (0,255,0), 3)

        return final

        ctns = cv2.findContours(raw_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]  # Find contours
        big_contour = []

        ctns_sorted = sorted(ctns, key=cv2.contourArea)

        for i, ctns in enumerate(ctns_sorted):
            if i > 4:
                break
            big_contour.append(ctns)
        final = cv2.drawContours(cv2.bitwise_and(img, img, mask=raw_mask), ctns, -1, (0,255,0), 3)

        return final
        

        ctns = cv2.findContours(raw_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]  # Find contours

        mask = np.zeros_like(raw_mask)  # Fill mask with zeros

        o = np.zeros_like(frame)

        idx = 0
        # Iterate contours
        for c in ctns:
            area = cv2.contourArea(c)  # Find the area of each contours

            if (area > 50):  # Ignore small contours (assume noise).
                cv2.drawContours(mask, [c], 0, 255, -1)

                # https://docs.opencv.org/3.4/dd/d49/tutorial_py_contour_features.html
                (x, y), radius = cv2.minEnclosingCircle(c)
                center = (int(x), int(y))
                radius = int(radius)
                cv2.circle(mask, center, radius, 255, -1)

                tmp_mask = np.zeros_like(mask)
                cv2.circle(tmp_mask, center, radius, 255, -1)
                output = cv2.bitwise_and(img, img, mask=tmp_mask)
                cv2.bitwise_or(o, output, o)
                idx += 1

        return o

    async def on_state(self, state: State):
        await self.pathcalculation.incoming_callback(state=state)
        await self.send(StateMessage(state=state))
        await self.sendpathpoints()
        if self.reader:
            frame = self.reader.frame
            if frame is not None:
                #print(np.average(frame))
                #frame = self.modify_frame(frame)
                frame = self.vision_worker.on_frame(frame)

                h, w, _ = frame.shape
                #print(len(frame.tobytes()), w * h * 3)
                header = struct.pack("III", w, h, 3)
                await self.send_bytes(header + frame.tobytes())
                #self.on_frame(self.reader.raw_frame)

    async def _disconnect_from_timeout(self):
        await self.disconnect("Drone stopped sending state messages")

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
                    self.drone = Drone(data.ip)
                    await self.drone.connect()
                    await self.drone.startstream()
                    
                    self.drone.set_state_callback(self.on_state)
                    self.drone.set_disconnect_callback(self._disconnect_from_timeout)
                    await self.drone.ext.led_set(0, 0, 255)
                    self.reader = FrameReader(self.drone.get_video_port())
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
                    filename = self.end_capture()
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