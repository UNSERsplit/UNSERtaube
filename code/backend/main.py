import asyncio
from contextlib import asynccontextmanager
import time

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

import dronemaster
from async_thread import AsyncThread

import routes.live as live

@asynccontextmanager
async def lifespan(app: FastAPI):
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
app.include_router(live.live_router)

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