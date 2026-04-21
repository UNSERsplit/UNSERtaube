from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.route import Route
from models.drone import Drone
from schemas.route import RouteCreate, Route as RouteSchema
from database import get_db

from uuid import UUID

routes_router = APIRouter(prefix="/route")

@routes_router.get("/")
def get_route(db: Session = Depends(get_db)) -> list[RouteSchema]:
    d = db.query(Route,Drone.name,Drone.ip).join(Route.drone).all()
    l = []
    for data in d:
        route, name, ip = data
        l.append(
            RouteSchema(
                name=route.name,
                drone_id=route.drone_id,
                id=route.id,
                created_at=route.created_at,
                drone_name=name,
                ip=ip,
                distance=route.distance,
                duration=route.duration
            )
        )
    
    return l