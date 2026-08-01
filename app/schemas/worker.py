from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class WorkerBase(BaseModel):
    worker_code: str
    full_name: str
    email: EmailStr
    role: str = "TECHNICIAN"
    department: str = "MAINTENANCE"
    clearance_level: int = 1
    is_active: bool = True

class WorkerCreate(WorkerBase):
    password: str

class WorkerUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    department: Optional[str] = None
    clearance_level: Optional[int] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class WorkerOut(WorkerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
