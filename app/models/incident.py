from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from app.models.base import BaseModel

class Incident(BaseModel):
    __tablename__ = "incidents"

    incident_code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="MEDIUM", nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    reported_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    resolution_status = Column(String(30), default="OPEN", nullable=False) # OPEN, UNDER_INVESTIGATION, RESOLVED, CLOSED

    machine = relationship("Machine", back_populates="incidents")
    worker = relationship("Worker", back_populates="incidents")
    task = relationship("Task", back_populates="incidents")
