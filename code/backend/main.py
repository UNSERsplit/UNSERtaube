import asyncio
from contextlib import asynccontextmanager
import time

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

import dronemaster
from async_thread import AsyncThread

import routes.live as live
import routes.recording as recording
import routes.drone as drone
from database import create_tables, DB

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    await dronemaster.start()
    background_task = AsyncThread(target=keepalive)
    background_task.start()
    yield
    background_task.close()
    await dronemaster.stop()

async def keepalive():
    while True:
        if live.drone:
            try:
                await live.drone.keepalive()
            except TimeoutError:
                print("Drone died")
                live.drone = None
        await asyncio.sleep(10)

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def ensure_drone(request: Request, call_next):
    if request.method == "POST" and request.url.path != "/live/connect" and request.url.path.startswith("/live"):
        if live.drone is None:
            return PlainTextResponse(status_code=404, content="Drone not connected")

    start_time = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as e:
        response = PlainTextResponse(status_code=500, content=str(e))
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.include_router(live.live_router)
app.include_router(recording.recording_router)
app.include_router(drone.drone_router)
