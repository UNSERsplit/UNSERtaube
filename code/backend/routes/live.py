from typing import Any, Dict, List, Tuple

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select
import uuid

import dronemaster
from database import DB
from models.drone import Drone
from schemas.drone import Drone as DroneDTO
from state_computation import StateComputation
from ai.ai import AI_Module

drone: dronemaster.Drone = None # type: ignore
db_drone: Drone = None # type: ignore
state_computation: StateComputation = None # type: ignore
ai_module: AI_Module = None # type: ignore

live_router = APIRouter(prefix="/live")

@live_router.get("/connected")
async def get_drone() -> DroneDTO:
    return db_drone # type: ignore

@live_router.post("/disconnect")
async def disconnect() -> str:
    global drone, state_computation, db_drone, ai_module
    drone.reboot()
    ai_module.on_disconnect()
    ai_module = None # type: ignore
    state_computation = None # type: ignore
    drone.stop_recording_commands()
    drone = None # type: ignore
    db_drone = None # type: ignore
    return "OK"

@live_router.post("/connect", responses={404: {"model": str}})
async def connect(db: DB, drone_id: uuid.UUID) -> str:
    global drone, state_computation, db_drone, ai_module

    obj = db.scalar(select(Drone).where(Drone.id == drone_id))

    if not obj:
        raise HTTPException(status_code=404, detail="Drone not found")
    
    db_drone = obj

    drone = dronemaster.Drone(obj.ip) # type: ignore
    try:
        await drone.initialize()
    except dronemaster.ProtocolError:
        drone = None # type: ignore
        raise
    except TimeoutError:
        drone = None # type: ignore
        raise
    await drone.rgb.set((0,255,0))
    await drone.streamon()
    drone.on_state = on_state
    state_computation = StateComputation()
    ai_module = AI_Module()
    return "OK"

@live_router.post("/command")
async def command(command: str, wait: bool):
    global drone
    return await drone.debug_command(command, wait_for_answer=wait)

@live_router.post("/people_detection")
async def people_detection(on: bool):
    global ai_module
    ai_module.set_people_detection(on)
    return "OK"

@live_router.post("/ring_detection")
async def ring_detection(on: bool):
    global ai_module
    ai_module.set_ring_detection(on)
    return "OK"

@live_router.post("/downvision")
async def downvision(on: bool):
    global drone
    await drone.downvision(on)
    return "OK"

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

@matrix_router.get("/pattern")
async def matrix_get_pattern():
    global drone
    return drone.matrix.pattern

live_router.include_router(flight_router)
live_router.include_router(led_router)
live_router.include_router(matrix_router)


websockets: List[WebSocket] = []

@live_router.websocket("/ws")
async def status(ws: WebSocket):
    await ws.accept()
    websockets.append(ws)

    try:
        await ws.send_bytes(b"f") # ?????
        if drone is None:
            await ws.send_json({"connected":False})

        while True:
            data = await ws.receive_json()

            if data["type"] == "rc":
                if drone:
                    drone.flight.rc(int(data["roll"]), int(data["pitch"]), int(data["throttle"]), int(data["yaw"]))
            else:
                print(data)
    except WebSocketDisconnect:
        pass

async def on_state(state: dict, compute: bool=True):
    remove = []

    if drone is None:
        compute = False
        state = {"connected":False}

    if compute:
        state = state_computation.on_state(state) # type: ignore
        state["detections"] = ai_module.get_detections()

    for ws in websockets:
        try:
            await ws.send_json(state)
        except Exception as e:
            #print(e)
            remove.append(ws)

    for ws in remove:
        websockets.remove(ws)