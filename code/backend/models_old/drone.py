from pydantic import BaseModel, UUID4
from typing import Optional

class Drone(BaseModel):
    id: UUID4
    name: Optional[str]
    serial: str

class UpdateDroneName(BaseModel):
    name: str