from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.certification import Certification, TrainingRecord
from app.schemas.certification import CertificationOut, CertificationCreate, TrainingRecordOut, TrainingRecordCreate

router = APIRouter()

@router.get("/", response_model=List[CertificationOut], summary="List all safety certifications")
def get_certifications(db: Session = Depends(get_db)):
    return db.query(Certification).all()

@router.post("/", response_model=CertificationOut, status_code=status.HTTP_201_CREATED, summary="Create new certification type")
def create_certification(cert_in: CertificationCreate, db: Session = Depends(get_db)):
    cert = Certification(**cert_in.dict())
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert

@router.get("/worker/{worker_id}", response_model=List[TrainingRecordOut], summary="List valid training records for a worker")
def get_worker_training(worker_id: int, db: Session = Depends(get_db)):
    return db.query(TrainingRecord).filter(TrainingRecord.worker_id == worker_id).all()
