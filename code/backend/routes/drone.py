from fastapi import APIRouter

from database import DB
from models.drone import Drone

from sqlalchemy import select

drone_router = APIRouter(prefix="/drone")

@drone_router.get("/")
async def get_all(db: DB):
    expr = select(Drone)

    return db.scalar(expr)