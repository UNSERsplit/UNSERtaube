import asyncio
from typing import Any, Callable, Coroutine, Optional
#from websocket.webrtc import UDPVideoTrack
from . import connection, State
from threading import Timer, Thread
import time

class Drone:
    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.connection: connection.Connection = None # type: ignore
        self.ext = Ext(self)
        self.state_callback: Callable[[State], Coroutine[Any, Any, None]] = None  # type: ignore
        self.disconnect_callback: Callable[[], Coroutine[Any, Any, None]] = None  # type: ignore
        self.timer = None
        self.recording = False
        self.recording_start = 0
        self.recording_data = []
        self.emergency = False

        self.replay_thread = None
    
    def replay_route(self, data):
        self.replay_thread = Thread(target=self._replay_route, args=(data,))
        self.replay_thread.start()
    
    def _replay_route(self, data):
        i = 0
        while not self.emergency and i < len(data): #TODO nach emergency mag er nimma
            d = data[i]
            i += 1

            ts, cmd = d
            time.sleep(ts)
            if self.emergency:
                return
            if isinstance(cmd, str):
                self.connection.send_message_noanswer(cmd)
            else:
                roll, pitch, throttle, yaw = cmd
                message = f"rc {roll} {pitch} {throttle} {yaw}"
                self.connection.send_message_noanswer(message)
        self.emergency = False

    def start_recording(self):
        self.recording = True
        self.recording_start = time.time_ns()
    
    def stop_recording(self):
        self.recording = False

        return self.recording_start, self.recording_data
    
    def get_video_port(self) -> int:
        return self.connection.future_video_port
    
    def set_video_stream(self, track: Any):
        self.connection.setVideoTrack(track)
    
    async def connect(self):
        self.connection = await connection.connection_manager.connect(self.ip)
        self.connection.setupStateCallback(self._state_callback)

    
    async def disconnect(self):
        if self.connection:
            await self.connection.disconnect()

    async def takeoff(self):
        if self.recording:
            self.recording_data.append((time.time_ns(), "takeoff"))
        self.connection.send_message_noanswer("takeoff")
    
    async def land(self):
        if self.recording:
            self.recording_data.append((time.time_ns(), "land"))
        self.connection.send_message_noanswer("land")
    
    async def _disconnect_(self):
        if self.disconnect_callback:
            await self.disconnect_callback()

    async def _state_callback(self, state: State):
        if self.timer:
            self.timer.cancel()
        self.timer = Timer(5, lambda : self.connection.loop.call_soon_threadsafe(self.connection._run_task, self._disconnect_))
        self.timer.start()

        if self.state_callback:
            await self.state_callback(state)

    def set_disconnect_callback(self, cb: Callable[[], Coroutine[Any, Any, None]]):
        self.disconnect_callback = cb
    
    def set_state_callback(self, cb: Callable[[State], Coroutine[Any, Any, None]]):
        self.state_callback = cb

    async def emergency_stop(self):
        self.emergency = True
        self.connection.send_message_noanswer("rc 0 0 0 0")
        self.connection.send_message_noanswer("emergency")

    async def startstream(self):
        await self.connection.setupVideoStream()
        await self.connection.send_control_message("streamon")

    async def stopstream(self):
        await self.connection.send_control_message("streamoff")
    
    def rc(self, roll: float, pitch: float, throttle: float, yaw: float):
        """all args from -100 to 100"""
        message = f"rc {roll} {pitch} {throttle} {yaw}"
        if self.recording:
            self.recording_data.append((time.time_ns(), (roll, pitch, throttle, yaw)))
        self.connection.send_message_noanswer(message)

class Ext:
    def __init__(self, drone: Drone) -> None:
        self.drone = drone

    async def get_tof(self) -> Optional[int]:
        resp = await self.drone.connection.send_raw_message("EXT tof?")
        tof, value = resp.split(" ")
        if tof != "tof":
            raise ConnectionError("EXT tof? responded with " + resp)
        value = int(value)
        if value == 8192:
            return None
        return value
    
    async def led_set(self, red: int, green: int, blue: int):
        resp = await self.drone.connection.send_raw_message(f"EXT led {red} {green} {blue}")
        if resp != "led ok":
            raise ConnectionError(f"EXT led {red} {green} {blue}" + " responded with " + resp)
    
    async def led_pulse(self, red: int, green: int, blue: int, freq: float):
        if not (0.1 <= freq <= 2.5):
            raise ValueError("frequency must be between 0.1 and 2.5Hz")
        resp = await self.drone.connection.send_raw_message(f"EXT led br {freq} {red} {green} {blue}")
        if resp != "led ok":
            raise ConnectionError(f"EXT led br {freq} {red} {green} {blue}" + " responded with " + resp)
    
    async def led_flash(self, red1: int, green1: int, blue1: int, freq: float, red2: int, green2: int, blue2: int):
        if not (0.1 <= freq <= 10):
            raise ValueError("frequency must be between 0.1 and 10Hz")
        resp = await self.drone.connection.send_raw_message(f"EXT led bl {freq} {red1} {green1} {blue1} {red2} {green2} {blue2}")
        if resp != "led ok":
            raise ConnectionError(f"EXT led bl {freq} {red1} {green1} {blue1} {red2} {green2} {blue2}" + " responded with " + resp)

    async def matrix_set_startup_pattern(self, colorstr:str):
        if colorstr == "":
            colorstr = "0"
        resp = await self.drone.connection.send_raw_message(f"EXT mled sg {colorstr}")
        if resp != "mled ok":
            raise ConnectionError(f"EXT mled sg {colorstr} responded with {resp}")

    async def matrix_set_pattern(self, colorstr:str):
        if colorstr == "":
            colorstr = "0"
        resp = await self.drone.connection.send_raw_message(f"EXT mled g {colorstr}")
        if resp != "mled ok":
            raise ConnectionError(f"EXT mled g {colorstr} responded with {resp}")
