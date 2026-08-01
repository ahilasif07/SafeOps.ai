from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.audit_log_repository import audit_log_repository
from app.schemas.audit_log import AuditLogCreate
from app.models.audit_log import AuditLog

class AuditLogService:
    def create_log(self, db: Session, log_in: AuditLogCreate) -> AuditLog:
        return audit_log_repository.create(db, log_in.dict())

    def get_history(self, db: Session, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        return audit_log_repository.get_history(db, skip=skip, limit=limit)

    def get_logs_by_worker(self, db: Session, worker_id: int) -> List[AuditLog]:
        return audit_log_repository.get_by_worker(db, worker_id)

audit_log_service = AuditLogService()
