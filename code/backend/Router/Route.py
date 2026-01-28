from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from .. import router
from ..Models import  Route
from ..database import get_db


@router.post("/routen/", response_model=Route)
def create_route_for_drohne(route: Route, db: Session = Depends(get_db)):
    # Prüfen, ob Drohne existiert
    drohne = db.query(Route).filter(Route.id == route.id_Drohne).first()
    if not drohne:
        raise HTTPException(status_code=404, detail="Drohne nicht gefunden")

    db_route = Route(**route.dict())
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    return db_route