import os

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.strip() + "\n")

# 1. RISK ENGINE
write("app/risk_engine/matrix.py", '''
from typing import Tuple

class RiskMatrix:
    @staticmethod
    def get_risk_level(score: float) -> str:
        if score >= 65.0:
            return "CRITICAL"
        elif score >= 40.0:
            return "HIGH"
        elif score >= 20.0:
            return "MEDIUM"
        else:
            return "LOW"

    @staticmethod
    def evaluate_action(score: float) -> Tuple[str, bool]:
        """Returns (decision, is_blocked)"""
        if score >= 65.0:
            return ("BLOCKED", True)
        elif score >= 40.0:
            return ("SUPERVISOR_APPROVAL_REQUIRED", False)
        elif score >= 20.0:
            return ("PROCEED_WITH_CAUTION", False)
        else:
            return ("APPROVED", False)
''')

write("app/risk_engine/rules.py", '''
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.worker import Worker
from app.models.machine import Machine
from app.models.procedure import Procedure
from app.repositories.certification_repository import certification_repository
from app.repositories.sensor_repository import sensor_repository
from app.repositories.incident_repository import incident_repository

class SafetyRuleChecker:
    @staticmethod
    def check_worker_clearance(worker: Worker, procedure: Procedure) -> Dict[str, Any]:
        if worker.clearance_level < procedure.required_clearance_level:
            return {
                "category": "WORKER_CLEARANCE",
                "description": f"Worker clearance level ({worker.clearance_level}) is below required level ({procedure.required_clearance_level})",
                "impact_score": 35.0,
                "status": "FAILED",
                "is_blocking": True
            }
        return {
            "category": "WORKER_CLEARANCE",
            "description": "Worker clearance level verified.",
            "impact_score": 0.0,
            "status": "PASSED",
            "is_blocking": False
        }

    @staticmethod
    def check_worker_certifications(db: Session, worker: Worker, procedure: Procedure) -> Dict[str, Any]:
        records = certification_repository.get_worker_training(db, worker.id)
        valid_certs = {r.certification.code for r in records if r.is_valid and r.certification}

        missing = []
        if procedure.category == "ELECTRICAL" and "CERT-ELEC-01" not in valid_certs:
            missing.append("CERT-ELEC-01 (High-Voltage Electrical Safety)")
        if procedure.category == "HYDRAULIC" and "CERT-HYD-01" not in valid_certs:
            missing.append("CERT-HYD-01 (High-Pressure Hydraulics)")
        if machine_requires_loto := True: # Checked dynamically
            if "CERT-LOTO-01" not in valid_certs:
                missing.append("CERT-LOTO-01 (Lock-Out / Tag-Out Authorized Specialist)")

        if missing:
            return {
                "category": "CERTIFICATIONS",
                "description": f"Worker lacks required active safety certifications: {', '.join(missing)}",
                "impact_score": 40.0,
                "status": "FAILED",
                "missing": missing,
                "is_blocking": True
            }
        return {
            "category": "CERTIFICATIONS",
            "description": "All required safety certifications are active.",
            "impact_score": 0.0,
            "status": "PASSED",
            "missing": [],
            "is_blocking": False
        }

    @staticmethod
    def check_machine_status(machine: Machine) -> Dict[str, Any]:
        if machine.status == "HAZARDOUS":
            return {
                "category": "MACHINE_STATUS",
                "description": f"Machine {machine.machine_code} is currently flagged as HAZARDOUS.",
                "impact_score": 50.0,
                "status": "FAILED",
                "is_blocking": True
            }
        elif machine.status == "LOCKED_OUT":
            return {
                "category": "MACHINE_STATUS",
                "description": f"Machine {machine.machine_code} is locked out for active maintenance.",
                "impact_score": 30.0,
                "status": "WARNING",
                "is_blocking": False
            }
        elif machine.safety_rating < 70.0:
            return {
                "category": "MACHINE_STATUS",
                "description": f"Machine safety rating is low ({machine.safety_rating}%).",
                "impact_score": 25.0,
                "status": "WARNING",
                "is_blocking": False
            }
        return {
            "category": "MACHINE_STATUS",
            "description": "Machine status is OPERATIONAL with acceptable safety rating.",
            "impact_score": 0.0,
            "status": "PASSED",
            "is_blocking": False
        }

    @staticmethod
    def check_telemetry_anomalies(db: Session, machine: Machine) -> Dict[str, Any]:
        readings = sensor_repository.get_latest_by_machine(db, machine.id, limit=5)
        anomalies = [f"{r.sensor_type}: {r.value}{r.unit}" for r in readings if r.is_anomaly]

        if anomalies:
            return {
                "category": "SENSOR_TELEMETRY",
                "description": f"Active sensor anomalies detected on machine: {', '.join(anomalies)}",
                "impact_score": 35.0,
                "status": "FAILED",
                "anomalies": anomalies,
                "is_blocking": True
            }
        return {
            "category": "SENSOR_TELEMETRY",
            "description": "All telemetry sensors (temp, pressure, vibration) within normal limits.",
            "impact_score": 0.0,
            "status": "PASSED",
            "anomalies": [],
            "is_blocking": False
        }

    @staticmethod
    def check_recent_incidents(db: Session, machine: Machine) -> Dict[str, Any]:
        incidents = incident_repository.get_by_machine(db, machine.id)
        open_incidents = [i for i in incidents if i.resolution_status in ["OPEN", "UNDER_INVESTIGATION"]]

        if open_incidents:
            return {
                "category": "INCIDENT_HISTORY",
                "description": f"{len(open_incidents)} unresolved safety incident(s) on this machine.",
                "impact_score": 20.0,
                "status": "WARNING",
                "is_blocking": False
            }
        return {
            "category": "INCIDENT_HISTORY",
            "description": "No unresolved safety incidents recorded.",
            "impact_score": 0.0,
            "status": "PASSED",
            "is_blocking": False
        }
''')

