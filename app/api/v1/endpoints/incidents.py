from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.incident import IncidentOut, IncidentCreate, IncidentUpdate
from app.services.incident_service import incident_service

router = APIRouter()

@router.get("/", response_model=List[IncidentOut], summary="List safety incidents & near-miss reports")
def get_incidents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return incident_service.get_incidents(db, skip=skip, limit=limit)

@router.post("/", response_model=IncidentOut, status_code=status.HTTP_201_CREATED, summary="Report a safety incident")
def create_incident(incident_in: IncidentCreate, db: Session = Depends(get_db)):
    return incident_service.create_incident(db, incident_in)
