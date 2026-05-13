from typing import Any, Dict, List, Tuple

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
import asyncio

import dronemaster

drone: dronemaster.Drone = None # type: ignore

live_router = APIRouter(prefix="/live")

@live_router.post("/connect")
async def connect(request: Request, ip: str = "10.242.206.235"):
    global drone
    drone = dronemaster.Drone(ip)
    await drone.initialize()
    await drone.streamon()
    drone.on_state = on_state
    return "OK"

@live_router.post("/command")
async def command(command: str, wait: bool):
    global drone
    return await drone.debug_command(command, wait_for_answer=wait)

@live_router.post("/start_command_recoding")
async def start_command_recoding():
    global drone
    drone.record_commands()
    return "OK"

@live_router.post("/stop_command_recoding")
async def stop_command_recoding():
    global drone
    return drone.stop_recording_commands()


@live_router.post("/replay")
async def replay_commands(data: List[Tuple[float, str, List[Any], Dict[str, Any]]]):
    global drone
    for entry in data:
        delay, cmd, args, kwargs = entry
        print(delay, cmd, args, kwargs)
        await asyncio.sleep(delay)
        func = drone.flight.__getattribute__(cmd)
        ret = func(*args, **kwargs)
        if ret is not None:
            await ret

flight_router = APIRouter(prefix="/flight")

@flight_router.post("/takeoff")
async def takeoff():
    global drone
    await drone.flight.takeoff()
    return "OK"

@flight_router.post("/stop")
async def stop():
    global drone
    await drone.flight.stop()
    return "OK"

@flight_router.post("/land")
async def land():
    global drone
    await drone.flight.land()
    return "OK"

@flight_router.post("/forward")
async def forward(dist: int):
    global drone
    await drone.flight.forward(dist, timeout=dist/4)
    return "OK"

@flight_router.post("/backwards")
async def backwards(dist: int):
    global drone
    await drone.flight.back(dist, timeout=dist/4)
    return "OK"

@flight_router.post("/left")
async def left(dist: int):
    global drone
    await drone.flight.left(dist, timeout=dist/4)
    return "OK"

@flight_router.post("/right")
async def right(dist: int):
    global drone
    await drone.flight.right(dist, timeout=dist/4)
    return "OK"

@flight_router.post("/up")
async def up(dist: int):
    global drone
    await drone.flight.up(dist, timeout=dist/4)
    return "OK"

@flight_router.post("/down")
async def down(dist: int):
    global drone
    await drone.flight.down(dist, timeout=dist/4)
    return "OK"

@flight_router.post("/clockwise")
async def clockwise(dist: int):
    global drone
    await drone.flight.clockwise(dist, timeout=dist/4)
    return "OK"

@flight_router.post("/counterclockwise")
async def counterclockwise(dist: int):
    global drone
    await drone.flight.counterclockwise(dist, timeout=dist/4)
    return "OK"


led_router = APIRouter(prefix="/rgb")

@led_router.post("/set")
async def set_rgb(rgb: Tuple[int, int, int]):
    global drone
    await drone.rgb.set(rgb)
    return "OK"

@led_router.post("/pulse")
async def pulse_rgb(rgb: Tuple[int, int, int], frequency: float):
    global drone
    await drone.rgb.pulse(rgb, frequency)
    return "OK"

@led_router.post("/flash")
async def flash_rgb(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int], frequency: float):
    global drone
    await drone.rgb.flash(rgb1, rgb2, frequency)
    return "OK"


matrix_router = APIRouter(prefix="/matrix")

@matrix_router.post("/brightness")
async def matrix_brightness(brightness: int):
    global drone
    await drone.matrix.set_brightness(brightness)
    return "OK"

@matrix_router.post("/pattern")
async def matrix_pattern(pattern: str):
    global drone
    await drone.matrix.set_pattern(pattern)
    return "OK"

live_router.include_router(flight_router)
live_router.include_router(led_router)
live_router.include_router(matrix_router)


websockets: List[WebSocket] = []

@live_router.websocket("/ws")
async def status(ws: WebSocket):
    await ws.accept()
    websockets.append(ws)

    try:
        while True:
            data = await ws.receive_json()

            if data["type"] == "rc":
                if drone:
                    drone.flight.rc(int(data["roll"]), int(data["pitch"]), int(data["throttle"]), int(data["yaw"]))
            else:
                print(data)
    except WebSocketDisconnect:
        print("Disconnect")

async def on_state(state: dict):
    remove = []
    for ws in websockets:
        try:
            await ws.send_json(state)
        except Exception as e:
            print(e)
            remove.append(ws)

    for ws in remove:
        websockets.remove(ws)