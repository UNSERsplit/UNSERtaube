from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db

router = APIRouter(
    prefix="/mission",
    tags=["Mission Control"]
)


# --- DROHNEN VERWALTUNG ---

@router.post("/drohnen/", response_model=schemas.Drohne)
def create_drohne(drohne: schemas.DrohneCreate, db: Session = Depends(get_db)):
    db_drohne = models.Drohne(Name=drohne.Name, IP=drohne.IP)
    db.add(db_drohne)
    db.commit()
    db.refresh(db_drohne)
    return db_drohne


@router.get("/drohnen/", response_model=List[schemas.Drohne])
def read_drohnen(db: Session = Depends(get_db)):
    return db.query(models.Drohne).all()


# --- ROUTEN VERWALTUNG (1:n) ---

@router.post("/routen/", response_model=schemas.Route)
def create_route_for_drohne(route: schemas.RouteCreate, db: Session = Depends(get_db)):
    # Prüfen, ob Drohne existiert
    drohne = db.query(models.Drohne).filter(models.Drohne.id == route.id_Drohne).first()
    if not drohne:
        raise HTTPException(status_code=404, detail="Drohne nicht gefunden")

    db_route = models.Route(**route.dict())
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    return db_route


# --- ROUTE ENTRIES (Die Flugdaten) ---

@router.post("/entries/", response_model=schemas.RouteEntry)
def add_telemetry_entry(entry: schemas.EntryCreate, db: Session = Depends(get_db)):
    db_entry = models.RouteEntry(**entry.dict())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.get("/routen/{route_id}/details")
def get_full_route_details(route_id: str, db: Session = Depends(get_db)):
    # Nutzt die SQLAlchemy relationship, um alles auf einmal zu laden
    route = db.query(models.Route).filter(models.Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route nicht gefunden")
    return {
        "route_name": route.Name,
        "drohne": route.drohne.Name,
        "telemetry_data": route.entries
    }