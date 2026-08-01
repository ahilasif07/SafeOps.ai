from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MachineBase(BaseModel):
    machine_code: str
    name: str
    model: str
    location: str
    status: str = "OPERATIONAL"
    safety_rating: float = 95.0
    requires_loto: bool = True

class MachineCreate(MachineBase):
    pass

class MachineUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    safety_rating: Optional[float] = None
    requires_loto: Optional[bool] = None
    last_maintenance_at: Optional[datetime] = None

class MachineOut(MachineBase):
    id: int
    last_maintenance_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
