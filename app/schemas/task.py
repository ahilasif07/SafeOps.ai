from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.worker import WorkerOut
from app.schemas.machine import MachineOut
from app.schemas.procedure import ProcedureOut

class TaskBase(BaseModel):
    task_code: str
    title: str
    description: Optional[str] = None
    worker_id: int
    machine_id: int
    procedure_id: int

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    block_reason: Optional[str] = None

class TaskHistoryOut(BaseModel):
    id: int
    task_id: int
    previous_status: str
    new_status: str
    changed_by_worker_id: Optional[int]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class TaskOut(TaskBase):
    id: int
    status: str
    risk_score: float
    risk_level: str
    block_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    worker: Optional[WorkerOut] = None
    machine: Optional[MachineOut] = None
    procedure: Optional[ProcedureOut] = None
    history: List[TaskHistoryOut] = []

    class Config:
        from_attributes = True
