import os

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.strip() + "\n")

# 1. INIT DB SCRIPT
write("app/database/init_db.py", '''
import datetime
from sqlalchemy.orm import Session
from app.database.session import engine, SessionLocal
from app.models.base import Base
from app.models.worker import Worker
from app.models.machine import Machine
from app.models.procedure import Procedure, ProcedureStep
from app.models.certification import Certification, TrainingRecord
from app.models.incident import Incident
from app.models.sensor import SensorReading
from app.models.task import Task
from app.auth.security import get_password_hash
from app.ai.sop_retriever import SOPRetriever
from app.utils.logger import logger

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Worker).first():
        logger.info("Database already seeded.")
        db.close()
        return

    logger.info("Seeding initial SafeOps AI industrial dataset...")

    # 1. Certifications
    cert_elec = Certification(code="CERT-ELEC-01", name="High-Voltage Electrical Safety", validity_months=24, issuing_body="OSHA Safety Board")
    cert_loto = Certification(code="CERT-LOTO-01", name="Lock-Out / Tag-Out Authorized Specialist", validity_months=12, issuing_body="National Safety Council")
    cert_hazmat = Certification(code="CERT-HAZMAT-01", name="Hazmat & Chemical Handling", validity_months=24, issuing_body="EPA Industrial Safety")
    cert_hyd = Certification(code="CERT-HYD-01", name="High-Pressure Hydraulics", validity_months=36, issuing_body="Fluid Power Society")

    db.add_all([cert_elec, cert_loto, cert_hazmat, cert_hyd])
    db.commit()

    # 2. Workers
    pass_hash = get_password_hash("SafeOpsPass2026!")
    w1 = Worker(worker_code="WRK-1001", full_name="John Doe", email="john.doe@safeops.io", role="TECHNICIAN", department="ELECTRICAL", clearance_level=3, is_active=True, hashed_password=pass_hash)
    w2 = Worker(worker_code="WRK-1002", full_name="Sarah Connor", email="sarah.c@safeops.io", role="SUPERVISOR", department="PLANT_OPS", clearance_level=5, is_active=True, hashed_password=pass_hash)
    w3 = Worker(worker_code="WRK-1003", full_name="Mike Vance", email="mike.vance@safeops.io", role="TECHNICIAN", department="MECHANICAL", clearance_level=1, is_active=True, hashed_password=pass_hash)
    w4 = Worker(worker_code="WRK-1004", full_name="Alex Mercer", email="alex.m@safeops.io", role="SAFETY_OFFICER", department="SAFETY_DEPT", clearance_level=4, is_active=True, hashed_password=pass_hash)

    db.add_all([w1, w2, w3, w4])
    db.commit()

    # 3. Training Records
    now = datetime.datetime.utcnow()
    tr1 = TrainingRecord(worker_id=w1.id, certification_id=cert_elec.id, issued_date=now - datetime.timedelta(days=100), expiry_date=now + datetime.timedelta(days=600), is_valid=True)
    tr2 = TrainingRecord(worker_id=w1.id, certification_id=cert_loto.id, issued_date=now - datetime.timedelta(days=50), expiry_date=now + datetime.timedelta(days=300), is_valid=True)
    tr3 = TrainingRecord(worker_id=w3.id, certification_id=cert_loto.id, issued_date=now - datetime.timedelta(days=400), expiry_date=now - datetime.timedelta(days=35), is_valid=False) # Expired!

    db.add_all([tr1, tr2, tr3])
    db.commit()

    # 4. Machines
    m1 = Machine(machine_code="MCH-TURB-01", name="Main Gas Turbine Alpha", model="Siemens SGT-800", location="Sector A - Powerhouse", status="OPERATIONAL", safety_rating=92.5, requires_loto=True)
    m2 = Machine(machine_code="MCH-PRESS-04", name="Hydraulic Stamping Press 4", model="Schuler 1000T", location="Sector B - Fabrication", status="MAINTENANCE", safety_rating=84.0, requires_loto=True)
    m3 = Machine(machine_code="MCH-CHEM-02", name="Chemical Reactor Vessel 2", model="Pfaudler 5000L", location="Sector C - Chemical Processing", status="HAZARDOUS", safety_rating=65.0, requires_loto=True)

    db.add_all([m1, m2, m3])
    db.commit()

    # 5. Procedures & Steps
    p1 = Procedure(procedure_code="SOP-ELEC-401", title="High-Voltage Transformer Maintenance & Inspection", description="Standard procedure for isolating, testing, and replacing transformer coils.", category="ELECTRICAL", required_clearance_level=3, is_approved=True, version="2.1")
    db.add(p1)
    db.commit()

    s1_1 = ProcedureStep(procedure_id=p1.id, step_number=1, title="Verify Lock-Out / Tag-Out (LOTO)", instruction="De-energize main 13.8kV circuit breaker and place master padlocks.", hazard_level="CRITICAL", requires_supervisor_signoff=True, required_ppe="Arc Flash Suit Level 4, Insulated Gloves 20kV")
    s1_2 = ProcedureStep(procedure_id=p1.id, step_number=2, title="Grounding Rod Discharge", instruction="Attach grounding cable to discharge remaining capacitive charge.", hazard_level="HIGH", requires_supervisor_signoff=False, required_ppe="Safety Glasses, Insulated Gloves 20kV")
    s1_3 = ProcedureStep(procedure_id=p1.id, step_number=3, title="Insulation Oil Sampling", instruction="Extract 500ml of oil from the bottom valve for breakdown voltage testing.", hazard_level="MEDIUM", requires_supervisor_signoff=False, required_ppe="Nitrile Gloves, Respirator")

    p2 = Procedure(procedure_code="SOP-HYD-202", title="Hydraulic Cylinder Seal Replacement", description="Procedure for depressurizing and replacing piston rod seals on stamping presses.", category="HYDRAULIC", required_clearance_level=2, is_approved=True, version="1.0")
    db.add(p2)
    db.commit()

    s2_1 = ProcedureStep(procedure_id=p2.id, step_number=1, title="Bleed Hydraulic Line Pressure", instruction="Open bleed valve V-102 until accumulator pressure reads 0 PSI.", hazard_level="HIGH", requires_supervisor_signoff=True, required_ppe="Face Shield, Heavy Leather Gloves")
    s2_2 = ProcedureStep(procedure_id=p2.id, step_number=2, title="Remove Cylinder End Cap", instruction="Unbolt 12 M24 retaining bolts in star pattern.", hazard_level="MEDIUM", requires_supervisor_signoff=False, required_ppe="Steel Toe Boots, Safety Glasses")

    db.add_all([s1_1, s1_2, s1_3, s2_1, s2_2])
    db.commit()

    # Index procedures in vector retriever
    SOPRetriever.index_procedure(p1.id, p1.procedure_code, p1.title, p1.description, p1.category, [s1_1, s1_2, s1_3])
    SOPRetriever.index_procedure(p2.id, p2.procedure_code, p2.title, p2.description, p2.category, [s2_1, s2_2])

    # 6. Sensor Readings
    sr1 = SensorReading(machine_id=m1.id, sensor_type="TEMPERATURE", value=68.5, unit="C", is_anomaly=False, timestamp=now)
    sr2 = SensorReading(machine_id=m1.id, sensor_type="VIBRATION", value=2.1, unit="mm/s", is_anomaly=False, timestamp=now)
    sr3 = SensorReading(machine_id=m3.id, sensor_type="TOXIC_GAS", value=18.4, unit="ppm", is_anomaly=True, timestamp=now)
    sr4 = SensorReading(machine_id=m3.id, sensor_type="TEMPERATURE", value=102.3, unit="C", is_anomaly=True, timestamp=now)

    db.add_all([sr1, sr2, sr3, sr4])
    db.commit()

    # 7. Incidents
    inc1 = Incident(incident_code="INC-2026-001", title="Over-pressurization Alarm on Reactor 2", description="Pressure spiked to 145 PSI during chemical batching process.", severity="HIGH", machine_id=m3.id, reported_at=now - datetime.timedelta(days=5), resolution_status="UNDER_INVESTIGATION")
    db.add(inc1)
    db.commit()

    db.close()
    logger.info("SafeOps AI Database initialization & seeding completed successfully.")
''')

