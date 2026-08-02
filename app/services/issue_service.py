from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.issue_repository import issue_repository
from app.schemas.issue import IssueCreate, IssueUpdate, IssueStatusUpdate, DuplicateCheckRequest
from app.models.issue import Issue, IssueComment, IssueAttachment
from app.services.duplicate_detector import duplicate_engine

class IssueService:
    def check_duplicates(self, db: Session, req: DuplicateCheckRequest) -> Dict[str, Any]:
        # Fetch current open or in-progress issues
        all_issues = issue_repository.get_multi(db, limit=500)
        open_issues = [i for i in all_issues if i.status in ["Open", "In Progress", "Waiting"]]
        return duplicate_engine.check_duplicate(
            new_title=req.title,
            new_description=req.description,
            new_machine_id=req.machine_id,
            open_issues=open_issues,
            threshold=req.threshold
        )

    def get_issue(self, db: Session, issue_id: int) -> Optional[Issue]:
        return issue_repository.get(db, issue_id)

    def get_issues(
        self,
        db: Session,
        machine_id: Optional[int] = None,
        department: Optional[str] = None,
        priority: Optional[str] = None,
        worker_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Issue]:
        return issue_repository.get_multi(
            db,
            machine_id=machine_id,
            department=department,
            priority=priority,
            worker_id=worker_id,
            status=status,
            skip=skip,
            limit=limit
        )

    def create_issue(self, db: Session, issue_in: IssueCreate) -> Issue:
        return issue_repository.create(db, issue_in)

    def update_issue(self, db: Session, issue_id: int, issue_in: IssueUpdate) -> Optional[Issue]:
        issue = issue_repository.get(db, issue_id)
        if not issue:
            return None
        return issue_repository.update(db, issue, issue_in.dict(exclude_unset=True))

    def update_issue_status(self, db: Session, issue_id: int, status_in: IssueStatusUpdate) -> Optional[Issue]:
        issue = issue_repository.get(db, issue_id)
        if not issue:
            return None
        return issue_repository.update_status(
            db,
            issue=issue,
            new_status=status_in.status,
            changed_by_id=status_in.changed_by_id,
            notes=status_in.notes,
            resolution=status_in.resolution
        )

    def add_comment(self, db: Session, issue_id: int, comment_text: str, author_name: str, author_id: Optional[int] = None) -> Optional[IssueComment]:
        issue = issue_repository.get(db, issue_id)
        if not issue:
            return None
        return issue_repository.add_comment(db, issue_id, author_name, comment_text, author_id)

    def add_attachment(self, db: Session, issue_id: int, file_name: str, file_url: str, file_type: str = "document") -> Optional[IssueAttachment]:
        issue = issue_repository.get(db, issue_id)
        if not issue:
            return None
        return issue_repository.add_attachment(db, issue_id, file_name, file_url, file_type)

    def assign_owner(self, db: Session, issue_id: int, assigned_worker_id: int, changed_by_id: Optional[int] = None, notes: Optional[str] = None) -> Optional[Issue]:
        issue = issue_repository.get(db, issue_id)
        if not issue:
            return None
        return issue_repository.assign_owner(db, issue, assigned_worker_id, changed_by_id, notes)

    def transfer_ownership(self, db: Session, issue_id: int, new_owner_id: int, reason: str, changed_by_id: Optional[int] = None) -> Optional[Issue]:
        issue = issue_repository.get(db, issue_id)
        if not issue:
            return None
        return issue_repository.transfer_ownership(db, issue, new_owner_id, reason, changed_by_id)

    def reassign_department(
        self, db: Session, issue_id: int, new_department: str, reason: str, new_owner_id: Optional[int] = None, new_supervisor_id: Optional[int] = None, changed_by_id: Optional[int] = None
    ) -> Optional[Issue]:
        issue = issue_repository.get(db, issue_id)
        if not issue:
            return None
        return issue_repository.reassign_department(
            db, issue, new_department=new_department, reason=reason, new_owner_id=new_owner_id, new_supervisor_id=new_supervisor_id, changed_by_id=changed_by_id
        )

    def escalate(
        self, db: Session, issue_id: int, reason: str, new_supervisor_id: Optional[int] = None, new_owner_id: Optional[int] = None, changed_by_id: Optional[int] = None, boost_priority: bool = True
    ) -> Optional[Issue]:
        issue = issue_repository.get(db, issue_id)
        if not issue:
            return None
        return issue_repository.escalate(
            db, issue, reason=reason, new_supervisor_id=new_supervisor_id, new_owner_id=new_owner_id, changed_by_id=changed_by_id, boost_priority=boost_priority
        )

    def close_issue(self, db: Session, issue_id: int, resolution: str, changed_by_id: Optional[int] = None, notes: Optional[str] = None) -> Optional[Issue]:
        issue = issue_repository.get(db, issue_id)
        if not issue:
            return None
        return issue_repository.close_issue(db, issue, resolution=resolution, changed_by_id=changed_by_id, notes=notes)

issue_service = IssueService()
