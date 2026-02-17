from . import connection

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
        self.connection.send_message_noanswer("land")
    
    async def emergency_stop(self):
        self.connection.send_message_noanswer("emergency")

    async def startstream(self):
        await self.connection.send_control_message("streamon")

    async def stopstream(self):
        await self.connection.send_control_message("streamoff")
    
    def rc(self, roll: float, pitch: float, throttle: float, yaw: float):
        """all args from -100 to 100"""
        message = f"rc {roll} {pitch} {throttle} {yaw}"
        self.connection.send_message_noanswer(message)