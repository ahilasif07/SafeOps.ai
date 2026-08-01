from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.worker import WorkerOut

class CertificationBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    validity_months: int = 24
    issuing_body: str = "OSHA Safety Institute"

class CertificationCreate(CertificationBase):
    pass

class CertificationOut(CertificationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TrainingRecordCreate(BaseModel):
    worker_id: int
    certification_id: int
    issued_date: datetime
    expiry_date: datetime
    is_valid: bool = True

class TrainingRecordOut(BaseModel):
    id: int
    worker_id: int
    certification_id: int
    issued_date: datetime
    expiry_date: datetime
    is_valid: bool
    certification: Optional[CertificationOut] = None

    class Config:
        from_attributes = True
