import inspect

from .low_level import ProtocolError, RepeatAction, RetryAction, RobomasterProtocol, Action, OK, ANY
from . import low_level as l
from time import time
from typing import Dict, List, Any, Tuple, Sequence


def limit(v: float, min: float, max: float):
    if v > max or v < min:
        raise ValueError(f"{v} must be in range of [{min},{max}]")

class CommandRecorder:
    allowed_commands = []

    def __init__(self):
        self.enabled = False
        self.last_command_time = None

    def _command(self, command: str, args: Sequence[Any], kwargs: Dict[str, Any]):
        if not self.enabled:
            return

        now = time()

        if self.last_command_time is not None:
            delay = now - self.last_command_time
        else:
            delay = 0
        self.last_command_time = now

        self.command(delay, command, args, kwargs)
    
    def command(self, delay: float, command: str, args: Sequence[Any], kwargs: Dict[str, Any]):
        pass

    def stop_and_return(self) -> Any:
        pass

class record:
    def __init__(self):
        pass

    def __call__(self, func):
        CommandRecorder.allowed_commands.append(func.__name__)

        def f(self2: Module, *args, **kwargs):
            self2.drone.command_recorder._command(func.__name__, args, kwargs)
            return func(self2, *args)
    
        f.__name__ = func.__name__
        f.__signature__ = inspect.signature(func) # type: ignore

        return f

class Drone:
    def __init__(self, ip: str):
        self.ip = ip
        self.flight = Flight(self)
        self.rgb = RGBLed(self)
        self.matrix = Matrix(self)
        self.last_state: Dict[str, Any] = {}
        self.command_recorder: CommandRecorder = CommandRecorder()

    def record_commands(self, recorder: CommandRecorder):
        self.command_recorder = recorder
        self.command_recorder.enabled = True

    def stop_recording_commands(self):
        self.command_recorder.enabled = False
        return self.command_recorder.stop_and_return()

    async def action(self, action: Action):
        return await l.protocol.send_action(action, self.ip)

    async def _on_state(self, state: dict):
        if "last_update" in self.last_state:
            delta = time() - self.last_state["last_update"]
        else:
            delta = 0
        state.update({"last_update": time(), "delta": delta, "connected": True})
        self.last_state = state
        await self.on_state(state)

    async def on_state(self, state: dict):
        pass

    async def initialize(self):
        await self.action(RetryAction(
            command="command",
            positive_answers=OK,
            negative_answers=ANY,
            retry_count=5,
            timeout=0.5
        ))

        l.protocol.on_state = self._on_state

    async def serial_number(self):
        return await self.action(RetryAction(
            command="sn?",
            positive_answers=[r"^[A-Z0-9]{14}$"],
            negative_answers=ANY,
            retry_count=5,
            timeout=1
        ))

    async def battery(self):
        return await self.action(RetryAction(
            command="battery?",
            positive_answers=[r"^\d{1,3}$"],
            negative_answers=ANY,
            retry_count=5,
            timeout=1
        ))

    async def streamon(self):
        await self.action(RetryAction(
            command="streamon",
            positive_answers=OK,
            negative_answers=ANY,
            retry_count=5,
            timeout=1
        ))

    async def streamoff(self):
        await self.action(RetryAction(
            command="streamoff",
            positive_answers=OK,
            negative_answers=ANY,
            retry_count=5,
            timeout=1
        ))
    
    async def downvision(self, on: bool):
        await self.action(RetryAction(
            command=f"downvision {1 if on else 0}",
            positive_answers=OK,
            negative_answers=ANY,
            retry_count=5,
            timeout=1
        ))

    async def ext_tof(self):
        raw = await self.action(RetryAction(
            command="EXT tof?",
            positive_answers=[r"^tof \d+$"],
            negative_answers=ANY,
            retry_count=5,
            timeout=1
        ))
        tof = int(raw.split(" ")[1])

        if tof == 8190:
            return None
        else:
            return tof

    async def tof(self):
        raw = await self.action(RetryAction(
            command="tof?",
            positive_answers=[r"^\d+mm$"],
            negative_answers=ANY,
            retry_count=5,
            timeout=1
        ))
        tof = int(raw[:-2])

        if tof == 100:
            return None
        else:
            return tof

    async def keepalive(self):
        if l.protocol.waiting_action is None:
            await self.action(RetryAction(
                command="command",
                positive_answers=OK,
                negative_answers=ANY,
                retry_count=5,
                timeout=0.5
            ))

    async def debug_command(self, command, wait_for_answer: bool = True):
        if wait_for_answer:
            return await self.action(RetryAction(
                command=command,
                positive_answers=ANY,
                negative_answers=ANY,
                retry_count=5,
                timeout=1
            ))
        else:
            l.protocol.send_command_noanswer(command, self.ip)
            return "[Command sent]"

    def reboot(self):
        l.protocol.send_command_noanswer("reboot", self.ip)

