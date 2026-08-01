from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.task import Task, TaskHistory
from app.repositories.base import BaseRepository

class TaskRepository(BaseRepository[Task]):
    def __init__(self):
        super().__init__(Task)

    def get_by_code(self, db: Session, code: str) -> Optional[Task]:
        return db.query(Task).filter(Task.task_code == code).first()

    def get_by_worker(self, db: Session, worker_id: int) -> List[Task]:
        return db.query(Task).filter(Task.worker_id == worker_id).all()

    def create_history(self, db: Session, task_id: int, prev_status: str, new_status: str, worker_id: int, notes: str = None):
        hist = TaskHistory(
            task_id=task_id,
            previous_status=prev_status,
            new_status=new_status,
            changed_by_worker_id=worker_id,
            notes=notes
        )
        db.add(hist)
        db.commit()

task_repository = TaskRepository()
