from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.worker import WorkerOut
from app.schemas.machine import MachineOut

class IssueCommentBase(BaseModel):
    comment_text: str
    author_name: Optional[str] = "System User"
    author_id: Optional[int] = None

class IssueCommentCreate(IssueCommentBase):
    pass

class IssueCommentOut(IssueCommentBase):
    id: int
    issue_id: int
    created_at: datetime
    updated_at: datetime
    author: Optional[WorkerOut] = None

    class Config:
        from_attributes = True


class IssueAttachmentBase(BaseModel):
    file_name: str
    file_url: str
    file_type: Optional[str] = "document"

class IssueAttachmentCreate(IssueAttachmentBase):
    pass

class IssueAttachmentOut(IssueAttachmentBase):
    id: int
    issue_id: int
    uploaded_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class IssueStatusHistoryOut(BaseModel):
    id: int
    issue_id: int
    changed_by_id: Optional[int] = None
    from_status: str
    to_status: str
    notes: Optional[str] = None
    changed_at: datetime
    changed_by: Optional[WorkerOut] = None

    class Config:
        from_attributes = True


class IssueOwnershipHistoryOut(BaseModel):
    id: int
    issue_id: int
    action_type: str
    previous_owner_id: Optional[int] = None
    new_owner_id: Optional[int] = None
    previous_supervisor_id: Optional[int] = None
    new_supervisor_id: Optional[int] = None
    previous_department: Optional[str] = None
    new_department: Optional[str] = None
    changed_by_id: Optional[int] = None
    reason_notes: Optional[str] = None
    changed_at: datetime
    
    previous_owner: Optional[WorkerOut] = None
    new_owner: Optional[WorkerOut] = None
    previous_supervisor: Optional[WorkerOut] = None
    new_supervisor: Optional[WorkerOut] = None
    changed_by: Optional[WorkerOut] = None

    class Config:
        from_attributes = True


class AssignOwnerRequest(BaseModel):
    assigned_worker_id: int
    changed_by_id: Optional[int] = None
    notes: Optional[str] = None


class TransferOwnershipRequest(BaseModel):
    new_owner_id: int
    changed_by_id: Optional[int] = None
    reason: str


class ReassignDepartmentRequest(BaseModel):
    new_department: str
    new_owner_id: Optional[int] = None
    new_supervisor_id: Optional[int] = None
    changed_by_id: Optional[int] = None
    reason: str


class EscalateIssueRequest(BaseModel):
    new_supervisor_id: Optional[int] = None
    new_owner_id: Optional[int] = None
    changed_by_id: Optional[int] = None
    reason: str
    boost_priority: Optional[bool] = True


class CloseIssueRequest(BaseModel):
    resolution: str
    changed_by_id: Optional[int] = None
    notes: Optional[str] = None


class IssueBase(BaseModel):
    title: str
    description: str
    machine_id: Optional[int] = None
    department: str = "PLANT_OPS"
    priority: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    status: str = "Open"  # Open, In Progress, Waiting, Resolved, Closed
    reporter_id: Optional[int] = None
    assigned_worker_id: Optional[int] = None
    assigned_supervisor_id: Optional[int] = None
    due_date: Optional[datetime] = None
    resolution: Optional[str] = None
    resolution_time: Optional[datetime] = None

class IssueCreate(BaseModel):
    issue_code: Optional[str] = None
    title: str
    description: str
    machine_id: Optional[int] = None
    department: Optional[str] = "PLANT_OPS"
    priority: Optional[str] = "MEDIUM"
    status: Optional[str] = "Open"
    reporter_id: Optional[int] = None
    assigned_worker_id: Optional[int] = None
    assigned_supervisor_id: Optional[int] = None
    due_date: Optional[datetime] = None

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    machine_id: Optional[int] = None
    department: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_worker_id: Optional[int] = None
    assigned_supervisor_id: Optional[int] = None
    due_date: Optional[datetime] = None
    resolution: Optional[str] = None

class IssueStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
    changed_by_id: Optional[int] = None
    resolution: Optional[str] = None

class DuplicateCheckRequest(BaseModel):
    title: str
    description: str
    machine_id: Optional[int] = None
    threshold: Optional[float] = 0.55

class DuplicateMatch(BaseModel):
    issue_id: int
    issue_code: str
    title: str
    description: str
    machine_id: Optional[int] = None
    machine_name: Optional[str] = "General Facility"
    status: str
    priority: str
    created_at: str
    similarity_score: float
    similarity_percentage: int

class DuplicateCheckResponse(BaseModel):
    is_possible_duplicate: bool
    threshold_used: float
    existing_issue_id: Optional[int] = None
    existing_issue_code: Optional[str] = None
    similarity_score: float = 0.0
    similarity_percentage: int = 0
    top_match: Optional[DuplicateMatch] = None
    all_matches: List[DuplicateMatch] = []

class IssueOut(IssueBase):
    id: int
    issue_code: str
    created_at: datetime
    updated_at: datetime
    machine: Optional[MachineOut] = None
    reporter: Optional[WorkerOut] = None
    assigned_worker: Optional[WorkerOut] = None
    assigned_supervisor: Optional[WorkerOut] = None
    comments: List[IssueCommentOut] = []
    attachments: List[IssueAttachmentOut] = []
    status_history: List[IssueStatusHistoryOut] = []
    ownership_history: List[IssueOwnershipHistoryOut] = []

    class Config:
        from_attributes = True
