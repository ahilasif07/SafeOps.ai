from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from app.models.base import BaseModel

class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    worker_id = Column(Integer, ForeignKey("workers.id", ondelete="SET NULL"), nullable=True)
    machine_id = Column(Integer, ForeignKey("machines.id", ondelete="SET NULL"), nullable=True)
    procedure_id = Column(Integer, ForeignKey("procedures.id", ondelete="SET NULL"), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    steps_completed = Column(Text, nullable=False, default="")
    completion_time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    status = Column(String(50), default="COMPLETED", nullable=False)
    notes = Column(Text, nullable=True)

    worker = relationship("Worker")
    machine = relationship("Machine")
    procedure = relationship("Procedure")
    task = relationship("Task")