# 2. ENDPOINTS
write("app/api/v1/endpoints/auth.py", '''
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.auth import Token, WorkerLogin
from app.schemas.worker import WorkerOut
from app.services.auth_service import auth_service
from app.auth.dependencies import get_current_active_worker
from app.models.worker import Worker

router = APIRouter()

@router.post("/login", response_model=Token, summary="Authenticate worker and return JWT token")
def login(login_data: WorkerLogin, db: Session = Depends(get_db)):
    return auth_service.authenticate_worker(db, login_data)

@router.get("/me", response_model=WorkerOut, summary="Get current logged in worker profile")
def read_me(current_worker: Worker = Depends(get_current_active_worker)):
    return current_worker
''')

write("app/api/v1/endpoints/workers.py", '''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.worker import WorkerOut, WorkerCreate, WorkerUpdate
from app.services.worker_service import worker_service

router = APIRouter()

@router.get("/", response_model=List[WorkerOut], summary="List all industrial workers")
def get_workers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return worker_service.get_workers(db, skip=skip, limit=limit)

@router.post("/", response_model=WorkerOut, status_code=status.HTTP_201_CREATED, summary="Create a new worker profile")
def create_worker(worker_in: WorkerCreate, db: Session = Depends(get_db)):
    existing = worker_service.get_worker_by_code(db, worker_in.worker_code)
    if existing:
        raise HTTPException(status_code=400, detail="Worker code already exists")
    return worker_service.create_worker(db, worker_in)

@router.get("/{worker_id}", response_model=WorkerOut, summary="Get worker by ID")
def get_worker(worker_id: int, db: Session = Depends(get_db)):
    worker = worker_service.get_worker(db, worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker

@router.put("/{worker_id}", response_model=WorkerOut, summary="Update worker details")
def update_worker(worker_id: int, worker_in: WorkerUpdate, db: Session = Depends(get_db)):
    worker = worker_service.update_worker(db, worker_id, worker_in)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker

@router.delete("/{worker_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deactivate or delete worker")
def delete_worker(worker_id: int, db: Session = Depends(get_db)):
    success = worker_service.delete_worker(db, worker_id)
    if not success:
        raise HTTPException(status_code=404, detail="Worker not found")
    return None
''')