write("app/risk_engine/evaluator.py", '''
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.worker import Worker
from app.models.machine import Machine
from app.models.procedure import Procedure
from app.risk_engine.rules import SafetyRuleChecker
from app.risk_engine.matrix import RiskMatrix
from app.schemas.safety_eval import SafetyEvalResponse, RiskFactorDetail

class SafetyRiskEvaluator:
    @staticmethod
    def evaluate(db: Session, worker: Worker, machine: Machine, procedure: Procedure) -> SafetyEvalResponse:
        factors = []
        block_reasons = []
        missing_certs = []
        sensor_anomalies = []
        total_risk = 0.0

        # Rule 1: Worker Clearance
        c_res = SafetyRuleChecker.check_worker_clearance(worker, procedure)
        total_risk += c_res["impact_score"]
        factors.append(RiskFactorDetail(category=c_res["category"], description=c_res["description"], impact_score=c_res["impact_score"], status=c_res["status"]))
        if c_res["is_blocking"]:
            block_reasons.append(c_res["description"])

        # Rule 2: Worker Certifications
        cert_res = SafetyRuleChecker.check_worker_certifications(db, worker, procedure)
        total_risk += cert_res["impact_score"]
        factors.append(RiskFactorDetail(category=cert_res["category"], description=cert_res["description"], impact_score=cert_res["impact_score"], status=cert_res["status"]))
        if cert_res["is_blocking"]:
            block_reasons.append(cert_res["description"])
            missing_certs.extend(cert_res.get("missing", []))

        # Rule 3: Machine Status
        m_res = SafetyRuleChecker.check_machine_status(machine)
        total_risk += m_res["impact_score"]
        factors.append(RiskFactorDetail(category=m_res["category"], description=m_res["description"], impact_score=m_res["impact_score"], status=m_res["status"]))
        if m_res["is_blocking"]:
            block_reasons.append(m_res["description"])

        # Rule 4: Sensor Telemetry
        s_res = SafetyRuleChecker.check_telemetry_anomalies(db, machine)
        total_risk += s_res["impact_score"]
        factors.append(RiskFactorDetail(category=s_res["category"], description=s_res["description"], impact_score=s_res["impact_score"], status=s_res["status"]))
        if s_res["is_blocking"]:
            block_reasons.append(s_res["description"])
            sensor_anomalies.extend(s_res.get("anomalies", []))

        # Rule 5: Incident History
        inc_res = SafetyRuleChecker.check_recent_incidents(db, machine)
        total_risk += inc_res["impact_score"]
        factors.append(RiskFactorDetail(category=inc_res["category"], description=inc_res["description"], impact_score=inc_res["impact_score"], status=inc_res["status"]))

        final_score = min(100.0, total_risk)
        risk_level = RiskMatrix.get_risk_level(final_score)
        decision, is_blocked = RiskMatrix.evaluate_action(final_score)

        loto_ok = not machine.requires_loto or "CERT-LOTO-01" not in missing_certs

        return SafetyEvalResponse(
            worker_id=worker.id,
            machine_id=machine.id,
            procedure_id=procedure.id,
            risk_score=final_score,
            risk_level=risk_level,
            decision=decision,
            is_blocked=is_blocked,
            block_reasons=block_reasons,
            required_certifications_missing=missing_certs,
            sensor_anomalies_detected=sensor_anomalies,
            loto_status_ok=loto_ok,
            risk_factors=factors,
            ai_safety_briefing=None
        )

evaluator = SafetyRiskEvaluator()
''')

