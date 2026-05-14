from pydantic import BaseModel
import uuid

class DroneCreate(BaseModel):
    name: str
    ip: str

class Drone(DroneCreate):
    id: uuid.UUID