import os

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.strip() + "\n")

# 1. SCHEMAS
write("app/schemas/auth.py", '''
from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    worker_id: int
    worker_code: str
    role: str

class TokenData(BaseModel):
    worker_code: Optional[str] = None
    role: Optional[str] = None

class WorkerLogin(BaseModel):
    email: EmailStr
    password: str
''')

write("app/schemas/worker.py", '''
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class WorkerBase(BaseModel):
    worker_code: str
    full_name: str
    email: EmailStr
    role: str = "TECHNICIAN"
    department: str = "MAINTENANCE"
    clearance_level: int = 1
    is_active: bool = True

class WorkerCreate(WorkerBase):
    password: str

class WorkerUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    department: Optional[str] = None
    clearance_level: Optional[int] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class WorkerOut(WorkerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
''')

write("app/schemas/machine.py", '''
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MachineBase(BaseModel):
    machine_code: str
    name: str
    model: str
    location: str
    status: str = "OPERATIONAL"
    safety_rating: float = 95.0
    requires_loto: bool = True

class MachineCreate(MachineBase):
    pass

class MachineUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    safety_rating: Optional[float] = None
    requires_loto: Optional[bool] = None
    last_maintenance_at: Optional[datetime] = None

class MachineOut(MachineBase):
    id: int
    last_maintenance_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
''')

write("app/schemas/procedure.py", '''
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProcedureStepBase(BaseModel):
    step_number: int
    title: str
    instruction: str
    hazard_level: str = "LOW"
    requires_supervisor_signoff: bool = False
    required_ppe: str = "Safety Glasses, Steel Toe Boots"

class ProcedureStepCreate(ProcedureStepBase):
    pass

class ProcedureStepOut(ProcedureStepBase):
    id: int
    procedure_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProcedureBase(BaseModel):
    procedure_code: str
    title: str
    description: Optional[str] = None
    category: str = "ELECTRICAL"
    required_clearance_level: int = 1
    is_approved: bool = True
    version: str = "1.0"

class ProcedureCreate(ProcedureBase):
    steps: List[ProcedureStepCreate] = []

class ProcedureUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    required_clearance_level: Optional[int] = None
    is_approved: Optional[bool] = None
    version: Optional[str] = None

class ProcedureOut(ProcedureBase):
    id: int
    steps: List[ProcedureStepOut] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
''')

write("app/schemas/task.py", '''
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.worker import WorkerOut
from app.schemas.machine import MachineOut
from app.schemas.procedure import ProcedureOut

class TaskBase(BaseModel):
    task_code: str
    title: str
    description: Optional[str] = None
    worker_id: int
    machine_id: int
    procedure_id: int

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    block_reason: Optional[str] = None

class TaskHistoryOut(BaseModel):
    id: int
    task_id: int
    previous_status: str
    new_status: str
    changed_by_worker_id: Optional[int]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class TaskOut(TaskBase):
    id: int
    status: str
    risk_score: float
    risk_level: str
    block_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    worker: Optional[WorkerOut] = None
    machine: Optional[MachineOut] = None
    procedure: Optional[ProcedureOut] = None
    history: List[TaskHistoryOut] = []

    class Config:
        from_attributes = True
''')

write("app/schemas/certification.py", '''
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.worker import WorkerOut

class CertificationBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    validity_months: int = 24
    issuing_body: str = "OSHA Safety Institute"

class CertificationCreate(CertificationBase):
    pass

class CertificationOut(CertificationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TrainingRecordCreate(BaseModel):
    worker_id: int
    certification_id: int
    issued_date: datetime
    expiry_date: datetime
    is_valid: bool = True

class TrainingRecordOut(BaseModel):
    id: int
    worker_id: int
    certification_id: int
    issued_date: datetime
    expiry_date: datetime
    is_valid: bool
    certification: Optional[CertificationOut] = None

    class Config:
        from_attributes = True
''')

write("app/schemas/incident.py", '''
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class IncidentBase(BaseModel):
    incident_code: str
    title: str
    description: str
    severity: str = "MEDIUM"
    machine_id: int
    worker_id: Optional[int] = None
    task_id: Optional[int] = None

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    resolution_status: Optional[str] = None

class IncidentOut(IncidentBase):
    id: int
    reported_at: datetime
    resolution_status: str
    created_at: datetime

    class Config:
        from_attributes = True
''')

write("app/schemas/supervisor.py", '''
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SupervisorApprovalCreate(BaseModel):
    task_id: int
    supervisor_id: int
    comments: Optional[str] = None

class SupervisorApprovalUpdate(BaseModel):
    status: str
    comments: Optional[str] = None

class SupervisorApprovalOut(BaseModel):
    id: int
    task_id: int
    supervisor_id: int
    status: str
    comments: Optional[str]
    decided_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
''')

