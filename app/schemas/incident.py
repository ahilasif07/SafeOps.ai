from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class IncidentBase(BaseModel):
    incident_code: str
    title: str
    description: str
    severity: str = "MEDIUM"
    machine_id: int
    worker_id: Optional[int] = None
    task_id: Optional[int] = None

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    resolution_status: Optional[str] = None

class IncidentOut(IncidentBase):
    id: int
    reported_at: datetime
    resolution_status: str
    created_at: datetime

    class Config:
        from_attributes = True
