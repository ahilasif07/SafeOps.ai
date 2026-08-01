from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.worker import WorkerOut, WorkerCreate, WorkerUpdate
from app.services.worker_service import worker_service

router = APIRouter()

@router.get("/", response_model=List[WorkerOut], summary="List all industrial workers")
def get_workers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return worker_service.get_workers(db, skip=skip, limit=limit)

@router.post("/", response_model=WorkerOut, status_code=status.HTTP_201_CREATED, summary="Create a new worker profile")
def create_worker(worker_in: WorkerCreate, db: Session = Depends(get_db)):
    existing = worker_service.get_worker_by_code(db, worker_in.worker_code)
    if existing:
        raise HTTPException(status_code=400, detail="Worker code already exists")
    return worker_service.create_worker(db, worker_in)

@router.get("/{worker_id}", response_model=WorkerOut, summary="Get worker by ID")
def get_worker(worker_id: int, db: Session = Depends(get_db)):
    worker = worker_service.get_worker(db, worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker

@router.put("/{worker_id}", response_model=WorkerOut, summary="Update worker details")
def update_worker(worker_id: int, worker_in: WorkerUpdate, db: Session = Depends(get_db)):
    worker = worker_service.update_worker(db, worker_id, worker_in)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker

@router.delete("/{worker_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deactivate or delete worker")
def delete_worker(worker_id: int, db: Session = Depends(get_db)):
    success = worker_service.delete_worker(db, worker_id)
    if not success:
        raise HTTPException(status_code=404, detail="Worker not found")
    return None
