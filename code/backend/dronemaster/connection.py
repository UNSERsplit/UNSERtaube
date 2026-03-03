from fractions import Fraction
import socket
import threading
import random
import time
from typing import Dict, Optional, Coroutine, Callable, Any
from asyncio import Future, get_event_loop, AbstractEventLoop
import ipaddress
from pydantic import BaseModel
import av
import hashlib
from av.container import InputContainer
import io

from websocket.webrtc import UDPVideoTrack

from .utils import find_mac, log

class State(BaseModel):
     pitch: int # pitch in degrees
     roll: int # roll in degrees
     yaw: int # yaw in degrees
     vgx: int # speed x in dm/s
     vgy: int # speed y in dm/s
     vgz: int # speed z in dm/s
     bat: int # battery in percent
     templ: int # temperature range low in °C
     temph: int # temperature range high in °C

     agx: float # acceleration x in cm/s²
     agy: float # acceleration y in cm/s²
     agz: float # acceleration z in cm/s²

class Connection:
    def __init__(self, target_ip: str, socket: socket.socket, loop: AbstractEventLoop) -> None:
        self.ip = target_ip
        self.dest = (target_ip, ConnectionManager.REMOTE_CMD_PORT)
        self.loop: AbstractEventLoop = loop
        self.socket = socket
        self.last_sent_timestamp = 0
        self.async_future: Optional[Future[str]] = None
        self.read_data: Optional[str] = None # data to read
        self.state_callback: Optional[Callable[[State], Coroutine[Any, Any, None]]] = None
        self.future_video_port = int(hashlib.sha256(self.ip.encode('utf-8')).hexdigest(), 16) % (ConnectionManager.LOCAL_VIDEO_PORT_MAX - ConnectionManager.LOCAL_VIDEO_PORT_MIN) + ConnectionManager.LOCAL_VIDEO_PORT_MIN
        self.videoTrack: Optional[UDPVideoTrack] = None

    def setupStateCallback(self, cb: Callable[[State], Coroutine[Any, Any, None]]):
        self.state_callback = cb
    
    def setVideoTrack(self, track: UDPVideoTrack):
        self.videoTrack = track

    async def setupVideoStream(self):
        await self.send_control_message("moff") # mission pad off
        await self.send_control_message("downvision 0")
        await self.send_control_message("setfps high")
        await self.send_control_message("setbitrate 5")
        await self.send_control_message("setresolution high")
        await self.send_control_message(f"port {ConnectionManager.LOCAL_STATE_PORT} {self.future_video_port}")

    async def _connect(self): # called by ConnectionManager.connect
        await self.send_control_message("command")

    def _disconnect(self): # called by ConnectionManager.disconnect
        try:
            if self.videoTrack:
                self.videoTrack.stop()
        except Exception as e:
            log("ERROR", "stopping video stream")
        self.send_message_noanswer("streamoff")
        self.send_message_noanswer("emergency")

    async def disconnect(self):
        await connection_manager.disconnect(self.ip)

    def _run_task(self, task, *args):
        self.loop.create_task(task(*args))

    def on_data(self, raw_data: bytes): # called when new data for this ip is received
        data = raw_data.decode()
        log("MSG", "D->S", data)

        if self._is_state_message(data):
            state = self.parse_state(data)
            if self.state_callback:
                self.loop.call_soon_threadsafe(self._run_task, self.state_callback, state)
        else:
            if self.async_future is not None and not self.async_future.done():
                self.loop.call_soon_threadsafe(self.async_future.set_result, data)
            else:
                log("DEBUG", f"Unsolicited data received {self.ip}: {data}")
    
    def parse_state(self, raw_data: str) -> State:
        INT_FIELDS = ("pitch", "roll", "yaw", "vgx", "vgy", "vgz", "bat", "templ", "temph")
        FLOAT_FIELDS = ("agx", "agy", "agz")

        state = State.model_construct()
        for entry in raw_data.strip().split(";"):
            if not entry:
                continue
            name, value = entry.split(":")

            if name in INT_FIELDS:
                setattr(state, name, int(value))
            if name in FLOAT_FIELDS:
                setattr(state, name, float(value))

        return state


    def _is_state_message(self, data: str):
        return data.startswith("mid:")

    async def send_raw_message(self, message: str, timeout: float = 5) -> str:
        self._delay()
        log("MSG", "S->D", message)
        self.loop = get_event_loop()
        if self.async_future is not None:
            await self.async_future

        timer = threading.Timer(timeout, lambda : self.loop.call_soon_threadsafe(self.async_future.set_exception, TimeoutError(f"The drone did not respond withing {timeout}s")) if self.async_future is not None else None)
        self.async_future = self.loop.create_future()
        timer.start()
        self.socket.sendto(message.encode(), self.dest)
        result = await self.async_future
        timer.cancel()
        return result.strip()

    async def send_control_message(self, message: str, timeout: float = 5) -> bool:
        response = await self.send_raw_message(message, timeout)
        if response.strip().upper() == "OK":
            return True
        raise ConnectionError(f"drone responed to {message} with {response}")

    def send_message_noanswer(self, message: str):
        self._delay()
        log("MSG", "S->D (noanswer)", message)
        self.socket.sendto(message.encode(), self.dest)

    def _delay(self):
        diff = time.time() - self.last_sent_timestamp
        if diff < ConnectionManager.TIME_BETWEEN_COMMANDS:
            time.sleep(diff)
        self.last_sent_timestamp = time.time()


