from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.task_repository import task_repository
from app.schemas.task import TaskCreate, TaskUpdate
from app.models.task import Task
from app.services.risk_service import risk_service
from app.schemas.safety_eval import SafetyEvalRequest

class TaskService:
    def get_tasks(self, db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
        return task_repository.get_all(db, skip=skip, limit=limit)

    def get_task(self, db: Session, task_id: int) -> Optional[Task]:
        return task_repository.get(db, task_id)

    def create_task(self, db: Session, task_in: TaskCreate) -> Task:
        # Run automated safety evaluation
        eval_req = SafetyEvalRequest(
            worker_id=task_in.worker_id,
            machine_id=task_in.machine_id,
            procedure_id=task_in.procedure_id
        )
        eval_res = risk_service.evaluate_task_safety(db, eval_req)

        data = task_in.dict()
        data["risk_score"] = eval_res.risk_score
        data["risk_level"] = eval_res.risk_level

        if eval_res.is_blocked:
            data["status"] = "BLOCKED"
            data["block_reason"] = " | ".join(eval_res.block_reasons)
        elif eval_res.decision == "SUPERVISOR_APPROVAL_REQUIRED":
            data["status"] = "PENDING"
            data["block_reason"] = "High safety risk requires supervisor sign-off before execution."
        else:
            data["status"] = "APPROVED"

        task = task_repository.create(db, data)
        task_repository.create_history(db, task.id, "NONE", task.status, task.worker_id, f"Initial task submission. Risk: {eval_res.risk_score}")
        return task

    def update_task_status(self, db: Session, task_id: int, new_status: str, worker_id: int, notes: str = None) -> Optional[Task]:
        task = task_repository.get(db, task_id)
        if not task:
            return None
        prev_status = task.status
        task.status = new_status
        db.commit()
        db.refresh(task)

        task_repository.create_history(db, task.id, prev_status, new_status, worker_id, notes)
        return task

task_service = TaskService()
