from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.route import Route
from models.drone import Drone
from schemas.route import RouteCreate, Route as RouteSchema
from database import get_db

from uuid import UUID

routes_router = APIRouter(prefix="/route")

@routes_router.post("/")
def create_route_for_drohne(route: RouteCreate, db: Session = Depends(get_db)) -> RouteSchema:
    # Prüfen, ob Drohne existiert
    drohne = db.query(Drone).filter(Drone.id == route.drone_id).first()
    if not drohne:
        raise HTTPException(status_code=404, detail="Drohne nicht gefunden")

    db_route = Route(**route.dict())
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    return db_route

@routes_router.get("/{id}")
def get_route(id: UUID, db: Session = Depends(get_db)) -> RouteSchema:
    return db.query(Route).where(Route.id == id).one()