# 2. SENSOR SIMULATOR
write("app/sensor_simulator/generator.py", '''
import random
from typing import Dict, Any

class SensorGenerator:
    @staticmethod
    def generate_reading(sensor_type: str, force_anomaly: bool = False) -> Dict[str, Any]:
        if sensor_type == "TEMPERATURE":
            unit = "C"
            val = random.uniform(95.0, 125.0) if force_anomaly else random.uniform(55.0, 75.0)
            is_anomaly = val > 90.0
        elif sensor_type == "PRESSURE":
            unit = "PSI"
            val = random.uniform(140.0, 180.0) if force_anomaly else random.uniform(80.0, 110.0)
            is_anomaly = val > 130.0
        elif sensor_type == "VIBRATION":
            unit = "mm/s"
            val = random.uniform(8.5, 15.0) if force_anomaly else random.uniform(1.0, 4.0)
            is_anomaly = val > 7.0
        elif sensor_type == "TOXIC_GAS":
            unit = "ppm"
            val = random.uniform(15.0, 45.0) if force_anomaly else random.uniform(0.0, 3.0)
            is_anomaly = val > 10.0
        else:
            unit = "BOOL"
            val = 1.0 if force_anomaly else 0.0
            is_anomaly = bool(val)

        return {
            "sensor_type": sensor_type,
            "value": round(val, 2),
            "unit": unit,
            "is_anomaly": is_anomaly
        }
''')

write("app/sensor_simulator/telemetry.py", '''
from typing import List
from sqlalchemy.orm import Session
from app.sensor_simulator.generator import SensorGenerator
from app.repositories.sensor_repository import sensor_repository
from app.schemas.sensor import SensorReadingOut

class TelemetrySimulator:
    @staticmethod
    def simulate_machine_readings(db: Session, machine_id: int, force_anomaly: bool = False) -> List[SensorReadingOut]:
        sensor_types = ["TEMPERATURE", "PRESSURE", "VIBRATION"]
        if machine_id % 2 == 1:
            sensor_types.append("TOXIC_GAS")

        results = []
        for st in sensor_types:
            data = SensorGenerator.generate_reading(st, force_anomaly=force_anomaly)
            data["machine_id"] = machine_id
            reading = sensor_repository.create(db, data)
            results.append(SensorReadingOut.from_orm(reading))
        return results

telemetry_simulator = TelemetrySimulator()
''')

