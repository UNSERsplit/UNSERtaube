import datetime

from sqlalchemy import Integer, String, ForeignKey, TIMESTAMP, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base # Hier wird die Base aus deiner database.py importiert
import uuid

class Recording(Base):
    __tablename__ = "Recording"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(30))

    drone_id: Mapped[UUID] = mapped_column(ForeignKey("Drone.id"), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, default=datetime.datetime.utcnow)

    duration: Mapped[int]
    distance: Mapped[int]

    # Beziehungen
    drone = relationship("Drone", back_populates="recordings")
