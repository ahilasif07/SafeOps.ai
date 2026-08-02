from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.issue import Issue, IssueComment, IssueAttachment, IssueStatusHistory, IssueOwnershipHistory
from app.schemas.issue import IssueCreate, IssueUpdate
import datetime

class IssueRepository:
    def get(self, db: Session, issue_id: int) -> Optional[Issue]:
        return db.query(Issue).filter(Issue.id == issue_id).first()

    def get_by_code(self, db: Session, issue_code: str) -> Optional[Issue]:
        return db.query(Issue).filter(Issue.issue_code == issue_code).first()

    def get_multi(
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
        query = db.query(Issue)
        if machine_id is not None:
            query = query.filter(Issue.machine_id == machine_id)
        if department and department.strip():
            query = query.filter(Issue.department.ilike(f"%{department.strip()}%"))
        if priority and priority.strip():
            query = query.filter(Issue.priority == priority.strip())
        if worker_id is not None:
            query = query.filter(Issue.assigned_worker_id == worker_id)
        if status and status.strip():
            query = query.filter(Issue.status == status.strip())
        return query.order_by(Issue.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, db: Session, issue_in: IssueCreate) -> Issue:
        code = issue_in.issue_code or f"ISS-{int(datetime.datetime.utcnow().timestamp())}"
        issue = Issue(
            issue_code=code,
            title=issue_in.title,
            description=issue_in.description,
            machine_id=issue_in.machine_id,
            department=issue_in.department or "PLANT_OPS",
            priority=issue_in.priority or "MEDIUM",
            status=issue_in.status or "Open",
            reporter_id=issue_in.reporter_id,
            assigned_worker_id=issue_in.assigned_worker_id,
            assigned_supervisor_id=issue_in.assigned_supervisor_id,
            due_date=issue_in.due_date
        )
        db.add(issue)
        db.commit()
        db.refresh(issue)

        # Initial status history
        history = IssueStatusHistory(
            issue_id=issue.id,
            changed_by_id=issue_in.reporter_id,
            from_status="CREATED",
            to_status=issue.status,
            notes="Issue opened in system."
        )
        db.add(history)

        # Initial ownership history
        ownership = IssueOwnershipHistory(
            issue_id=issue.id,
            action_type="INITIAL_CREATION",
            new_owner_id=issue.assigned_worker_id,
            new_supervisor_id=issue.assigned_supervisor_id,
            new_department=issue.department,
            changed_by_id=issue_in.reporter_id,
            reason_notes="Issue logged and initial ownership assigned."
        )
        db.add(ownership)

        db.commit()
        db.refresh(issue)

        return issue

    def assign_owner(
        self, db: Session, issue: Issue, assigned_worker_id: int, changed_by_id: Optional[int] = None, notes: Optional[str] = None
    ) -> Issue:
        old_owner = issue.assigned_worker_id
        issue.assigned_worker_id = assigned_worker_id
        if issue.status == "Open":
            issue.status = "In Progress"

        ownership = IssueOwnershipHistory(
            issue_id=issue.id,
            action_type="ASSIGN_OWNER",
            previous_owner_id=old_owner,
            new_owner_id=assigned_worker_id,
            previous_supervisor_id=issue.assigned_supervisor_id,
            new_supervisor_id=issue.assigned_supervisor_id,
            previous_department=issue.department,
            new_department=issue.department,
            changed_by_id=changed_by_id,
            reason_notes=notes or f"Owner assigned to worker #{assigned_worker_id}"
        )
        db.add(ownership)
        db.commit()
        db.refresh(issue)
        return issue

    def transfer_ownership(
        self, db: Session, issue: Issue, new_owner_id: int, reason: str, changed_by_id: Optional[int] = None
    ) -> Issue:
        old_owner = issue.assigned_worker_id
        issue.assigned_worker_id = new_owner_id

        ownership = IssueOwnershipHistory(
            issue_id=issue.id,
            action_type="TRANSFER_OWNERSHIP",
            previous_owner_id=old_owner,
            new_owner_id=new_owner_id,
            previous_supervisor_id=issue.assigned_supervisor_id,
            new_supervisor_id=issue.assigned_supervisor_id,
            previous_department=issue.department,
            new_department=issue.department,
            changed_by_id=changed_by_id,
            reason_notes=reason or "Ownership transferred."
        )
        db.add(ownership)
        db.commit()
        db.refresh(issue)
        return issue

    def reassign_department(
        self,
        db: Session,
        issue: Issue,
        new_department: str,
        reason: str,
        new_owner_id: Optional[int] = None,
        new_supervisor_id: Optional[int] = None,
        changed_by_id: Optional[int] = None
    ) -> Issue:
        old_dept = issue.department
        old_owner = issue.assigned_worker_id
        old_sup = issue.assigned_supervisor_id

        issue.department = new_department
        if new_owner_id is not None:
            issue.assigned_worker_id = new_owner_id
        if new_supervisor_id is not None:
            issue.assigned_supervisor_id = new_supervisor_id

        ownership = IssueOwnershipHistory(
            issue_id=issue.id,
            action_type="REASSIGN_DEPARTMENT",
            previous_department=old_dept,
            new_department=new_department,
            previous_owner_id=old_owner,
            new_owner_id=issue.assigned_worker_id,
            previous_supervisor_id=old_sup,
            new_supervisor_id=issue.assigned_supervisor_id,
            changed_by_id=changed_by_id,
            reason_notes=reason or f"Department reassigned from {old_dept} to {new_department}"
        )
        db.add(ownership)
        db.commit()
        db.refresh(issue)
        return issue

    def escalate(
        self,
        db: Session,
        issue: Issue,
        reason: str,
        new_supervisor_id: Optional[int] = None,
        new_owner_id: Optional[int] = None,
        changed_by_id: Optional[int] = None,
        boost_priority: bool = True
    ) -> Issue:
        old_sup = issue.assigned_supervisor_id
        old_owner = issue.assigned_worker_id
        old_priority = issue.priority

        if new_supervisor_id is not None:
            issue.assigned_supervisor_id = new_supervisor_id
        if new_owner_id is not None:
            issue.assigned_worker_id = new_owner_id

        if boost_priority:
            if issue.priority == "LOW":
                issue.priority = "MEDIUM"
            elif issue.priority == "MEDIUM":
                issue.priority = "HIGH"
            elif issue.priority == "HIGH":
                issue.priority = "CRITICAL"

        if issue.status == "Open":
            issue.status = "Waiting"

        ownership = IssueOwnershipHistory(
            issue_id=issue.id,
            action_type="ESCALATE",
            previous_owner_id=old_owner,
            new_owner_id=issue.assigned_worker_id,
            previous_supervisor_id=old_sup,
            new_supervisor_id=issue.assigned_supervisor_id,
            previous_department=issue.department,
            new_department=issue.department,
            changed_by_id=changed_by_id,
            reason_notes=f"ESCALATED (Priority: {old_priority} -> {issue.priority}): {reason}"
        )
        db.add(ownership)

        status_hist = IssueStatusHistory(
            issue_id=issue.id,
            changed_by_id=changed_by_id,
            from_status=issue.status,
            to_status=issue.status,
            notes=f"Escalated priority to {issue.priority}. Reason: {reason}"
        )
        db.add(status_hist)

        db.commit()
        db.refresh(issue)
        return issue

    def close_issue(
        self,
        db: Session,
        issue: Issue,
        resolution: str,
        changed_by_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Issue:
        old_status = issue.status
        issue.status = "Closed"
        issue.resolution = resolution
        issue.resolution_time = datetime.datetime.utcnow()

        ownership = IssueOwnershipHistory(
            issue_id=issue.id,
            action_type="CLOSE_ISSUE",
            previous_owner_id=issue.assigned_worker_id,
            new_owner_id=issue.assigned_worker_id,
            previous_supervisor_id=issue.assigned_supervisor_id,
            new_supervisor_id=issue.assigned_supervisor_id,
            previous_department=issue.department,
            new_department=issue.department,
            changed_by_id=changed_by_id,
            reason_notes=notes or f"Issue closed with resolution: {resolution}"
        )
        db.add(ownership)

        status_hist = IssueStatusHistory(
            issue_id=issue.id,
            changed_by_id=changed_by_id,
            from_status=old_status,
            to_status="Closed",
            notes=notes or f"Resolution: {resolution}"
        )
        db.add(status_hist)

        db.commit()
        db.refresh(issue)
        return issue

    def update(self, db: Session, issue: Issue, obj_in: dict) -> Issue:
        for field, val in obj_in.items():
            if val is not None and hasattr(issue, field):
                setattr(issue, field, val)
        db.commit()
        db.refresh(issue)
        return issue

    def update_status(
        self,
        db: Session,
        issue: Issue,
        new_status: str,
        changed_by_id: Optional[int] = None,
        notes: Optional[str] = None,
        resolution: Optional[str] = None
    ) -> Issue:
        old_status = issue.status
        issue.status = new_status
        if resolution:
            issue.resolution = resolution
        if new_status in ["Resolved", "Closed"] and not issue.resolution_time:
            issue.resolution_time = datetime.datetime.utcnow()

        db.commit()

        history = IssueStatusHistory(
            issue_id=issue.id,
            changed_by_id=changed_by_id,
            from_status=old_status,
            to_status=new_status,
            notes=notes or f"Status changed from {old_status} to {new_status}"
        )
        db.add(history)
        db.commit()
        db.refresh(issue)
        return issue

    def add_comment(self, db: Session, issue_id: int, author_name: str, comment_text: str, author_id: Optional[int] = None) -> IssueComment:
        comment = IssueComment(
            issue_id=issue_id,
            author_id=author_id,
            author_name=author_name or "System User",
            comment_text=comment_text
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment

    def add_attachment(self, db: Session, issue_id: int, file_name: str, file_url: str, file_type: str = "document") -> IssueAttachment:
        attachment = IssueAttachment(
            issue_id=issue_id,
            file_name=file_name,
            file_url=file_url,
            file_type=file_type
        )
        db.add(attachment)
        db.commit()
        db.refresh(attachment)
        return attachment

issue_repository = IssueRepository()
