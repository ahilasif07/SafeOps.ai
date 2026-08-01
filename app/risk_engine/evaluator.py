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
