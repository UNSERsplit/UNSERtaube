from typing import Any, Callable, Coroutine
from . import connection, State

class Drone:
    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.connection: connection.Connection = None # type: ignore
    
    async def connect(self):
        self.connection = await connection.connection_manager.connect(self.ip)
    
    async def disconnect(self):
        if self.connection:
            await self.connection.disconnect()

    async def takeoff(self):
        await self.connection.send_control_message("takeoff", timeout=20)
    
    async def land(self):
        await self.connection.send_control_message("land")
    
    def set_state_callback(self, cb: Callable[[State], Coroutine[Any, Any, None]]):
        self.connection.setupStateCallback(cb)

    async def emergency_stop(self):
        self.connection.send_message_noanswer("emergency")

    async def startstream(self, cb: Callable[[bytes], Coroutine[Any, Any, None]]):
        await self.connection.setupVideoStream(cb)
        await self.connection.send_control_message("streamon")

    async def stopstream(self):
        await self.connection.send_control_message("streamoff")
    
    def rc(self, roll: float, pitch: float, throttle: float, yaw: float):
        """all args from -100 to 100"""
        message = f"rc {roll} {pitch} {throttle} {yaw}"
        self.connection.send_message_noanswer(message)