from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.audit_log import AuditLogOut, AuditLogCreate
from app.services.audit_log_service import audit_log_service

router = APIRouter()

@router.get("/history", response_model=List[AuditLogOut], summary="Get complete audit log history")
@router.get("/", response_model=List[AuditLogOut], summary="Get audit logs")
def get_audit_history(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return audit_log_service.get_history(db, skip=skip, limit=limit)

@router.post("/", response_model=AuditLogOut, status_code=status.HTTP_201_CREATED, summary="Create an audit log entry")
def create_audit_log(log_in: AuditLogCreate, db: Session = Depends(get_db)):
    return audit_log_service.create_log(db, log_in)
