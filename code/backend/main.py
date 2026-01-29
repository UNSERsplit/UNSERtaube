from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from websocket_mgr import WebsocketManager
from routes.drone import drone_router
from routes.route import routes_router
from database import create_tables
from pydantic import ValidationError
import os
from websocket.ws_messages import IncommingMessage

import dronemaster

@asynccontextmanager
async def lifespan(app: FastAPI):
    dronemaster.start()
    yield
    dronemaster.stop()

app = FastAPI(lifespan=lifespan)
app.include_router(drone_router)
app.include_router(routes_router)

manager = WebsocketManager()

network_cidr = os.environ["EXTERNAL_IP"]
print(network_cidr)

@app.get("/")
def test() -> str:
    return "it works"

@app.websocket("/ws")
async def websocket(ws: WebSocket):
    await ws.accept()
    await manager.connnect(ws)
    
    while True:
        data = await ws.receive_text()
        try:
            message = IncommingMessage.validate_json(data)
        except ValidationError as e:
            await ws.send_text(e.json())
            continue
        
        await manager.on_message(ws, message)

        await ws.send_json(message.model_dump())


create_tables()

drone: dronemaster.Drone

@app.get("/connect/{ip}")
async def a(ip: str):
    global drone
    drone = dronemaster.Drone(ip)
    await drone.connect()
    await drone.takeoff()

@app.get("/takeoff")
async def b():
    await drone.takeoff()

@app.get("/land")
async def c():
    await drone.land()

@app.get("/scan")
async def scan() -> list[dronemaster.ScanResult]:
    return await dronemaster.scan(os.environ["EXTERNAL_IP"])