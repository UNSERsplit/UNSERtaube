from typing import Iterable

from fastapi import APIRouter, HTTPException
import uuid
from sqlalchemy import select

from database import DB
from models.drone import Drone
from schemas.drone import DroneCreate, Drone as DroneDTO

drone_router = APIRouter(prefix="/drone")

@drone_router.get("/")
async def get_all(db: DB) -> Iterable[DroneDTO]:
    expr = select(Drone)

    return db.scalars(expr).all() # type: ignore

@drone_router.post("/")
async def create(db: DB, dto: DroneCreate) -> DroneDTO:
    drone = Drone(
        ip=dto.ip,
        name=dto.name
    )

    db.add(drone)
    db.commit()
    db.refresh(drone)

    return drone # type: ignore

@drone_router.get("/{id}", responses={404: {"model": str}})
async def get_by_id(db: DB, id: uuid.UUID) -> DroneDTO:
    expr = select(Drone).where(Drone.id == id)

    obj = db.scalar(expr)
    if not obj:
        raise HTTPException(status_code=404, detail="Drone not found")

    print(obj)
    print(obj.recordings)

    return obj # type: ignore

@drone_router.delete("/{id}", responses={404: {"model": str}})
async def delete_by_id(db: DB, id: uuid.UUID) -> str:
    expr = select(Drone).where(Drone.id == id)
    obj = db.scalar(expr)
    if not obj:
        raise HTTPException(status_code=404, detail="Drone not found")

    db.delete(obj)
    db.commit()

    return "OK"