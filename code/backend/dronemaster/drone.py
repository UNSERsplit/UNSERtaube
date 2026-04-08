from typing import Any, Callable, Coroutine, Optional
#from websocket.webrtc import UDPVideoTrack
from . import connection, State

class Drone:
    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.connection: connection.Connection = None # type: ignore
        self.ext = Ext(self)
    
    def get_video_port(self) -> int:
        return self.connection.future_video_port
    
    def set_video_stream(self, track: Any):
        self.connection.setVideoTrack(track)
    
    async def connect(self):
        self.connection = await connection.connection_manager.connect(self.ip)
    
    async def disconnect(self):
        if self.connection:
            await self.connection.disconnect()

    async def takeoff(self):
        await self.connection.send_control_message(f"takeoff", timeout=30, repeat=0)
    
    async def land(self):
        await self.connection.send_control_message("land", timeout=10, repeat=0)
    
    def set_state_callback(self, cb: Callable[[State], Coroutine[Any, Any, None]]):
        self.connection.setupStateCallback(cb)

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

    async def matrix_set_startup_pattern(self, colorstr:str):
        if colorstr != "":
            colorstr = "0"
        resp = await self.drone.connection.send_raw_message(f"EXT mled sg {colorstr}")
        if resp != "mled ok":
            raise ConnectionError(f"EXT mled sg {colorstr} responded with {resp}")

    async def matrix_set_pattern(self, colorstr:str):
        if colorstr != "":
            colorstr = "0"
        resp = await self.drone.connection.send_raw_message(f"EXT mled g {colorstr}")
        if resp != "mled ok":
            raise ConnectionError(f"EXT mled g {colorstr} responded with {resp}")
