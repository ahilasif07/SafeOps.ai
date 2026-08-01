from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.worker_repository import worker_repository
from app.auth.security import verify_password, create_access_token
from app.schemas.auth import Token, WorkerLogin

class AuthService:
    def authenticate_worker(self, db: Session, login_data: WorkerLogin) -> Token:
        worker = worker_repository.get_by_email(db, login_data.email)
        if not worker or not verify_password(login_data.password, worker.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not worker.is_active:
            raise HTTPException(status_code=400, detail="Worker account deactivated")

        access_token = create_access_token(data={"sub": worker.worker_code, "role": worker.role})
        return Token(
            access_token=access_token,
            worker_id=worker.id,
            worker_code=worker.worker_code,
            role=worker.role
        )

auth_service = AuthService()
