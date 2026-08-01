from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AuditLogBase(BaseModel):
    worker_id: Optional[int] = None
    machine_id: Optional[int] = None
    procedure_id: Optional[int] = None
    task_id: Optional[int] = None
    steps_completed: str
    status: str = "COMPLETED"
    notes: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogOut(AuditLogBase):
    id: int
    completion_time: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
