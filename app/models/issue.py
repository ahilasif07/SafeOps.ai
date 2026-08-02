from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
import datetime
from app.models.base import BaseModel

class Issue(BaseModel):
    __tablename__ = "issues"

    issue_code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    machine_id = Column(Integer, ForeignKey("machines.id", ondelete="SET NULL"), nullable=True)
    department = Column(String(100), nullable=False, default="PLANT_OPS")
    priority = Column(String(50), nullable=False, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(50), nullable=False, default="Open")  # Open, In Progress, Waiting, Resolved, Closed
    
    reporter_id = Column(Integer, ForeignKey("workers.id", ondelete="SET NULL"), nullable=True)
    assigned_worker_id = Column(Integer, ForeignKey("workers.id", ondelete="SET NULL"), nullable=True)
    assigned_supervisor_id = Column(Integer, ForeignKey("workers.id", ondelete="SET NULL"), nullable=True)
    
    due_date = Column(DateTime, nullable=True)
    resolution = Column(Text, nullable=True)
    resolution_time = Column(DateTime, nullable=True)

    machine = relationship("Machine")
    reporter = relationship("Worker", foreign_keys=[reporter_id])
    assigned_worker = relationship("Worker", foreign_keys=[assigned_worker_id])
    assigned_supervisor = relationship("Worker", foreign_keys=[assigned_supervisor_id])

    comments = relationship("IssueComment", back_populates="issue", cascade="all, delete-orphan")
    attachments = relationship("IssueAttachment", back_populates="issue", cascade="all, delete-orphan")
    status_history = relationship("IssueStatusHistory", back_populates="issue", cascade="all, delete-orphan")
    ownership_history = relationship("IssueOwnershipHistory", back_populates="issue", cascade="all, delete-orphan", order_by="desc(IssueOwnershipHistory.changed_at)")


class IssueComment(BaseModel):
    __tablename__ = "issue_comments"

    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("workers.id", ondelete="SET NULL"), nullable=True)
    author_name = Column(String(100), nullable=False, default="System User")
    comment_text = Column(Text, nullable=False)

    issue = relationship("Issue", back_populates="comments")
    author = relationship("Worker")


class IssueAttachment(BaseModel):
    __tablename__ = "issue_attachments"

    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_url = Column(Text, nullable=False)
    file_type = Column(String(50), nullable=False, default="document")
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    issue = relationship("Issue", back_populates="attachments")


class IssueStatusHistory(BaseModel):
    __tablename__ = "issue_status_history"

    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    changed_by_id = Column(Integer, ForeignKey("workers.id", ondelete="SET NULL"), nullable=True)
    from_status = Column(String(50), nullable=False)
    to_status = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    changed_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    issue = relationship("Issue", back_populates="status_history")
    changed_by = relationship("Worker")


class IssueOwnershipHistory(BaseModel):
    __tablename__ = "issue_ownership_history"

    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(50), nullable=False)  # INITIAL_CREATION, ASSIGN_OWNER, TRANSFER_OWNERSHIP, REASSIGN_DEPARTMENT, ESCALATE, CLOSE_ISSUE
    
    previous_owner_id = Column(Integer, ForeignKey("workers.id", ondelete="SET NULL"), nullable=True)
    new_owner_id = Column(Integer, ForeignKey("workers.id", ondelete="SET NULL"), nullable=True)
    
    previous_supervisor_id = Column(Integer, ForeignKey("workers.id", ondelete="SET NULL"), nullable=True)
    new_supervisor_id = Column(Integer, ForeignKey("workers.id", ondelete="SET NULL"), nullable=True)
    
    previous_department = Column(String(100), nullable=True)
    new_department = Column(String(100), nullable=True)
    
    changed_by_id = Column(Integer, ForeignKey("workers.id", ondelete="SET NULL"), nullable=True)
    reason_notes = Column(Text, nullable=True)
    changed_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    issue = relationship("Issue", back_populates="ownership_history")
    previous_owner = relationship("Worker", foreign_keys=[previous_owner_id])
    new_owner = relationship("Worker", foreign_keys=[new_owner_id])
    previous_supervisor = relationship("Worker", foreign_keys=[previous_supervisor_id])
    new_supervisor = relationship("Worker", foreign_keys=[new_supervisor_id])
    changed_by = relationship("Worker", foreign_keys=[changed_by_id])