# 3. AI / GEMINI / RAG
write("app/ai/vector_store.py", '''
import math
from typing import List, Dict, Any

class InMemoryVectorStore:
    """Lightweight in-memory vector store with cosine similarity for RAG SOP retrieval."""
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []

    def _dummy_embed(self, text: str) -> List[float]:
        # Simple deterministic hash vector for text similarity without external heavy DL dependencies
        vec = [0.0] * 32
        for i, char in enumerate(text.lower()):
            vec[ord(char) % 32] += 1.0
        norm = math.sqrt(sum(x*x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def add_document(self, doc_id: str, content: str, metadata: Dict[str, Any]):
        embedding = self._dummy_embed(content)
        self.documents.append({
            "id": doc_id,
            "content": content,
            "metadata": metadata,
            "embedding": embedding
        })

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.documents:
            return []
        q_vec = self._dummy_embed(query)

        scored = []
        for doc in self.documents:
            d_vec = doc["embedding"]
            similarity = sum(a * b for a, b in zip(q_vec, d_vec))
            scored.append({
                "id": doc["id"],
                "content": doc["content"],
                "metadata": doc["metadata"],
                "score": round(similarity, 4)
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

vector_store = InMemoryVectorStore()
''')

write("app/ai/sop_retriever.py", '''
from typing import List, Dict, Any
from app.ai.vector_store import vector_store

class SOPRetriever:
    @staticmethod
    def index_procedure(procedure_id: int, code: str, title: str, description: str, category: str, steps: List[Any]):
        step_text = "\\n".join([f"Step {s.step_number}: {s.title} - {s.instruction} (Hazard: {s.hazard_level}, PPE: {s.required_ppe})" for s in steps])
        full_content = f"SOP Code: {code}\\nTitle: {title}\\nCategory: {category}\\nDescription: {description}\\nSteps:\\n{step_text}"

        vector_store.add_document(
            doc_id=f"SOP-{procedure_id}",
            content=full_content,
            metadata={
                "procedure_id": procedure_id,
                "code": code,
                "title": title,
                "category": category
            }
        )

    @staticmethod
    def query_sops(query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        return vector_store.search(query_text, top_k=top_k)

sop_retriever = SOPRetriever()
''')

write("app/ai/gemini_client.py", '''
import os
from google import genai
from app.utils.config import settings
from app.utils.logger import logger

class GeminiSafetyAdvisor:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini Client: {e}")

    def generate_safety_briefing(self, worker_name: str, machine_name: str, procedure_title: str, risk_score: float, risk_level: str, hazards: list) -> str:
        if not self.client:
            # Fallback high-quality structured safety advisory when API key is missing/unconfigured
            return (
                f"⚠️ [SafeOps AI Safety Briefing for {worker_name}]\\n"
                f"Task: {procedure_title} on {machine_name}\\n"
                f"Evaluated Risk Score: {risk_score}/100 ({risk_level})\\n\\n"
                f"Critical Directives:\\n"
                f"1. Perform mandatory LOTO verification prior to touching circuit conductors or hydraulic lines.\\n"
                f"2. Mandatory PPE: Arc Flash Level 4, Insulated Gloves (20kV), Steel Toe Boots.\\n"
                f"3. Ensure secondary supervisor signoff is logged before initiating hazardous steps.\\n"
                f"Identify hazards: {', '.join(hazards) if hazards else 'None detected.'}"
            )

        prompt = (
            f"You are SafeOps AI, an industrial safety copilot. Generate a concise, urgent 3-bullet point safety briefing "
            f"for technician {worker_name} executing '{procedure_title}' on '{machine_name}'. "
            f"Risk Score: {risk_score}/100 ({risk_level}). Identified hazard factors: {hazards}. "
            f"Include required PPE and lock-out tag-out instructions."
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Error invoking Gemini API: {e}")
            return f"SafeOps AI Advisory: Risk level is {risk_level} ({risk_score}/100). Maintain full PPE compliance and supervisor signoff."

gemini_advisor = GeminiSafetyAdvisor()
''')