class Module:
    def __init__(self, drone: Drone):
        self.drone = drone

    async def action(self, action: Action):
        return await self.drone.action(action)

class Flight(Module):
    @record()
    async def takeoff(self):
        await self.action(RepeatAction(
            command="takeoff",
            positive_answers=OK,
            negative_answers=ANY,
            timeout=20
        ))

    async def forward(self, dist: int, timeout: float = 5):
        """dist forward in cm [20-500]"""
        limit(dist, 20, 500)
        await self.action(RepeatAction(
            command=f"forward {dist}",
            positive_answers=OK,
            negative_answers=ANY,
            timeout=timeout
        ))

    async def back(self, dist: int, timeout: float = 5):
        """dist backwards in cm [20-500]"""
        limit(dist, 20, 500)
        await self.action(RepeatAction(
            command=f"back {dist}",
            positive_answers=OK,
            negative_answers=ANY,
            timeout=timeout
        ))

    async def up(self, dist: int, timeout: float = 5):
        """dist upwards in cm [20-500]"""
        limit(dist, 20, 500)
        await self.action(RepeatAction(
            command=f"up {dist}",
            positive_answers=OK,
            negative_answers=ANY,
            timeout=timeout
        ))

    async def down(self, dist: int, timeout: float = 5):
        """dist downwards in cm [20-500]"""
        limit(dist, 20, 500)
        await self.action(RepeatAction(
            command=f"down {dist}",
            positive_answers=OK,
            negative_answers=ANY,
            timeout=timeout
        ))

    async def left(self, dist: int, timeout: float = 5):
        """dist left in cm [20-500]"""
        limit(dist, 20, 500)
        await self.action(RepeatAction(
            command=f"left {dist}",
            positive_answers=OK,
            negative_answers=ANY,
            timeout=timeout
        ))

    async def right(self, dist: int, timeout: float = 5):
        """dist right in cm [20-500]"""
        limit(dist, 20, 500)
        await self.action(RepeatAction(
            command=f"right {dist}",
            positive_answers=OK,
            negative_answers=ANY,
            timeout=timeout
        ))

    async def clockwise(self, angle: int, timeout: float = 5):
        """rotate angle degrees clockwise [1-360]"""
        limit(angle, 1, 360)
        await self.action(RepeatAction(
            command=f"cw {angle}",
            positive_answers=OK,
            negative_answers=ANY,
            timeout=timeout
        ))

    async def counterclockwise(self, angle: int, timeout: float = 5):
        """rotate angle degrees counterclockwise [1-360]"""
        limit(angle, 1, 360)
        await self.action(RepeatAction(
            command=f"ccw {angle}",
            positive_answers=OK,
            negative_answers=ANY,
            timeout=timeout
        ))

    @record()
    async def land(self):
        await self.action(RepeatAction(
            command="land",
            positive_answers=OK,
            negative_answers=ANY,
            timeout=20
        ))

    @record()
    async def stop(self):
        await self.action(RepeatAction(
            command="stop",
            positive_answers= [r"^forced stop$", r"^ok$"],
            negative_answers=ANY,
            timeout=5
        ))

    @record()
    async def emergency(self):
        await self.action(RetryAction(
            command="emergency",
            positive_answers=OK,
            negative_answers=ANY,
            retry_count=5,
            timeout=1
        ))

    async def motoron(self):
        await self.action(RetryAction(
            command="motoron",
            positive_answers=OK,
            negative_answers=ANY,
            retry_count=5,
            timeout=1
        ))

    async def motoroff(self):
        await self.action(RetryAction(
            command="motoroff",
            positive_answers=OK,
            negative_answers=ANY,
            retry_count=5,
            timeout=1
        ))

    @record()
    async def flip(self, direction: str, timeout: float = 5):
        """flip in direction l r f b"""
        if direction not in ("l", "r", "f", "b"):
            raise ValueError("Direction must be in l,r,f,b")

        await self.action(RepeatAction(
            command=f"flip {direction}",
            positive_answers=OK,
            negative_answers=ANY,
            timeout=timeout
        ))

    @record()
    def rc(self, roll: int, pitch: int, throttle: int, yaw: int):
        limit(roll, -100, 100)
        limit(pitch, -100, 100)
        limit(throttle, -100, 100)
        limit(yaw, -100, 100)

        l.protocol.send_command_noanswer(f"rc {roll} {pitch} {throttle} {yaw}", self.drone.ip)

