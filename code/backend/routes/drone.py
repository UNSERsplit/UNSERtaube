# --- DROHNEN VERWALTUNG ---
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Sequence
from models.drone import Drone
from schemas.drone import Drone as DroneSchema, DroneCreate
from database import get_db
import os
import dronemaster



drone_router = APIRouter(prefix="/drone")

@drone_router.post("/scan")
async def scan() -> list[dronemaster.ScanResult]:
    return await dronemaster.scan(os.environ["EXTERNAL_IP"])

@drone_router.post("/")
def create_drohne(drohne: DroneCreate, db: Session = Depends(get_db)) -> DroneSchema:
    db_drohne = Drone(name=drohne.name, ip=drohne.ip)
    db.add(db_drohne)
    db.commit()
    db.refresh(db_drohne)
    return db_drohne


@drone_router.get("/")
def read_drohnen(db: Session = Depends(get_db)) -> Sequence[DroneSchema]:
    return db.query(Drone).all()