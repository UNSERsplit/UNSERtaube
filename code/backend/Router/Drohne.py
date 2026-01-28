# --- DROHNEN VERWALTUNG ---
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import router
from ..Models import  Drohne
from ..database import get_db


DrohneROuter = APIRouter(prefix="/api/Drohne")

@router.post("/drohnen/", response_model=Drohne)
def create_drohne(drohne: Drohne, db: Session = Depends(get_db)):
    db_drohne = Drohne(Name=drohne.Name, IP=drohne.IP)
    db.add(db_drohne)
    db.commit()
    db.refresh(db_drohne)
    return db_drohne


@router.get("/drohnen/", response_model=List[Drohne])
def read_drohnen(db: Session = Depends(get_db)):
    return db.query(Drohne).all()