from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.machine_repository import machine_repository
from app.schemas.machine import MachineCreate, MachineUpdate
from app.models.machine import Machine

class MachineService:
    def get_machines(self, db: Session, skip: int = 0, limit: int = 100) -> List[Machine]:
        return machine_repository.get_all(db, skip=skip, limit=limit)

    def get_machine(self, db: Session, machine_id: int) -> Optional[Machine]:
        return machine_repository.get(db, machine_id)

    def create_machine(self, db: Session, machine_in: MachineCreate) -> Machine:
        return machine_repository.create(db, machine_in.dict())

    def update_machine(self, db: Session, machine_id: int, machine_in: MachineUpdate) -> Optional[Machine]:
        machine = machine_repository.get(db, machine_id)
        if not machine:
            return None
        return machine_repository.update(db, machine, machine_in.dict(exclude_unset=True))

machine_service = MachineService()
