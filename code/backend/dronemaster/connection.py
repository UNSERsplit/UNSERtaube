import socket
import threading
from typing import Dict, Optional
from asyncio import Future, get_event_loop, AbstractEventLoop

class Connection:
    def __init__(self, target_ip: str, socket: socket.socket, loop: AbstractEventLoop) -> None:
        self.dest = (target_ip, ConnectionManager.REMOTE_CMD_PORT)
        self.loop: AbstractEventLoop = loop
        self.socket = socket
        self.read_event = threading.Event() # called when data is ready to be read
        self.read_event.set()
        self.async_future: Optional[Future[str]] = None
        self.read_data: Optional[str] = None # data to read
    
    async def connect(self): # called by ConnectionManager.connect
        await self.send_message("command")

    def on_data(self, raw_data: bytes): # called when new data for this ip is received
        data = raw_data.decode()

        if self._is_state_message(data):
            pass #TODO
        else:
            self.read_data = data
            self.read_event.set()
            if self.async_future is not None:
                self.loop.call_soon_threadsafe(self.async_future.set_result, data)
    
    def _is_state_message(self, data: str):
        return data.startswith("mid:")
    
    def send_message_noanswer(self, message: str):
        self.socket.sendto(message.encode(), self.dest)

    def send_message_sync(self, message: str, timeout: float = 5) -> str:
        if not self.read_event.wait(timeout): # the drone did not respond to the previous command
            raise TimeoutError(f"The drone did not respond to the prevoius command withing {timeout}s")

        self.read_event.clear()
        self.socket.sendto(message.encode(), self.dest)

        flag = self.read_event.wait(timeout) # wait until a response is available

        if not flag:
            raise TimeoutError(f"The drone did not respond withing {timeout}s")
        
        data = self.read_data
        self.read_data = None
        
        assert data is not None
        return data
    
    async def send_message(self, message: str, timeout: float = 5) -> str:
        self.loop = get_event_loop()
        if self.async_future is not None:
            await self.async_future
        
        timer = threading.Timer(timeout, lambda : self.loop.call_soon_threadsafe(self.async_future.set_exception, TimeoutError(f"The drone did not respond withing {timeout}s")) if self.async_future is not None else None)
        self.async_future = self.loop.create_future()
        timer.start()
        print(1)
        self.socket.sendto(message.encode(), self.dest)
        print(2)
        result = await self.async_future
        print(3 / 0)
        timer.cancel()
        return result


class ConnectionManager:
    LOCAL_IP = "0.0.0.0"

    LOCAL_STATE_PORT = 8890
    LOCAL_VIDEO_PORT = 11111
    REMOTE_CMD_PORT = 8889

    def __init__(self) -> None:
        self.event = threading.Event()
        self.loop = get_event_loop()

        self.connections: Dict[str, Connection] = {}

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((
            ConnectionManager.LOCAL_IP, 
            ConnectionManager.LOCAL_STATE_PORT
        ))

        self.thread = threading.Thread(target=self._run)
        self.thread.start()
    
    async def connect(self, target_ip: str) -> Connection:
        conn = Connection(target_ip, self.socket, self.loop)
        self.connections[target_ip] = conn
        await conn.connect()
        return conn
    
    def stop(self):
        self.event.set()
    
    def _run(self):
        while not self.event.is_set():
            data, addr = self.socket.recvfrom(1024)
            connection = self.connections.get(addr[1])
            if connection is None:
                print(f"Data from unknown client {addr}: {data}")
                continue

            connection.on_data(data)
        
        self.socket.close()