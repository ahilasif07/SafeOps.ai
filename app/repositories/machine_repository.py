from typing import Optional
from sqlalchemy.orm import Session
from app.models.machine import Machine
from app.repositories.base import BaseRepository

class MachineRepository(BaseRepository[Machine]):
    def __init__(self):
        super().__init__(Machine)

    def get_by_code(self, db: Session, code: str) -> Optional[Machine]:
        return db.query(Machine).filter(Machine.machine_code == code).first()

machine_repository = MachineRepository()
