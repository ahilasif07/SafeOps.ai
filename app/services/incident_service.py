from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.incident_repository import incident_repository
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.models.incident import Incident

class IncidentService:
    def get_incidents(self, db: Session, skip: int = 0, limit: int = 100) -> List[Incident]:
        return incident_repository.get_all(db, skip=skip, limit=limit)

    def create_incident(self, db: Session, incident_in: IncidentCreate) -> Incident:
        return incident_repository.create(db, incident_in.dict())

incident_service = IncidentService()