write("app/api/v1/endpoints/machines.py", '''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.machine import MachineOut, MachineCreate, MachineUpdate
from app.services.machine_service import machine_service

router = APIRouter()

@router.get("/", response_model=List[MachineOut], summary="List all industrial machines")
def get_machines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return machine_service.get_machines(db, skip=skip, limit=limit)

@router.post("/", response_model=MachineOut, status_code=status.HTTP_201_CREATED, summary="Register a new machine")
def create_machine(machine_in: MachineCreate, db: Session = Depends(get_db)):
    return machine_service.create_machine(db, machine_in)

@router.get("/{machine_id}", response_model=MachineOut, summary="Get machine by ID")
def get_machine(machine_id: int, db: Session = Depends(get_db)):
    machine = machine_service.get_machine(db, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@router.put("/{machine_id}", response_model=MachineOut, summary="Update machine status or ratings")
def update_machine(machine_id: int, machine_in: MachineUpdate, db: Session = Depends(get_db)):
    machine = machine_service.update_machine(db, machine_id, machine_in)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine
''')

write("app/api/v1/endpoints/procedures.py", '''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.procedure import ProcedureOut, ProcedureCreate, ProcedureUpdate
from app.services.procedure_service import procedure_service

router = APIRouter()

@router.get("/", response_model=List[ProcedureOut], summary="List all Standard Operating Procedures (SOPs)")
def get_procedures(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return procedure_service.get_procedures(db, skip=skip, limit=limit)

@router.post("/", response_model=ProcedureOut, status_code=status.HTTP_201_CREATED, summary="Create approved SOP with hazard steps")
def create_procedure(procedure_in: ProcedureCreate, db: Session = Depends(get_db)):
    return procedure_service.create_procedure(db, procedure_in)

@router.get("/{procedure_id}", response_model=ProcedureOut, summary="Get SOP by ID")
def get_procedure(procedure_id: int, db: Session = Depends(get_db)):
    proc = procedure_service.get_procedure(db, procedure_id)
    if not proc:
        raise HTTPException(status_code=404, detail="Procedure not found")
    return proc
''')

write("app/api/v1/endpoints/tasks.py", '''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.task import TaskOut, TaskCreate, TaskUpdate
from app.services.task_service import task_service

router = APIRouter()

@router.get("/", response_model=List[TaskOut], summary="List all maintenance tasks & safety status")
def get_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return task_service.get_tasks(db, skip=skip, limit=limit)

@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED, summary="Submit maintenance task order (Evaluates safety risk)")
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    try:
        return task_service.create_task(db, task_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{task_id}", response_model=TaskOut, summary="Get task by ID")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task order not found")
    return task

@router.put("/{task_id}/status", response_model=TaskOut, summary="Update task status (e.g., APPROVED, COMPLETED)")
def update_task_status(task_id: int, status_name: str, worker_id: int, notes: str = None, db: Session = Depends(get_db)):
    task = task_service.update_task_status(db, task_id, status_name, worker_id, notes)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
''')

write("app/api/v1/endpoints/certifications.py", '''
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
''')

write("app/api/v1/endpoints/incidents.py", '''
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
''')

