from . import connection

class Drone:
    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.connection: connection.Connection
    
    async def connect(self):
        self.connection = await connection.connection_manager.connect(self.ip)

    async def takeoff(self):
        await self.connection.send_control_message("takeoff")
    
    async def land(self):
        await self.connection.send_control_message("land")
    
    async def emergency_stop(self):
        await self.connection.send_control_message("emergency")
    
    def rc(self, roll: float, pitch: float, throttle: float, yaw: float):
        """all args from -100 to 100"""
        message = f"rc {roll} {pitch} {throttle} {yaw}"
        self.connection.send_message_noanswer(message)