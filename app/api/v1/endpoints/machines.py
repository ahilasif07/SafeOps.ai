from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.machine import MachineOut, MachineCreate, MachineUpdate
from app.services.machine_service import machine_service

router = APIRouter()

@router.get("/", response_model=List[MachineOut], summary="List all industrial machines")
def get_machines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return machine_service.get_machines(db, skip=skip, limit=limit)

@router.post("/", response_model=MachineOut, status_code=status.HTTP_201_CREATED, summary="Register a new machine")
def create_machine(machine_in: MachineCreate, db: Session = Depends(get_db)):
    return machine_service.create_machine(db, machine_in)

@router.get("/{machine_id}", response_model=MachineOut, summary="Get machine by ID")
def get_machine(machine_id: int, db: Session = Depends(get_db)):
    machine = machine_service.get_machine(db, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@router.put("/{machine_id}", response_model=MachineOut, summary="Update machine status or ratings")
def update_machine(machine_id: int, machine_in: MachineUpdate, db: Session = Depends(get_db)):
    machine = machine_service.update_machine(db, machine_id, machine_in)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine
