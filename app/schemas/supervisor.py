from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SupervisorApprovalCreate(BaseModel):
    task_id: int
    supervisor_id: int
    comments: Optional[str] = None

class SupervisorApprovalUpdate(BaseModel):
    status: str
    comments: Optional[str] = None

class SupervisorApprovalOut(BaseModel):
    id: int
    task_id: int
    supervisor_id: int
    status: str
    comments: Optional[str]
    decided_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
