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

    def delete_machine(self, db: Session, machine_id: int) -> bool:
        machine = machine_repository.get(db, machine_id)
        if not machine:
            return False
        db.delete(machine)
        db.commit()
        return True

    def assign_sop(self, db: Session, machine_id: int, procedure_id: int) -> bool:
        from app.models.procedure import Procedure
        machine = machine_repository.get(db, machine_id)
        procedure = db.query(Procedure).filter(Procedure.id == procedure_id).first()
        if not machine or not procedure:
            return False
        if procedure not in machine.sops:
            machine.sops.append(procedure)
            db.commit()
        return True

    def get_machine_sops(self, db: Session, machine_id: int):
        machine = machine_repository.get(db, machine_id)
        if not machine:
            return None
        return machine.sops

machine_service = MachineService()
