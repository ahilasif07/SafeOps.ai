from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.auth import Token, WorkerLogin
from app.schemas.worker import WorkerOut
from app.services.auth_service import auth_service
from app.auth.dependencies import get_current_active_worker
from app.models.worker import Worker

router = APIRouter()

@router.post("/login", response_model=Token, summary="Authenticate worker and return JWT token")
def login(login_data: WorkerLogin, db: Session = Depends(get_db)):
    return auth_service.authenticate_worker(db, login_data)

@router.get("/me", response_model=WorkerOut, summary="Get current logged in worker profile")
def read_me(current_worker: Worker = Depends(get_current_active_worker)):
    return current_worker
