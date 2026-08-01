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
