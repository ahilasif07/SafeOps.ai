from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.procedure_repository import procedure_repository
from app.schemas.procedure import ProcedureCreate, ProcedureUpdate
from app.models.procedure import Procedure, ProcedureStep
from app.ai.sop_retriever import SOPRetriever

class ProcedureService:
    def get_procedures(self, db: Session, skip: int = 0, limit: int = 100) -> List[Procedure]:
        return procedure_repository.get_all(db, skip=skip, limit=limit)

    def get_procedure(self, db: Session, proc_id: int) -> Optional[Procedure]:
        return procedure_repository.get(db, proc_id)

    def create_procedure(self, db: Session, proc_in: ProcedureCreate) -> Procedure:
        data = proc_in.dict()
        steps_data = data.pop("steps", [])

        proc = procedure_repository.create(db, data)
        steps_objs = []
        for step in steps_data:
            s_obj = ProcedureStep(procedure_id=proc.id, **step)
            db.add(s_obj)
            steps_objs.append(s_obj)
        db.commit()
        db.refresh(proc)

        # Index into vector retriever
        SOPRetriever.index_procedure(proc.id, proc.procedure_code, proc.title, proc.description or "", proc.category, steps_objs)

        return proc

    def update_procedure(self, db: Session, proc_id: int, proc_in: ProcedureCreate) -> Optional[Procedure]:
        proc = procedure_repository.get(db, proc_id)
        if not proc:
            return None
        data = proc_in.dict()
        steps_data = data.pop("steps", [])

        # Update base procedure attributes
        proc = procedure_repository.update(db, proc, data)

        # Replace existing steps
        db.query(ProcedureStep).filter(ProcedureStep.procedure_id == proc.id).delete()
        steps_objs = []
        for step in steps_data:
            s_obj = ProcedureStep(procedure_id=proc.id, **step)
            db.add(s_obj)
            steps_objs.append(s_obj)
        db.commit()
        db.refresh(proc)

        # Re-index into vector retriever
        SOPRetriever.index_procedure(proc.id, proc.procedure_code, proc.title, proc.description or "", proc.category, steps_objs)

        return proc

procedure_service = ProcedureService()
