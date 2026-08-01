from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    worker_id: int
    worker_code: str
    role: str

class TokenData(BaseModel):
    worker_code: Optional[str] = None
    role: Optional[str] = None

class WorkerLogin(BaseModel):
    email: EmailStr
    password: str
