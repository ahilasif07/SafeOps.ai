from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.certification import Certification, TrainingRecord
from app.repositories.base import BaseRepository

class CertificationRepository(BaseRepository[Certification]):
    def __init__(self):
        super().__init__(Certification)

    def get_by_code(self, db: Session, code: str) -> Optional[Certification]:
        return db.query(Certification).filter(Certification.code == code).first()

    def get_worker_training(self, db: Session, worker_id: int) -> List[TrainingRecord]:
        return db.query(TrainingRecord).filter(TrainingRecord.worker_id == worker_id, TrainingRecord.is_valid == True).all()

certification_repository = CertificationRepository()
