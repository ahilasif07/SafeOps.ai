from typing import Optional
from sqlalchemy.orm import Session
from app.models.worker import Worker
from app.repositories.base import BaseRepository

class WorkerRepository(BaseRepository[Worker]):
    def __init__(self):
        super().__init__(Worker)

    def get_by_email(self, db: Session, email: str) -> Optional[Worker]:
        return db.query(Worker).filter(Worker.email == email).first()

    def get_by_code(self, db: Session, code: str) -> Optional[Worker]:
        return db.query(Worker).filter(Worker.worker_code == code).first()

worker_repository = WorkerRepository()