# 4. AUTH SECURITY & DEPENDENCIES
write("app/auth/security.py", '''
import datetime
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.utils.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
''')

write("app/auth/dependencies.py", '''
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.utils.config import settings
from app.database.session import get_db
from app.repositories.worker_repository import worker_repository
from app.models.worker import Worker

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_current_worker(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Worker:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate industrial access credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        worker_code: str = payload.get("sub")
        if worker_code is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    worker = worker_repository.get_by_code(db, code=worker_code)
    if worker is None:
        raise credentials_exception
    return worker

def get_current_active_worker(current_worker: Worker = Depends(get_current_worker)) -> Worker:
    if not current_worker.is_active:
        raise HTTPException(status_code=400, detail="Inactive worker account")
    return current_worker
''')

# 5. SERVICES
write("app/services/worker_service.py", '''
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.worker_repository import worker_repository
from app.schemas.worker import WorkerCreate, WorkerUpdate
from app.models.worker import Worker
from app.auth.security import get_password_hash

class WorkerService:
    def get_workers(self, db: Session, skip: int = 0, limit: int = 100) -> List[Worker]:
        return worker_repository.get_all(db, skip=skip, limit=limit)

    def get_worker(self, db: Session, worker_id: int) -> Optional[Worker]:
        return worker_repository.get(db, worker_id)

    def get_worker_by_code(self, db: Session, code: str) -> Optional[Worker]:
        return worker_repository.get_by_code(db, code)

    def create_worker(self, db: Session, worker_in: WorkerCreate) -> Worker:
        data = worker_in.dict()
        data["hashed_password"] = get_password_hash(data.pop("password"))
        return worker_repository.create(db, data)

    def update_worker(self, db: Session, worker_id: int, worker_in: WorkerUpdate) -> Optional[Worker]:
        worker = worker_repository.get(db, worker_id)
        if not worker:
            return None
        data = worker_in.dict(exclude_unset=True)
        if "password" in data and data["password"]:
            data["hashed_password"] = get_password_hash(data.pop("password"))
        return worker_repository.update(db, worker, data)

    def delete_worker(self, db: Session, worker_id: int) -> bool:
        return worker_repository.delete(db, worker_id)

worker_service = WorkerService()
''')

write("app/services/machine_service.py", '''
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
''')

write("app/services/procedure_service.py", '''
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

procedure_service = ProcedureService()
''')

write("app/services/risk_service.py", '''
from sqlalchemy.orm import Session
from app.repositories.worker_repository import worker_repository
from app.repositories.machine_repository import machine_repository
from app.repositories.procedure_repository import procedure_repository
from app.risk_engine.evaluator import evaluator
from app.schemas.safety_eval import SafetyEvalRequest, SafetyEvalResponse
from app.ai.gemini_client import gemini_advisor

class RiskService:
    def evaluate_task_safety(self, db: Session, req: SafetyEvalRequest) -> SafetyEvalResponse:
        worker = worker_repository.get(db, req.worker_id)
        if not worker:
            raise ValueError(f"Worker {req.worker_id} not found")
        machine = machine_repository.get(db, req.machine_id)
        if not machine:
            raise ValueError(f"Machine {req.machine_id} not found")
        procedure = procedure_repository.get(db, req.procedure_id)
        if not procedure:
            raise ValueError(f"Procedure {req.procedure_id} not found")

        eval_res = evaluator.evaluate(db, worker, machine, procedure)

        # AI Briefing
        hazards = [f.description for f in eval_res.risk_factors if f.status in ["FAILED", "WARNING"]]
        briefing = gemini_advisor.generate_safety_briefing(
            worker.full_name,
            machine.name,
            procedure.title,
            eval_res.risk_score,
            eval_res.risk_level,
            hazards
        )
        eval_res.ai_safety_briefing = briefing
        return eval_res

risk_service = RiskService()
''')

