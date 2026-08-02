from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.issue_repository import issue_repository
from app.schemas.issue import IssueCreate, IssueUpdate, IssueStatusUpdate
from app.models.issue import Issue, IssueComment, IssueAttachment

class IssueService:
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

issue_service = IssueService()
