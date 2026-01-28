from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base # Hier wird die Base aus deiner database.py importiert
import uuid

class Drohne(Base):
    __tablename__ = "Drohne"

    # UUID als Primary Key, wie in deiner Datei definiert
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    Name = Column(String)
    IP = Column(String)

    # Beziehung zu Route (1:n)
    routen = relationship("Route", back_populates="drohne")

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

class RouteEntry(Base):
    __tablename__ = "RouteEntry"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    Timestamp = Column(TIMESTAMP, nullable=True)

    # Die numerischen Werte (Throttle, Yaw, Pitch, Roll) sind als numeric(4,1) definiert
    Throttle = Column(Numeric(precision=4, scale=1))
    Yaw = Column(Numeric(precision=4, scale=1))
    Pitch = Column(Numeric(precision=4, scale=1))
    Roll = Column(Numeric(precision=4, scale=1))

    # Fremdschlüssel zur Route
    id_Route = Column(UUID(as_uuid=True), ForeignKey("Route.id"), nullable=False)

    # Beziehung zurück zur Route
    route = relationship("Route", back_populates="entries")