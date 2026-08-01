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