class RGBLed(Module):
    async def set(self, color: Tuple[int, int, int]):
        red, green, blue = color
        limit(red, 0, 255)
        limit(green, 0, 255)
        limit(blue, 0, 255)
        await self.action(RetryAction(
            command=f"EXT led {red} {green} {blue}",
            positive_answers=[r"^led ok$"],
            negative_answers=ANY,
            timeout=0.5,
            retry_count=5
        ))

    async def pulse(self, color: Tuple[int, int, int], frequency: float):
        red, green, blue = color
        limit(red, 0, 255)
        limit(green, 0, 255)
        limit(blue, 0, 255)
        limit(frequency, 0.1, 2.5)
        await self.action(RetryAction(
            command=f"EXT led br {frequency} {red} {green} {blue}",
            positive_answers=[r"^led ok$"],
            negative_answers=ANY,
            timeout=0.5,
            retry_count=5
        ))

    async def flash(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], frequency: float):
        red1, green1, blue1 = color1
        red2, green2, blue2 = color2
        limit(red1, 0, 255)
        limit(green1, 0, 255)
        limit(blue1, 0, 255)
        limit(red2, 0, 255)
        limit(green2, 0, 255)
        limit(blue2, 0, 255)
        limit(frequency, 0.1, 10)
        await self.action(RetryAction(
            command=f"EXT led bl {frequency} {red1} {green1} {blue1} {red2} {green2} {blue2}",
            positive_answers=[r"^led ok$"],
            negative_answers=ANY,
            timeout=0.5,
            retry_count=5
        ))

class Matrix(Module):
    def __init__(self, drone: Drone):
        super().__init__(drone)
        self.pattern = "ppppp000"\
                       "00p00000"\
                       "00pbbbbb"\
                       "00p00b00"\
                       "00p00b00"\
                       "00000b00"\
                       "00000b00"\
                       "rrrrpppp"

    async def set_brightness(self, brightness: int):
        limit(brightness, 0, 255)
        await self.action(RetryAction(
            command=f"EXT mled sl {brightness}",
            positive_answers=[r"^mled ok$"],
            negative_answers=ANY,
            timeout=0.5,
            retry_count=5
        ))

    async def set_pattern(self, pattern: str):
        limit(len(pattern.replace("r","").replace("b","").replace("p","").replace("0","")), 0, 0)
        limit(len(pattern), 1, 64)

        await self.action(RetryAction(
            command=f"EXT mled g {pattern}",
            positive_answers=[r"^matrix ok$"],
            negative_answers=ANY,
            timeout=0.5,
            retry_count=5
        ))

        self.pattern = pattern