class ConnectionManager:
    LOCAL_IP = "0.0.0.0"

    LOCAL_STATE_PORT = 8890
    LOCAL_VIDEO_PORT_MIN = 11111
    LOCAL_VIDEO_PORT_MAX = 55555
    REMOTE_CMD_PORT = 8889

    TIME_BETWEEN_COMMANDS = 0.5

    def __init__(self) -> None:
        self.event = threading.Event()
        self.loop = get_event_loop()
        self.data_received_from_ip = set()

        self.connections: Dict[str, Connection] = {}

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(2)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((
            ConnectionManager.LOCAL_IP,
            ConnectionManager.LOCAL_STATE_PORT
        ))

        self.thread = threading.Thread(target=self._run)
        self.thread.start()
    
    def _run_task(self, task, *args):
        self.loop.create_task(task(*args))

    async def connect(self, target_ip: str) -> Connection:
        if target_ip in self.connections:
            return self.connections[target_ip]

        conn = Connection(target_ip, self.socket, self.loop)
        self.connections[target_ip] = conn
        await conn._connect()
        return conn

    async def disconnect(self, ip: str):
        if ip not in self.connections:
            return
        self.connections[ip]._disconnect()

        del self.connections[ip]


    def stop(self):
        self.event.set()

        for ip, connection in self.connections.items():
            try:
                connection._disconnect()
            except Exception as e:
                log("ERROR", "drone disconnect failed", e)

    def _run(self):
        while not self.event.is_set():
            try:
                data, addr = self.socket.recvfrom(1024)
                self.data_received_from_ip.add(addr[0])
                connection = self.connections.get(addr[0])
                if connection is None:
                    print(f"Data from unknown client {addr}: {data}")
                    continue

                connection.on_data(data)
            except TimeoutError:
                pass

        self.socket.close()

connection_manager: ConnectionManager

class ScanResult(BaseModel):
    ip: str
    sn: str
    mac: Optional[str]

def start():
    global connection_manager
    connection_manager = ConnectionManager()

def stop():
    connection_manager.stop()

async def scan(myip: str, timeout: float = 5) -> list[ScanResult]:
    interface = ipaddress.IPv4Interface(myip)
    connection_manager.data_received_from_ip = set()

    old_timeout = connection_manager.socket.gettimeout()
    connection_manager.socket.settimeout(None)

    for addr in interface.network:
        if str(addr).split(".")[-1] in ("255", "0"):
            continue
        connection_manager.socket.sendto(b"command", (str(addr), ConnectionManager.REMOTE_CMD_PORT))

    connection_manager.socket.settimeout(old_timeout)

    loop = get_event_loop()
    future = loop.create_future()
    timer = threading.Timer(timeout, lambda : loop.call_soon_threadsafe(future.set_result, None))
    timer.start()
    await future

    ips = list(connection_manager.data_received_from_ip)
    connections = list()

    for ip in ips:
        try:
            conn = Connection(ip, connection_manager.socket, connection_manager.loop) # do not send second command
            connection_manager.connections[ip] = conn

            conn = await connection_manager.connect(ip)
            sn = await conn.send_raw_message("sn?")
            mac = find_mac(ip)
            connections.append(ScanResult(ip=conn.ip, sn=sn, mac=mac))
        except:
            print(f"drone {ip} responded to initial scan but now does not work")
    
    return connections

class CanvasWaypoints:
    def __init__(self):
        self.waypoints = [(0,0,0)]

    def addwaypoint(self, x: int, y: int, z: int) -> None:
        self.waypoints.append((x, y, z))

    def getwaypoints(self):
        return self.waypoints

class PathCalculation:
    def __init__(self) -> None:
        self.xpos = 0.0 # in m  - Aktuelle Position der Drohne relativ zum Start
        self.ypos = 0.0 # in m  ^
        self.zpos = 0.0 # in m  ^
        self.time_last_callback = None
        self.canvas_waypoints = CanvasWaypoints()

    async def incoming_callback(self, state: State):
        if self.time_last_callback is None:
            self.time_last_callback = time.time()
            return
        curr_time = time.time()
        last_callback = self.time_last_callback - curr_time
        self.time_last_callback = curr_time

        self.xpos += (state.vgx/10) / last_callback
        self.ypos += (state.vgy/10) / last_callback
        self.zpos += (state.vgz/10) / last_callback

        self.canvas_waypoints.addwaypoint(int(self.xpos), int(self.ypos), int(self.zpos))
