import asyncio
import re
from asyncio import Future, InvalidStateError
from typing import List, Optional, Any

OK = [r"^ok$"]
ERROR = [r"^error$"]
ANY = [r"^.*?$"]

class ProtocolError(BaseException):
    def __init__(self, response: str):
        self.response = response

    def __str__(self):
        return f"ProtocolError({self.response})"

class Action:
    def __init__(self, command: str, positive_answers: List[str], negative_answers: List[str]):
        self.command = command
        self.positive_answers = positive_answers
        self.negative_answers = negative_answers

        self.future = asyncio.get_running_loop().create_future()

    async def send(self, transport: asyncio.DatagramTransport, target: str) -> Any:
        pass

    def on_receive(self, data: bytes, addr):
        pass

    def on_cancel(self):
        self.future.cancel()

class RetryAction(Action):
    """intended for commands that may be sent multiple times (eg. reads, ...)"""
    def __init__(self, command: str, positive_answers: List[str], negative_answers: List[str], timeout: float, retry_count: int):
        super().__init__(command, positive_answers, negative_answers)
        self.timeout = timeout
        self.retry_count = retry_count

    async def send(self, transport: asyncio.DatagramTransport, target: str):
        self.future = asyncio.get_running_loop().create_future()
        count = 1

        while count < self.retry_count:
            print("\t\t\t", self.command.encode())
            transport.sendto(self.command.encode(), (target, 8889))

            try:
                response = await asyncio.wait_for(asyncio.shield(self.future), timeout=self.timeout)
                return response
            except asyncio.TimeoutError:
                count += 1

        raise TimeoutError("tried to send the command too often")

    def on_receive(self, data: bytes, addr):
        if data.startswith(b"Re"):
            return
        for pattern in self.positive_answers:
            if re.match(pattern, data.decode()):
                self.future.set_result(data.decode())
                return

        for pattern in self.negative_answers:
            if re.match(pattern, data.decode()):
                self.future.set_exception(ProtocolError(data.decode()))
                return

        print("???", data)


class RepeatAction(Action):
    """intended for commands that may not be sent multiple times (eg. takeoff, land)"""
    counter = hash(Action)
    last_answer_id = None

    def __init__(self, command: str, positive_answers: List[str], negative_answers: List[str], timeout: float):
        super().__init__(command, positive_answers, negative_answers)
        self.timeout = timeout

    async def send(self, transport: asyncio.DatagramTransport, target: str):
        for i in range(1, 6):
            print("\t\t\t", f"Re{RepeatAction.counter % 100:02d}{i:02d} {self.command}".encode())
            transport.sendto(f"Re{RepeatAction.counter % 100:02d}{i:02d} {self.command}".encode(), (target, 8889))

        RepeatAction.counter += 1

        try:
            response = await asyncio.wait_for(asyncio.shield(self.future), timeout=self.timeout)
            return response
        except asyncio.TimeoutError:
            raise TimeoutError("did not respond within " + str(self.timeout)) from None



    def on_receive(self, data: bytes, addr):
        if not data.startswith(b"Re"):
            self.handle(data)
            return

        if RepeatAction.last_answer_id == data[2:4]:
            return
        RepeatAction.last_answer_id = data[2:4]

        self.handle(data[7:])

    def handle(self, data: bytes):
        for pattern in self.positive_answers:
            if re.match(pattern, data.decode()):
                self.future.set_result(data.decode())
                return

        for pattern in self.negative_answers:
            if re.match(pattern, data.decode()):
                self.future.set_exception(ProtocolError(data.decode()))
                return

        print("???", data)


class RobomasterProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport = None
        self.waiting_action: Optional[Action] = None

    async def on_state(self, state: dict):
        pass

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        self.transport = None

    def datagram_received(self, data, addr):
        #print(addr[0], data)
        if data.startswith(b"mid:"):
            self.state_received(data.strip(), addr)
        else:
            self.received(data.strip(), addr)

    def state_received(self, data, addr):
        INT_FIELDS = ("pitch", "roll", "yaw", "vgx", "vgy", "vgz", "bat", "templ", "temph", "tof", "h", "time")
        FLOAT_FIELDS = ("agx", "agy", "agz", "baro")

        state = {}
        for entry in data.decode().strip().split(";"):
            if not entry:
                continue
            name, value = entry.split(":")

            if name in INT_FIELDS:
                state[name] = int(value)
            elif name in FLOAT_FIELDS:
                state[name] = float(value)
            else:
                pass

        asyncio.get_running_loop().create_task(self.on_state(state))

    def received(self, data, addr):
        print(data)
        if self.waiting_action is None:
            if RepeatAction.last_answer_id == data[2:4]:
                return # was from previous action
            print("unexpected data", data, addr)
            return

        self.waiting_action.on_receive(data, addr)

    async def send_action(self, action: Action, target: str):
        if self.waiting_action is not None:
            self.waiting_action.on_cancel()
        self.waiting_action = action
        try:
            return await action.send(self.transport, target)
        finally:
            self.waiting_action = None

    def send_command_noanswer(self, command: str, target: str):
        print("\t\t\t", command.encode())
        self.transport.sendto(command.encode(), (target, 8889))



transport: asyncio.DatagramTransport
protocol: RobomasterProtocol

async def start():
    global transport, protocol
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(RobomasterProtocol, local_addr=("0.0.0.0", 8890), reuse_port=True)
    return protocol

async def stop():
    transport.close()