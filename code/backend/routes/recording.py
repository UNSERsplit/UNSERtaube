from typing import Optional
import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
import subprocess
import os

from models.recording import Recording

from database import DB

def to_path(uuid: uuid.UUID) -> str:
    return os.path.join(f"videos/{uuid.hex}.mp4")

class Recorder:
    def __init__(self, uuid: uuid.UUID) -> None:
        self.uuid = uuid
        self.filename = to_path(uuid)
        self.process = None

    def start(self):
        self.process = subprocess.Popen(["ffmpeg", "-i", "rtsp://localhost:8554/camera", "-c", "copy", "-map", "0", self.filename], stdin=subprocess.PIPE)

    def stop(self):
        if self.process:
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

    return recorder.uuid

@recording_router.post("/save")
def save(db: DB, name: str):
    global recorder
    if recorder is None:
        return None
    
    recorder.stop()

    recording = Recording(
        id=recorder.uuid,
        name=name,
        drone_id=None,
        duration=999,
        distance=100
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
    
    return "ok"

@recording_router.post("/discard")
def discard() -> str:
    global recorder
    if recorder is not None:
        recorder.discard()
    
    return "ok"

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

    path = to_path(id)
    if os.path.exists(path):
        os.remove(path)

    return "OK"

