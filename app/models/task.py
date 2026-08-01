from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Task(BaseModel):
    __tablename__ = "tasks"

    task_code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    procedure_id = Column(Integer, ForeignKey("procedures.id"), nullable=False)
    status = Column(String(30), default="PENDING", nullable=False) # PENDING, APPROVED, IN_PROGRESS, COMPLETED, BLOCKED, CANCELLED
    risk_score = Column(Float, default=0.0, nullable=False) # 0 to 100
    risk_level = Column(String(20), default="LOW", nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    block_reason = Column(Text, nullable=True)

    worker = relationship("Worker", back_populates="tasks")
    machine = relationship("Machine", back_populates="tasks")
    procedure = relationship("Procedure", back_populates="tasks")
    history = relationship("TaskHistory", back_populates="task", cascade="all, delete-orphan", order_by="TaskHistory.created_at.desc()")
    supervisor_approvals = relationship("SupervisorApproval", back_populates="task", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="task")

class TaskHistory(BaseModel):
    __tablename__ = "task_history"

    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    previous_status = Column(String(30), nullable=False)
    new_status = Column(String(30), nullable=False)
    changed_by_worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    notes = Column(Text, nullable=True)

    task = relationship("Task", back_populates="history")
