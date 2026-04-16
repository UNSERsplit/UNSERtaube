from typing import Any, Callable, Coroutine, Optional
#from websocket.webrtc import UDPVideoTrack
from . import connection, State
from threading import Timer

class Drone:
    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.connection: connection.Connection = None # type: ignore
        self.ext = Ext(self)
        self.state_callback: Callable[[State], Coroutine[Any, Any, None]] = None  # type: ignore
        self.disconnect_callback: Callable[[], Coroutine[Any, Any, None]] = None  # type: ignore
        self.timer = None
    
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
        self.connection.send_message_noanswer("takeoff")
    
    async def land(self):
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
        self.connection.send_message_noanswer("emergency")

    async def startstream(self):
        await self.connection.setupVideoStream()
        await self.connection.send_control_message("streamon")

    async def stopstream(self):
        await self.connection.send_control_message("streamoff")
    
    def rc(self, roll: float, pitch: float, throttle: float, yaw: float):
        """all args from -100 to 100"""
        message = f"rc {roll} {pitch} {throttle} {yaw}"
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