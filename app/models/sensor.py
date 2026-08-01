from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from app.models.base import BaseModel

class SensorReading(BaseModel):
    __tablename__ = "sensor_readings"

    machine_id = Column(Integer, ForeignKey("machines.id", ondelete="CASCADE"), nullable=False)
    sensor_type = Column(String(50), nullable=False) # TEMPERATURE, PRESSURE, VIBRATION, TOXIC_GAS, EMERGENCY_STOP
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False) # C, PSI, mm/s, ppm, BOOL
    is_anomaly = Column(Boolean, default=False, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    machine = relationship("Machine", back_populates="sensor_readings")
