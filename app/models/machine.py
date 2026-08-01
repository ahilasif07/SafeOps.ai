from sqlalchemy import Column, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
import datetime
from app.models.base import BaseModel

class Machine(BaseModel):
    __tablename__ = "machines"

    machine_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="OPERATIONAL") # OPERATIONAL, MAINTENANCE, LOCKED_OUT, HAZARDOUS
    last_maintenance_at = Column(DateTime, default=datetime.datetime.utcnow)
    safety_rating = Column(Float, default=95.0) # 0 to 100
    requires_loto = Column(Boolean, default=True)

    tasks = relationship("Task", back_populates="machine")
    incidents = relationship("Incident", back_populates="machine")
    sensor_readings = relationship("SensorReading", back_populates="machine", cascade="all, delete-orphan")
