from typing import Optional
from sqlalchemy.orm import Session
from app.models.supervisor import SupervisorApproval
from app.repositories.base import BaseRepository

class SupervisorRepository(BaseRepository[SupervisorApproval]):
    def __init__(self):
        super().__init__(SupervisorApproval)

    def get_by_task(self, db: Session, task_id: int) -> Optional[SupervisorApproval]:
        return db.query(SupervisorApproval).filter(SupervisorApproval.task_id == task_id).first()

supervisor_repository = SupervisorRepository()
