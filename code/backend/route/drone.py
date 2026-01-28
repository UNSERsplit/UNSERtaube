from fastapi import APIRouter, Path, Body
from models.drone import Drone, UpdateDroneName
from pydantic import UUID4
from typing import Annotated

router = APIRouter(prefix="/drone")

@router.get("/known")
def get_known_drones() -> list[Drone]:
    return []

@router.put("/{id}")
def update_drone_name(
            id: Annotated[UUID4, Path()],
            body: Annotated[UpdateDroneName, Body()]) -> Drone:
    return Drone(
        id=id,
        name=body.name,
        serial="123456789"
    )

