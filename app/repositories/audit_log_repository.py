from typing import List
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository

class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self):
        super().__init__(AuditLog)

    def get_by_worker(self, db: Session, worker_id: int) -> List[AuditLog]:
        return db.query(AuditLog).filter(AuditLog.worker_id == worker_id).order_by(AuditLog.completion_time.desc()).all()

    def get_history(self, db: Session, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        return db.query(AuditLog).order_by(AuditLog.completion_time.desc()).offset(skip).limit(limit).all()

audit_log_repository = AuditLogRepository()
