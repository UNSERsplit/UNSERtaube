from typing import Any, Dict, Iterator, Sequence, Tuple

import struct

from dronemaster.Drone import CommandRecorder

class BinaryRecorder(CommandRecorder):
    dirs = ("f","b","l","r")

    def __init__(self):
        super().__init__()

        self.bytes = bytearray()
    
    @staticmethod
    def _encode(id: int, delay: float, a1: int, a2: int, a3: int, a4: int) -> bytes:
        return struct.pack('<Bdbbbb', id, delay, a1, a2, a3, a4)
    
    @staticmethod
    def _depack(bytes: bytes) -> Tuple[int, float, int, int, int, int]:
        id, delay, a1, a2, a3, a4 = struct.unpack('<Bdbbbb', bytes)
        return id, delay, a1, a2, a3, a4
    
    @staticmethod
    def _iter_decode(bytes: bytes) -> Iterator[Tuple[int, float, int, int, int, int]]:
        iter = struct.iter_unpack('<Bdbbbb', bytes)

        for id, delay, a1, a2, a3, a4 in iter:
            yield id, delay, a1, a2, a3, a4

    def command(self, delay: float, command: str, args: Sequence[Any], kwargs: Dict[str, Any]):
        assert len(kwargs) == 0

        id, a1, a2, a3, a4 = 0,0,0,0,0


        match command:
            case "takeoff":
                id = 1
            case "land":
                id = 2
            case "emergency":
                id = 3
            case "stop":
                id = 4
            case "rc":
                id = 5
                a1, a2, a3, a4 = args
            case "flip":
                id = 6
                a1 = self.dirs.index(args[0]) + 1

        bytes = self._encode(
            id=id,
            delay=delay,
            a1=a1,
            a2=a2,
            a3=a3,
            a4=a4
        )

        d_delay, d_cmd, d_args = self._decode(*self._depack(bytes))
        assert abs(d_delay - delay) < 0.000001
        assert d_cmd == command
        assert d_args == args

        self.bytes += bytearray(bytes)

        return super().command(delay, command, args, kwargs)
    
    @staticmethod
    def _decode(id, delay, a1, a2, a3, a4):
        cmd = ""
        args = ()

        match id:
            case 1:
                cmd = "takeoff"
            case 2:
                cmd = "land"
            case 3:
                cmd = "emergency"
            case 4:
                cmd = "stop"
            case 5:
                cmd = "rc"
                args = (a1, a2, a3, a4)
            case 6:
                cmd = "flip"
                args = (BinaryRecorder.dirs[a1 - 1])
        
        return delay, cmd, args
    
    @staticmethod
    def decode_commands(input_bytes: bytes):
        for id, delay, a1, a2, a3, a4 in BinaryRecorder._iter_decode(input_bytes):
            yield BinaryRecorder._decode(id, delay, a1, a2, a3, a4)
    
    def stop_and_return(self) -> Any:
        return self.bytes