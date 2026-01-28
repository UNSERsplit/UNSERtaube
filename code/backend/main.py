from fastapi import FastAPI, WebSocket
from websocket_mgr import WebsocketManager
from routes.drone import drone_router
from routes.route import routes_router
from database import create_tables
import os

app = FastAPI()
app.include_router(drone_router)
app.include_router(routes_router)

manager = WebsocketManager()

network_cidr = os.environ["EXTERNAL_IP"]

@app.get("/")
def test() -> str:
    return "it works"

@app.websocket("/ws")
async def websocket(ws: WebSocket):
    await ws.accept()
    await manager.connnect(ws)
    
    tl_drone = None
    while True:
        data = await ws.receive_json()
        message_type = data["type"]

        if message_type == "select_drone":
            drone_ip = data["ip"]

            config.ROBOT_IP_STR = drone_ip

            tl_drone = robot.Drone()
            tl_drone.initialize()
        
        elif message_type == "scan_network":
            async def onNewClientFound(addr: tuple[str, int]):
                await ws.send_json({
                    "type": "new_drone",
                    "ip": addr[0]
                })
            async def onScanFinished():
                await ws.send_json({
                    "type": "scan_finished"
                })
            scan(network_cidr, onNewClientFound, onScanFinished)


        await ws.send_json({"received": data})

@app.get("/ping/{id}")#nur zum testn
def ping(id: int):
    return {"id": id}


create_tables()

from dronemaster.connection import ConnectionManager

mngr = ConnectionManager()

@app.get("/test")
async def a():
    connector = await mngr.connect("192.168.222.100")
    print(connector)