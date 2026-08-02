from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.schemas.issue import (
    IssueOut, IssueCreate, IssueUpdate, IssueStatusUpdate,
    IssueCommentOut, IssueCommentCreate, IssueAttachmentOut, IssueAttachmentCreate,
    DuplicateCheckRequest, DuplicateCheckResponse,
    AssignOwnerRequest, TransferOwnershipRequest, ReassignDepartmentRequest, EscalateIssueRequest, CloseIssueRequest
)
from app.services.issue_service import issue_service

router = APIRouter()

@router.post("/check-duplicates", response_model=DuplicateCheckResponse, summary="Check for duplicate open issues using fuzzy engine")
def check_duplicate_issues(req: DuplicateCheckRequest, db: Session = Depends(get_db)):
    return issue_service.check_duplicates(db, req)

@router.get("/", response_model=List[IssueOut], summary="List issues with filters")
def list_issues(
    machine_id: Optional[int] = Query(None, description="Filter by Machine ID"),
    department: Optional[str] = Query(None, description="Filter by Department"),
    priority: Optional[str] = Query(None, description="Filter by Priority (LOW, MEDIUM, HIGH, CRITICAL)"),
    worker_id: Optional[int] = Query(None, description="Filter by Assigned Worker ID"),
    status: Optional[str] = Query(None, description="Filter by Status (Open, In Progress, Waiting, Resolved, Closed)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return issue_service.get_issues(
        db,
        machine_id=machine_id,
        department=department,
        priority=priority,
        worker_id=worker_id,
        status=status,
        skip=skip,
        limit=limit
    )

@router.post("/", response_model=IssueOut, status_code=status.HTTP_201_CREATED, summary="Create new issue")
def create_issue(issue_in: IssueCreate, db: Session = Depends(get_db)):
    return issue_service.create_issue(db, issue_in)

@router.get("/{issue_id}", response_model=IssueOut, summary="Get issue details by ID")
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = issue_service.get_issue(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue

@router.put("/{issue_id}", response_model=IssueOut, summary="Update issue details")
def update_issue(issue_id: int, issue_in: IssueUpdate, db: Session = Depends(get_db)):
    updated = issue_service.update_issue(db, issue_id, issue_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Issue not found")
    return updated

@router.put("/{issue_id}/status", response_model=IssueOut, summary="Update issue status")
def update_issue_status(issue_id: int, status_in: IssueStatusUpdate, db: Session = Depends(get_db)):
    updated = issue_service.update_issue_status(db, issue_id, status_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Issue not found")
    return updated

@router.post("/{issue_id}/comments", response_model=IssueCommentOut, summary="Add comment to issue")
def add_issue_comment(issue_id: int, comment_in: IssueCommentCreate, db: Session = Depends(get_db)):
    comment = issue_service.add_comment(
        db,
        issue_id=issue_id,
        comment_text=comment_in.comment_text,
        author_name=comment_in.author_name or "System User",
        author_id=comment_in.author_id
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Issue not found")
    return comment

@router.post("/{issue_id}/attachments", response_model=IssueAttachmentOut, summary="Add attachment to issue")
def add_issue_attachment(issue_id: int, attachment_in: IssueAttachmentCreate, db: Session = Depends(get_db)):
    attachment = issue_service.add_attachment(
        db,
        issue_id=issue_id,
        file_name=attachment_in.file_name,
        file_url=attachment_in.file_url,
        file_type=attachment_in.file_type or "document"
    )
    if not attachment:
        raise HTTPException(status_code=404, detail="Issue not found")
    return attachment

@router.post("/{issue_id}/assign-owner", response_model=IssueOut, summary="Assign owner to issue")
def assign_issue_owner(issue_id: int, req: AssignOwnerRequest, db: Session = Depends(get_db)):
    updated = issue_service.assign_owner(
        db, issue_id=issue_id, assigned_worker_id=req.assigned_worker_id, changed_by_id=req.changed_by_id, notes=req.notes
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Issue not found")
    return updated

@router.post("/{issue_id}/transfer-ownership", response_model=IssueOut, summary="Transfer issue ownership to another worker")
def transfer_issue_ownership(issue_id: int, req: TransferOwnershipRequest, db: Session = Depends(get_db)):
    updated = issue_service.transfer_ownership(
        db, issue_id=issue_id, new_owner_id=req.new_owner_id, reason=req.reason, changed_by_id=req.changed_by_id
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Issue not found")
    return updated

@router.post("/{issue_id}/reassign-department", response_model=IssueOut, summary="Reassign department for issue")
def reassign_issue_department(issue_id: int, req: ReassignDepartmentRequest, db: Session = Depends(get_db)):
    updated = issue_service.reassign_department(
        db,
        issue_id=issue_id,
        new_department=req.new_department,
        reason=req.reason,
        new_owner_id=req.new_owner_id,
        new_supervisor_id=req.new_supervisor_id,
        changed_by_id=req.changed_by_id
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Issue not found")
    return updated

@router.post("/{issue_id}/escalate", response_model=IssueOut, summary="Escalate issue to higher supervisor or priority")
def escalate_issue(issue_id: int, req: EscalateIssueRequest, db: Session = Depends(get_db)):
    updated = issue_service.escalate(
        db,
        issue_id=issue_id,
        reason=req.reason,
        new_supervisor_id=req.new_supervisor_id,
        new_owner_id=req.new_owner_id,
        changed_by_id=req.changed_by_id,
        boost_priority=req.boost_priority if req.boost_priority is not None else True
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Issue not found")
    return updated

@router.post("/{issue_id}/close", response_model=IssueOut, summary="Close issue with technical resolution")
def close_issue(issue_id: int, req: CloseIssueRequest, db: Session = Depends(get_db)):
    updated = issue_service.close_issue(
        db, issue_id=issue_id, resolution=req.resolution, changed_by_id=req.changed_by_id, notes=req.notes
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Issue not found")
    return updated
