from typing import Optional
from sqlalchemy.orm import Session
from app.models.procedure import Procedure
from app.repositories.base import BaseRepository

class ProcedureRepository(BaseRepository[Procedure]):
    def __init__(self):
        super().__init__(Procedure)

    def get_by_code(self, db: Session, code: str) -> Optional[Procedure]:
        return db.query(Procedure).filter(Procedure.procedure_code == code).first()

procedure_repository = ProcedureRepository()