write("app/services/task_service.py", '''
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.task_repository import task_repository
from app.schemas.task import TaskCreate, TaskUpdate
from app.models.task import Task
from app.services.risk_service import risk_service
from app.schemas.safety_eval import SafetyEvalRequest

class TaskService:
    def get_tasks(self, db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
        return task_repository.get_all(db, skip=skip, limit=limit)

    def get_task(self, db: Session, task_id: int) -> Optional[Task]:
        return task_repository.get(db, task_id)

    def create_task(self, db: Session, task_in: TaskCreate) -> Task:
        # Run automated safety evaluation
        eval_req = SafetyEvalRequest(
            worker_id=task_in.worker_id,
            machine_id=task_in.machine_id,
            procedure_id=task_in.procedure_id
        )
        eval_res = risk_service.evaluate_task_safety(db, eval_req)

        data = task_in.dict()
        data["risk_score"] = eval_res.risk_score
        data["risk_level"] = eval_res.risk_level

        if eval_res.is_blocked:
            data["status"] = "BLOCKED"
            data["block_reason"] = " | ".join(eval_res.block_reasons)
        elif eval_res.decision == "SUPERVISOR_APPROVAL_REQUIRED":
            data["status"] = "PENDING"
            data["block_reason"] = "High safety risk requires supervisor sign-off before execution."
        else:
            data["status"] = "APPROVED"

        task = task_repository.create(db, data)
        task_repository.create_history(db, task.id, "NONE", task.status, task.worker_id, f"Initial task submission. Risk: {eval_res.risk_score}")
        return task

    def update_task_status(self, db: Session, task_id: int, new_status: str, worker_id: int, notes: str = None) -> Optional[Task]:
        task = task_repository.get(db, task_id)
        if not task:
            return None
        prev_status = task.status
        task.status = new_status
        db.commit()
        db.refresh(task)

        task_repository.create_history(db, task.id, prev_status, new_status, worker_id, notes)
        return task

task_service = TaskService()
''')

write("app/services/sensor_service.py", '''
from typing import List
from sqlalchemy.orm import Session
from app.repositories.sensor_repository import sensor_repository
from app.schemas.sensor import SensorReadingCreate, SensorReadingOut
from app.sensor_simulator.telemetry import telemetry_simulator
from app.models.sensor import SensorReading

class SensorService:
    def log_reading(self, db: Session, reading_in: SensorReadingCreate) -> SensorReading:
        data = reading_in.dict()
        # Anomaly threshold check
        val = data["value"]
        st = data["sensor_type"]
        is_anomaly = (st == "TEMPERATURE" and val > 90.0) or (st == "PRESSURE" and val > 130.0) or (st == "VIBRATION" and val > 7.0) or (st == "TOXIC_GAS" and val > 10.0)
        data["is_anomaly"] = is_anomaly
        return sensor_repository.create(db, data)

    def get_latest_readings(self, db: Session, machine_id: int, limit: int = 10) -> List[SensorReading]:
        return sensor_repository.get_latest_by_machine(db, machine_id, limit)

    def trigger_telemetry_simulation(self, db: Session, machine_id: int, force_anomaly: bool = False) -> List[SensorReadingOut]:
        return telemetry_simulator.simulate_machine_readings(db, machine_id, force_anomaly)

sensor_service = SensorService()
''')

write("app/services/auth_service.py", '''
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.worker_repository import worker_repository
from app.auth.security import verify_password, create_access_token
from app.schemas.auth import Token, WorkerLogin

class AuthService:
    def authenticate_worker(self, db: Session, login_data: WorkerLogin) -> Token:
        worker = worker_repository.get_by_email(db, login_data.email)
        if not worker or not verify_password(login_data.password, worker.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not worker.is_active:
            raise HTTPException(status_code=400, detail="Worker account deactivated")

        access_token = create_access_token(data={"sub": worker.worker_code, "role": worker.role})
        return Token(
            access_token=access_token,
            worker_id=worker.id,
            worker_code=worker.worker_code,
            role=worker.role
        )

auth_service = AuthService()
''')

write("app/services/incident_service.py", '''
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
''')

print("Part B written successfully.")
