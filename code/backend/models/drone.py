from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base # Hier wird die Base aus deiner database.py importiert
import uuid

class Drone(Base):
    __tablename__ = "Drone"

    # UUID als Primary Key, wie in deiner Datei definiert
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    ip = Column(String)

    # Beziehung zu Route (1:n)
    routes = relationship("Route", back_populates="drone")