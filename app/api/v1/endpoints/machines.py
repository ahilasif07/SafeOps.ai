from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.machine import MachineOut, MachineCreate, MachineUpdate
from app.schemas.procedure import ProcedureOut, SopAssignmentRequest, SopAssignmentResponse
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

@router.delete("/{machine_id}", status_code=status.HTTP_200_OK, summary="Delete machine")
def delete_machine(machine_id: int, db: Session = Depends(get_db)):
    success = machine_service.delete_machine(db, machine_id)
    if not success:
        raise HTTPException(status_code=404, detail="Machine not found")
    return {"detail": "Machine deleted successfully"}

@router.post("/{machine_id}/sops", response_model=SopAssignmentResponse, summary="Assign SOP to machine")
def assign_sop_to_machine(machine_id: int, request: SopAssignmentRequest, db: Session = Depends(get_db)):
    success = machine_service.assign_sop(db, machine_id, request.procedure_id)
    if not success:
        raise HTTPException(status_code=404, detail="Machine or Procedure not found")
    return SopAssignmentResponse(machine_id=machine_id, procedure_id=request.procedure_id)

@router.get("/{machine_id}/sops", response_model=List[ProcedureOut], summary="Get SOPs assigned to machine")
def get_machine_sops(machine_id: int, db: Session = Depends(get_db)):
    sops = machine_service.get_machine_sops(db, machine_id)
    if sops is None:
        raise HTTPException(status_code=404, detail="Machine not found")
    return sops