write("app/schemas/sensor.py", '''
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SensorReadingCreate(BaseModel):
    machine_id: int
    sensor_type: str
    value: float
    unit: str

class SensorReadingOut(SensorReadingCreate):
    id: int
    is_anomaly: bool
    timestamp: datetime

    class Config:
        from_attributes = True
''')

write("app/schemas/safety_eval.py", '''
from pydantic import BaseModel
from typing import List, Optional

class SafetyEvalRequest(BaseModel):
    worker_id: int
    machine_id: int
    procedure_id: int

class RiskFactorDetail(BaseModel):
    category: str
    description: str
    impact_score: float
    status: str

class SafetyEvalResponse(BaseModel):
    worker_id: int
    machine_id: int
    procedure_id: int
    risk_score: float
    risk_level: str
    decision: str
    is_blocked: bool
    block_reasons: List[str]
    required_certifications_missing: List[str]
    sensor_anomalies_detected: List[str]
    loto_status_ok: bool
    risk_factors: List[RiskFactorDetail]
    ai_safety_briefing: Optional[str] = None
''')

# 2. REPOSITORIES
write("app/repositories/base.py", '''
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ModelType, obj_in: dict) -> ModelType:
        for field, value in obj_in.items():
            if value is not None:
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> bool:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False
''')

write("app/repositories/worker_repository.py", '''
from typing import Optional
from sqlalchemy.orm import Session
from app.models.worker import Worker
from app.repositories.base import BaseRepository

class WorkerRepository(BaseRepository[Worker]):
    def __init__(self):
        super().__init__(Worker)

    def get_by_email(self, db: Session, email: str) -> Optional[Worker]:
        return db.query(Worker).filter(Worker.email == email).first()

    def get_by_code(self, db: Session, code: str) -> Optional[Worker]:
        return db.query(Worker).filter(Worker.worker_code == code).first()

worker_repository = WorkerRepository()
''')

write("app/repositories/machine_repository.py", '''
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
''')

write("app/repositories/procedure_repository.py", '''
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
''')

write("app/repositories/task_repository.py", '''
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.task import Task, TaskHistory
from app.repositories.base import BaseRepository

class TaskRepository(BaseRepository[Task]):
    def __init__(self):
        super().__init__(Task)

    def get_by_code(self, db: Session, code: str) -> Optional[Task]:
        return db.query(Task).filter(Task.task_code == code).first()

    def get_by_worker(self, db: Session, worker_id: int) -> List[Task]:
        return db.query(Task).filter(Task.worker_id == worker_id).all()

    def create_history(self, db: Session, task_id: int, prev_status: str, new_status: str, worker_id: int, notes: str = None):
        hist = TaskHistory(
            task_id=task_id,
            previous_status=prev_status,
            new_status=new_status,
            changed_by_worker_id=worker_id,
            notes=notes
        )
        db.add(hist)
        db.commit()

task_repository = TaskRepository()
''')

write("app/repositories/certification_repository.py", '''
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.certification import Certification, TrainingRecord
from app.repositories.base import BaseRepository

class CertificationRepository(BaseRepository[Certification]):
    def __init__(self):
        super().__init__(Certification)

    def get_by_code(self, db: Session, code: str) -> Optional[Certification]:
        return db.query(Certification).filter(Certification.code == code).first()

    def get_worker_training(self, db: Session, worker_id: int) -> List[TrainingRecord]:
        return db.query(TrainingRecord).filter(TrainingRecord.worker_id == worker_id, TrainingRecord.is_valid == True).all()

certification_repository = CertificationRepository()
''')

write("app/repositories/incident_repository.py", '''
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
''')

write("app/repositories/sensor_repository.py", '''
from typing import List
from sqlalchemy.orm import Session
from app.models.sensor import SensorReading
from app.repositories.base import BaseRepository

class SensorRepository(BaseRepository[SensorReading]):
    def __init__(self):
        super().__init__(SensorReading)

    def get_latest_by_machine(self, db: Session, machine_id: int, limit: int = 10) -> List[SensorReading]:
        return db.query(SensorReading).filter(SensorReading.machine_id == machine_id).order_by(SensorReading.timestamp.desc()).limit(limit).all()

sensor_repository = SensorRepository()
''')

write("app/repositories/supervisor_repository.py", '''
from typing import Optional
from sqlalchemy.orm import Session
from app.models.supervisor import SupervisorApproval
from app.repositories.base import BaseRepository

class SupervisorRepository(BaseRepository[SupervisorApproval]):
    def __init__(self):
        super().__init__(SupervisorApproval)

    def get_by_task(self, db: Session, task_id: int) -> Optional[SupervisorApproval]:
        return db.query(SupervisorApproval).filter(SupervisorApproval.task_id == task_id).first()

supervisor_repository = SupervisorRepository()
''')

print("Part A written successfully.")
