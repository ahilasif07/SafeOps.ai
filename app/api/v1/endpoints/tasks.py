from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.task import TaskOut, TaskCreate, TaskUpdate
from app.services.task_service import task_service

router = APIRouter()

@router.get("/", response_model=List[TaskOut], summary="List all maintenance tasks & safety status")
def get_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return task_service.get_tasks(db, skip=skip, limit=limit)

@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED, summary="Submit maintenance task order (Evaluates safety risk)")
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    try:
        return task_service.create_task(db, task_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{task_id}", response_model=TaskOut, summary="Get task by ID")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task order not found")
    return task

@router.put("/{task_id}/status", response_model=TaskOut, summary="Update task status (e.g., APPROVED, COMPLETED)")
def update_task_status(task_id: int, status_name: str, worker_id: int, notes: str = None, db: Session = Depends(get_db)):
    task = task_service.update_task_status(db, task_id, status_name, worker_id, notes)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}/complete", response_model=TaskOut, summary="Complete task and record audit log")
def complete_task(task_id: int, worker_id: int, steps_completed: str = "All steps executed", notes: str = None, db: Session = Depends(get_db)):
    task = task_service.complete_task(db, task_id, worker_id, steps_completed=steps_completed, notes=notes)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
