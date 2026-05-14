from pydantic import BaseModel
import uuid
import datetime
from typing import Optional

from .drone import Drone

class Recording(BaseModel):
    id: uuid.UUID
    name: str
    duration: float
    distance: float
    created_at: datetime.datetime

    drone: Drone