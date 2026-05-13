from pydantic import BaseModel
from uuid import UUID
import datetime
#TODO des gonze no richtig mochn
class RouteBase(BaseModel):
    name: str
    drone_id: UUID

class RouteCreate(RouteBase):
    pass

class Route(RouteBase):
    id: UUID
    created_at: datetime.datetime
    drone_name: str
    ip: str
    duration: int
    distance: int

    class Config:
        from_attributes = True