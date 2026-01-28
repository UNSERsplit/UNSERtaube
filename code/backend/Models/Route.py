from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base # Hier wird die Base aus deiner database.py importiert
import uuid

class Route(Base):
    __tablename__ = "Route"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    Name = Column(String)
    Video = Column(Integer)
    Flugvideo = Column(String) # cltype: text in deiner Datei

    # Fremdschlüssel zur Drohne
    id_Drohne = Column(UUID(as_uuid=True), ForeignKey("Drohne.id"), nullable=False)

    # Beziehungen
    drohne = relationship("Drohne", back_populates="routen")
    entries = relationship("RouteEntry", back_populates="route")