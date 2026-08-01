from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProcedureStepBase(BaseModel):
    step_number: int
    title: str
    instruction: str
    hazard_level: str = "LOW"
    requires_supervisor_signoff: bool = False
    required_ppe: str = "Safety Glasses, Steel Toe Boots"

class ProcedureStepCreate(ProcedureStepBase):
    pass

class ProcedureStepOut(ProcedureStepBase):
    id: int
    procedure_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProcedureBase(BaseModel):
    procedure_code: str
    title: str
    description: Optional[str] = None
    category: str = "ELECTRICAL"
    required_clearance_level: int = 1
    is_approved: bool = True
    version: str = "1.0"

class ProcedureCreate(ProcedureBase):
    steps: List[ProcedureStepCreate] = []

class ProcedureUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    required_clearance_level: Optional[int] = None
    is_approved: Optional[bool] = None
    version: Optional[str] = None

class ProcedureOut(ProcedureBase):
    id: int
    steps: List[ProcedureStepOut] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SopAssignmentRequest(BaseModel):
    procedure_id: int

class SopAssignmentResponse(BaseModel):
    machine_id: int
    procedure_id: int
    message: str = "SOP assigned to machine successfully"
