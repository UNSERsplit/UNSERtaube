from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from websocket_mgr import WebsocketManager
from routes.drone import drone_router
from routes.route import routes_router
from database import create_tables
from pydantic import ValidationError
from websocket.ws_messages import IncommingMessage
from websocket.openapi_messages import MsgServerDef, MsgClientDef

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

@app.websocket("/ws")
async def websocket(ws: WebSocket):
    await ws.accept()
    await manager.connnect(ws)
    
    try:
        while True:
            data = await ws.receive_text()
            try:
                message = IncommingMessage.validate_json(data)
            except ValidationError as e:
                await ws.send_json({"type":"error", "context": e.errors()})
                continue
            
            await manager.on_message(ws, message)
    except WebSocketDisconnect as e:
        pass

def append_ws_schemas():
  from fastapi.openapi.utils import get_openapi
  from fastapi.openapi.constants import REF_TEMPLATE

  if app.openapi_schema:
    return app.openapi_schema
  
  openapi_schema = get_openapi(
    title=app.title,
    version=app.version,
    summary=app.summary,
    description=app.description,
    routes=app.routes,
    servers=app.servers
  )
  
  extras = {
      "serverbound": {**MsgClientDef.model_json_schema(ref_template=REF_TEMPLATE, by_alias=False), "description": "All serverbound websocket messages, look under $defs"},
      "clientbound": {**MsgServerDef.model_json_schema(ref_template=REF_TEMPLATE, by_alias=False), "description": "All clientbound websocket messages, look under $defs"}
  }

  openapi_schema["components"]["schemas"].update(extras)
  app.openapi_schema = openapi_schema

  return app.openapi_schema

app.openapi = append_ws_schemas

create_tables()