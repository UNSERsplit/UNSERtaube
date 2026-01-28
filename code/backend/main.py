from fastapi import FastAPI, WebSocket
from drone_scan import scan
from websocket_mgr import WebsocketManager
from route.drone import router as drone_router
import os

app = FastAPI()
app.include_router(drone_router)

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