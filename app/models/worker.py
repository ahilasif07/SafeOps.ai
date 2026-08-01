from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Worker(BaseModel):
    __tablename__ = "workers"

    worker_code = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    role = Column(String(50), nullable=False, default="TECHNICIAN") # TECHNICIAN, SUPERVISOR, SAFETY_OFFICER, MANAGER
    department = Column(String(100), nullable=False, default="MAINTENANCE")
    clearance_level = Column(Integer, nullable=False, default=1) # 1 to 5
    is_active = Column(Boolean, default=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    training_records = relationship("TrainingRecord", back_populates="worker", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="worker")
    incidents = relationship("Incident", back_populates="worker")
    supervisor_approvals = relationship("SupervisorApproval", back_populates="supervisor")