write("app/api/v1/endpoints/supervisor_approvals.py", '''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database.session import get_db
from app.models.supervisor import SupervisorApproval
from app.schemas.supervisor import SupervisorApprovalOut, SupervisorApprovalCreate, SupervisorApprovalUpdate
from app.repositories.task_repository import task_repository

router = APIRouter()

@router.get("/", response_model=List[SupervisorApprovalOut], summary="List pending supervisor approvals")
def get_approvals(db: Session = Depends(get_db)):
    return db.query(SupervisorApproval).all()

@router.post("/", response_model=SupervisorApprovalOut, status_code=status.HTTP_201_CREATED, summary="Request supervisor approval for high-risk task")
def request_approval(app_in: SupervisorApprovalCreate, db: Session = Depends(get_db)):
    approval = SupervisorApproval(**app_in.dict(), status="PENDING")
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval

@router.put("/{approval_id}", response_model=SupervisorApprovalOut, summary="Supervisor decides approval (APPROVED or REJECTED)")
def decide_approval(approval_id: int, decision: SupervisorApprovalUpdate, db: Session = Depends(get_db)):
    approval = db.query(SupervisorApproval).filter(SupervisorApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")

    approval.status = decision.status
    approval.comments = decision.comments
    approval.decided_at = datetime.utcnow()
    db.commit()

    # If approved, update task status to APPROVED
    if decision.status == "APPROVED":
        task = task_repository.get(db, approval.task_id)
        if task:
            task.status = "APPROVED"
            db.commit()

    db.refresh(approval)
    return approval
''')

write("app/api/v1/endpoints/sensor_readings.py", '''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.sensor import SensorReadingOut, SensorReadingCreate
from app.services.sensor_service import sensor_service

router = APIRouter()

@router.post("/log", response_model=SensorReadingOut, summary="Log sensor reading from machine IoT gateway")
def log_reading(reading_in: SensorReadingCreate, db: Session = Depends(get_db)):
    return sensor_service.log_reading(db, reading_in)

@router.get("/machine/{machine_id}", response_model=List[SensorReadingOut], summary="Get latest telemetry readings for a machine")
def get_machine_telemetry(machine_id: int, limit: int = 10, db: Session = Depends(get_db)):
    return sensor_service.get_latest_readings(db, machine_id, limit)

@router.post("/simulate/{machine_id}", response_model=List[SensorReadingOut], summary="Trigger IoT telemetry simulation for machine")
def simulate_telemetry(machine_id: int, force_anomaly: bool = False, db: Session = Depends(get_db)):
    return sensor_service.trigger_telemetry_simulation(db, machine_id, force_anomaly)
''')

write("app/api/v1/endpoints/safety_eval.py", '''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.safety_eval import SafetyEvalRequest, SafetyEvalResponse
from app.services.risk_service import risk_service

router = APIRouter()

@router.post("/evaluate", response_model=SafetyEvalResponse, summary="Evaluate task safety & calculate composite risk score")
def evaluate_safety(req: SafetyEvalRequest, db: Session = Depends(get_db)):
    try:
        return risk_service.evaluate_task_safety(db, req)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
''')

write("app/api/v1/endpoints/sop_ai.py", '''
from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.ai.sop_retriever import SOPRetriever

router = APIRouter()

@router.get("/search", summary="Vector semantic search for SOPs & safety guidelines")
def search_sops(q: str, top_k: int = 3):
    return SOPRetriever.query_sops(q, top_k=top_k)
''')

# 3. API V1 ROUTER
write("app/api/v1/router.py", '''
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, workers, machines, procedures, tasks,
    certifications, incidents, supervisor_approvals,
    sensor_readings, safety_eval, sop_ai
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(workers.router, prefix="/workers", tags=["Workers & Credentials"])
api_router.include_router(machines.router, prefix="/machines", tags=["Industrial Machinery"])
api_router.include_router(procedures.router, prefix="/procedures", tags=["Standard Operating Procedures (SOPs)"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Maintenance Work Orders"])
api_router.include_router(certifications.router, prefix="/certifications", tags=["Safety Certifications"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents & Near Misses"])
api_router.include_router(supervisor_approvals.router, prefix="/approvals", tags=["Supervisor Sign-offs"])
api_router.include_router(sensor_readings.router, prefix="/sensors", tags=["IoT Telemetry"])
api_router.include_router(safety_eval.router, prefix="/safety", tags=["Risk Engine & Safety Evaluation"])
api_router.include_router(sop_ai.router, prefix="/sop-ai", tags=["AI Copilot & Vector SOP Search"])
''')

# 4. MAIN FASTAPI ENTRYPOINT
write("app/main.py", '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.config import settings
from app.api.v1.router import api_router
from app.database.init_db import init_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health"])
def root_health():
    return {
        "status": "online",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "documentation": "/docs"
    }
''')

print("Part C written successfully.")
