import asyncio
from typing import Optional
import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
import subprocess
import os
from time import time

from models.recording import Recording
from database import DB
from BinaryRecorder import BinaryRecorder

from . import live

def to_video_path(uuid: uuid.UUID) -> str:
    return os.path.join(f"videos/{uuid.hex}.mp4")

def to_flight_path(uuid: uuid.UUID) -> str:
    return os.path.join(f"paths/{uuid.hex}.path")

class Recorder:
    def __init__(self, uuid: uuid.UUID) -> None:
        self.uuid = uuid
        self.filename = to_video_path(uuid)
        self.process = None
        self.start_time = 0
        self.stop_time = 0

    def start(self):
        self.start_time = time()
        self.process = subprocess.Popen(["ffmpeg", "-i", "rtsp://localhost:8554/camera", "-c", "copy", "-map", "0", self.filename], stdin=subprocess.PIPE)

    def stop(self):
        if self.process:
            self.stop_time = time()
            try:
                self.process.communicate(input=b'q', timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                print("Timeout on video writer, killed")
            self.process = None

    def discard(self):
        if self.process:
            self.stop()
        os.remove(self.filename)

recording_router = APIRouter(prefix="/recording")

recorder: Optional[Recorder] = None

@recording_router.post("/start")
def start() -> uuid.UUID:
    global recorder
    if recorder is not None:
        recorder.discard()
    
    recorder = Recorder(uuid.uuid4())
    recorder.start()

    live.drone.record_commands(BinaryRecorder())

    return recorder.uuid

@recording_router.post("/save")
def save(db: DB, name: str):
    global recorder
    if recorder is None:
        return None
    
    recorder.stop()

    commands = live.drone.stop_recording_commands()

    with open(to_flight_path(recorder.uuid), "wb") as f:
        f.write(commands)

    recording = Recording(
        id=recorder.uuid,
        name=name,
        drone_id=None, # TODO use real
        duration=recorder.stop_time - recorder.start_time,
        distance=live.state_computation.distance
    )

    recorder = None
    
    
    db.add(recording)
    db.commit()
    db.refresh(recording)

    return recording

@recording_router.post("/stop")
def stop() -> str:
    global recorder
    if recorder is not None:
        recorder.stop()
    
    live.drone.stop_recording_commands()
    
    return "ok"

@recording_router.post("/discard")
def discard() -> str:
    global recorder
    if recorder is not None:
        recorder.discard()
    
    live.drone.stop_recording_commands()
    
    return "ok"

replay_allowed = True

@recording_router.post("/replay/stop")
async def stop_replay():
    global replay_allowed
    replay_allowed = False

    await live.drone.flight.stop()

    return "Stopped"

@recording_router.post("/replay/{id}")
async def replay(db: DB, id: uuid.UUID):
    global replay_allowed
    obj = db.scalar(select(Recording).where(Recording.id == id))
    if obj is None:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    path = to_flight_path(id)

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Flight path not found")
    
    data = None

    with open(path, "rb") as f:
        data = f.read()
    
    if not live.drone:
        raise HTTPException(status_code=404, detail="Drone not connected")
    
    for delay, cmd, args in BinaryRecorder.decode_commands(data):
        await asyncio.sleep(delay)
        if not replay_allowed:
            replay_allowed = True
            return "STOPPED"
        func = live.drone.flight.__getattribute__(cmd)
        ret = func(*args)
        if ret is not None:
            await ret
    
    return "OK"

@recording_router.get("/")
def get_all(db: DB):
    return db.scalars(select(Recording)).all()


@recording_router.get("/{id}")
def get_by_id(db: DB, id: uuid.UUID):
    return db.scalar(select(Recording).where(Recording.id == id))

@recording_router.delete("/{id}")
def delete_by_id(db: DB, id: uuid.UUID):
    obj = db.scalar(select(Recording).where(Recording.id == id))
    if obj is None:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    db.delete(obj)
    db.commit()

    path = to_video_path(id)
    if os.path.exists(path):
        os.remove(path)
    
    path = to_flight_path(id)
    if os.path.exists(path):
        os.remove(path)

    return "OK"

