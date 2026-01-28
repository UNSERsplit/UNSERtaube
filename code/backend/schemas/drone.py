from pydantic import BaseModel
from uuid import UUID

class DroneBase(BaseModel):
    name: str
    ip: str

class DroneCreate(DroneBase):
    pass

class Drone(DroneBase):
    id: UUID

    class Config:
        from_attributes = True