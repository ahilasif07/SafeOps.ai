import os

files = {}

# 1. UTILS & DB
files["app/utils/config.py"] = '''
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SafeOps AI - Enterprise Industrial Safety System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./safeops.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "safeops-ai-super-secret-industrial-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    BLOCK_RISK_THRESHOLD: float = 65.0
    SUPERVISOR_APPROVAL_THRESHOLD: float = 40.0
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    class Config:
        case_sensitive = True

settings = Settings()
'''

files["app/utils/logger.py"] = '''
import logging
import sys

def setup_logger(name: str = "safeops"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s")
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger

logger = setup_logger()
'''

files["app/database/session.py"] = '''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.utils.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''

# 2. MODELS
files["app/models/base.py"] = '''
import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
'''

files["app/models/worker.py"] = '''
from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Worker(BaseModel):
    __tablename__ = "workers"

    worker_code = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    role = Column(String(50), nullable=False, default="TECHNICIAN") # TECHNICIAN, SUPERVISOR, SAFETY_OFFICER, MANAGER
    department = Column(String(100), nullable=False, default="MAINTENANCE")
    clearance_level = Column(Integer, nullable=False, default=1) # 1 to 5
    is_active = Column(Boolean, default=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    training_records = relationship("TrainingRecord", back_populates="worker", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="worker")
    incidents = relationship("Incident", back_populates="worker")
    supervisor_approvals = relationship("SupervisorApproval", back_populates="supervisor")
'''

files["app/models/machine.py"] = '''
from sqlalchemy import Column, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
import datetime
from app.models.base import BaseModel

class Machine(BaseModel):
    __tablename__ = "machines"

    machine_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="OPERATIONAL") # OPERATIONAL, MAINTENANCE, LOCKED_OUT, HAZARDOUS
    last_maintenance_at = Column(DateTime, default=datetime.datetime.utcnow)
    safety_rating = Column(Float, default=95.0) # 0 to 100
    requires_loto = Column(Boolean, default=True)

    tasks = relationship("Task", back_populates="machine")
    incidents = relationship("Incident", back_populates="machine")
    sensor_readings = relationship("SensorReading", back_populates="machine", cascade="all, delete-orphan")
'''

files["app/models/procedure.py"] = '''
from sqlalchemy import Column, String, Boolean, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Procedure(BaseModel):
    __tablename__ = "procedures"

    procedure_code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, default="ELECTRICAL") # ELECTRICAL, MECHANICAL, CHEMICAL, HYDRAULIC
    required_clearance_level = Column(Integer, default=1, nullable=False)
    is_approved = Column(Boolean, default=True, nullable=False)
    version = Column(String(20), default="1.0", nullable=False)

    steps = relationship("ProcedureStep", back_populates="procedure", cascade="all, delete-orphan", order_by="ProcedureStep.step_number")
    tasks = relationship("Task", back_populates="procedure")

class ProcedureStep(BaseModel):
    __tablename__ = "procedure_steps"

    procedure_id = Column(Integer, ForeignKey("procedures.id", ondelete="CASCADE"), nullable=False)
    step_number = Column(Integer, nullable=False)
    title = Column(String(150), nullable=False)
    instruction = Column(Text, nullable=False)
    hazard_level = Column(String(20), default="LOW", nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    requires_supervisor_signoff = Column(Boolean, default=False)
    required_ppe = Column(String(200), default="Safety Glasses, Steel Toe Boots")

    procedure = relationship("Procedure", back_populates="steps")
'''

files["app/models/task.py"] = '''
from sqlalchemy import Column, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Task(BaseModel):
    __tablename__ = "tasks"

    task_code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    procedure_id = Column(Integer, ForeignKey("procedures.id"), nullable=False)
    status = Column(String(30), default="PENDING", nullable=False) # PENDING, APPROVED, IN_PROGRESS, COMPLETED, BLOCKED, CANCELLED
    risk_score = Column(Float, default=0.0, nullable=False) # 0 to 100
    risk_level = Column(String(20), default="LOW", nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    block_reason = Column(Text, nullable=True)

    worker = relationship("Worker", back_populates="tasks")
    machine = relationship("Machine", back_populates="tasks")
    procedure = relationship("Procedure", back_populates="tasks")
    history = relationship("TaskHistory", back_populates="task", cascade="all, delete-orphan", order_by="TaskHistory.created_at.desc()")
    supervisor_approvals = relationship("SupervisorApproval", back_populates="task", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="task")

class TaskHistory(BaseModel):
    __tablename__ = "task_history"

    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    previous_status = Column(String(30), nullable=False)
    new_status = Column(String(30), nullable=False)
    changed_by_worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    notes = Column(Text, nullable=True)

    task = relationship("Task", back_populates="history")
'''

files["app/models/certification.py"] = '''
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Certification(BaseModel):
    __tablename__ = "certifications"

    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(120), nullable=False)
    description = Column(String(255), nullable=True)
    validity_months = Column(Integer, default=24, nullable=False)
    issuing_body = Column(String(100), default="OSHA Safety Institute")

    training_records = relationship("TrainingRecord", back_populates="certification", cascade="all, delete-orphan")

class TrainingRecord(BaseModel):
    __tablename__ = "training_records"

    worker_id = Column(Integer, ForeignKey("workers.id", ondelete="CASCADE"), nullable=False)
    certification_id = Column(Integer, ForeignKey("certifications.id", ondelete="CASCADE"), nullable=False)
    issued_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    is_valid = Column(Boolean, default=True, nullable=False)

    worker = relationship("Worker", back_populates="training_records")
    certification = relationship("Certification", back_populates="training_records")
'''

files["app/models/incident.py"] = '''
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from app.models.base import BaseModel

class Incident(BaseModel):
    __tablename__ = "incidents"

    incident_code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="MEDIUM", nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    reported_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    resolution_status = Column(String(30), default="OPEN", nullable=False) # OPEN, UNDER_INVESTIGATION, RESOLVED, CLOSED

    machine = relationship("Machine", back_populates="incidents")
    worker = relationship("Worker", back_populates="incidents")
    task = relationship("Task", back_populates="incidents")
'''

files["app/models/supervisor.py"] = '''
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class SupervisorApproval(BaseModel):
    __tablename__ = "supervisor_approvals"

    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    supervisor_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    status = Column(String(20), default="PENDING", nullable=False) # PENDING, APPROVED, REJECTED
    comments = Column(Text, nullable=True)
    decided_at = Column(DateTime, nullable=True)

    task = relationship("Task", back_populates="supervisor_approvals")
    supervisor = relationship("Worker", back_populates="supervisor_approvals")
'''

files["app/models/sensor.py"] = '''
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from app.models.base import BaseModel

class SensorReading(BaseModel):
    __tablename__ = "sensor_readings"

    machine_id = Column(Integer, ForeignKey("machines.id", ondelete="CASCADE"), nullable=False)
    sensor_type = Column(String(50), nullable=False) # TEMPERATURE, PRESSURE, VIBRATION, TOXIC_GAS, EMERGENCY_STOP
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False) # C, PSI, mm/s, ppm, BOOL
    is_anomaly = Column(Boolean, default=False, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    machine = relationship("Machine", back_populates="sensor_readings")
'''

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.strip() + "\n")

print(f"Written {len(files)} files successfully.")
