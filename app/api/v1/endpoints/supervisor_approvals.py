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
