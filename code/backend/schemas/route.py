from pydantic import BaseModel
from uuid import UUID
#TODO des gonze no richtig mochn
class RouteBase(BaseModel):
    name: str
    drone_id: UUID

class RouteCreate(RouteBase):
    pass

class Route(RouteBase):
    id: UUID

    class Config:
        from_attributes = True