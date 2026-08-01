from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.procedure import ProcedureOut, ProcedureCreate, ProcedureUpdate
from app.services.procedure_service import procedure_service

router = APIRouter()

@router.get("/", response_model=List[ProcedureOut], summary="List all Standard Operating Procedures (SOPs)")
def get_procedures(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return procedure_service.get_procedures(db, skip=skip, limit=limit)

@router.post("/", response_model=ProcedureOut, status_code=status.HTTP_201_CREATED, summary="Create approved SOP with hazard steps")
def create_procedure(procedure_in: ProcedureCreate, db: Session = Depends(get_db)):
    return procedure_service.create_procedure(db, procedure_in)

@router.get("/{procedure_id}", response_model=ProcedureOut, summary="Get SOP by ID")
def get_procedure(procedure_id: int, db: Session = Depends(get_db)):
    proc = procedure_service.get_procedure(db, procedure_id)
    if not proc:
        raise HTTPException(status_code=404, detail="Procedure not found")
    return proc

@router.put("/{procedure_id}", response_model=ProcedureOut, summary="Update an existing SOP")
def update_procedure(procedure_id: int, procedure_in: ProcedureCreate, db: Session = Depends(get_db)):
    proc = procedure_service.update_procedure(db, procedure_id, procedure_in)
    if not proc:
        raise HTTPException(status_code=404, detail="Procedure not found")
    return proc
