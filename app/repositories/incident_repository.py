from typing import List
from sqlalchemy.orm import Session
from app.models.incident import Incident
from app.repositories.base import BaseRepository

class IncidentRepository(BaseRepository[Incident]):
    def __init__(self):
        super().__init__(Incident)

    def get_by_machine(self, db: Session, machine_id: int) -> List[Incident]:
        return db.query(Incident).filter(Incident.machine_id == machine_id).all()

incident_repository = IncidentRepository()
