from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    login: str
    password: str
    is_staff: bool


class UserOut(BaseModel):
    id: int
    login: str
    created_at: datetime
    is_staff: bool

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None






