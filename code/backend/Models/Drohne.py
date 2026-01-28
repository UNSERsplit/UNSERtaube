from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base # Hier wird die Base aus deiner database.py importiert
import uuid

class Drohne(Base):
    __tablename__ = "Drohne"

    # UUID als Primary Key, wie in deiner Datei definiert
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    Name = Column(String)
    IP = Column(String)

    # Beziehung zu Route (1:n)
    routen = relationship("Route", back_populates="drohne")