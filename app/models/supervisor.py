from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class SupervisorApproval(BaseModel):
    __tablename__ = "supervisor_approvals"

    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    supervisor_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    status = Column(String(20), default="PENDING", nullable=False) # PENDING, APPROVED, REJECTED
    comments = Column(Text, nullable=True)
    decided_at = Column(DateTime, nullable=True)

    task = relationship("Task", back_populates="supervisor_approvals")
    supervisor = relationship("Worker", back_populates="supervisor_approvals")
