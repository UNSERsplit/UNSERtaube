from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base # Hier wird die Base aus deiner database.py importiert
import uuid
from .route_entry import RouteEntry

class Route(Base):
    __tablename__ = "Route"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    video = Column(Integer)
    Flugvideo = Column(String) # cltype: text in deiner Datei

    # Fremdschlüssel zur Drohne
    drone_id = Column(UUID(as_uuid=True), ForeignKey("Drone.id"), nullable=False)

    # Beziehungen
    drone = relationship("Drone", back_populates="routes")
    entries = relationship("RouteEntry", back_populates="route")