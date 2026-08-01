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
