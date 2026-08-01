from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.utils.config import settings
from app.database.session import get_db
from app.repositories.worker_repository import worker_repository
from app.models.worker import Worker

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_current_worker(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Worker:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate industrial access credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        worker_code: str = payload.get("sub")
        if worker_code is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    worker = worker_repository.get_by_code(db, code=worker_code)
    if worker is None:
        raise credentials_exception
    return worker

def get_current_active_worker(current_worker: Worker = Depends(get_current_worker)) -> Worker:
    if not current_worker.is_active:
        raise HTTPException(status_code=400, detail="Inactive worker account")
    return current_worker
