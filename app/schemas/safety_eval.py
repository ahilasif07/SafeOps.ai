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
