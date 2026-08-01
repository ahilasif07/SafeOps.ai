from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.worker_repository import worker_repository
from app.schemas.worker import WorkerCreate, WorkerUpdate
from app.models.worker import Worker
from app.auth.security import get_password_hash

class WorkerService:
    def get_workers(self, db: Session, skip: int = 0, limit: int = 100) -> List[Worker]:
        return worker_repository.get_all(db, skip=skip, limit=limit)

    def get_worker(self, db: Session, worker_id: int) -> Optional[Worker]:
        return worker_repository.get(db, worker_id)

    def get_worker_by_code(self, db: Session, code: str) -> Optional[Worker]:
        return worker_repository.get_by_code(db, code)

    def create_worker(self, db: Session, worker_in: WorkerCreate) -> Worker:
        data = worker_in.dict()
        data["hashed_password"] = get_password_hash(data.pop("password"))
        return worker_repository.create(db, data)

    def update_worker(self, db: Session, worker_id: int, worker_in: WorkerUpdate) -> Optional[Worker]:
        worker = worker_repository.get(db, worker_id)
        if not worker:
            return None
        data = worker_in.dict(exclude_unset=True)
        if "password" in data and data["password"]:
            data["hashed_password"] = get_password_hash(data.pop("password"))
        return worker_repository.update(db, worker, data)

    def delete_worker(self, db: Session, worker_id: int) -> bool:
        return worker_repository.delete(db, worker_id)

worker_service = WorkerService()
