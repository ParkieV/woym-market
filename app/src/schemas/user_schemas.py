from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    login: str
    password: str


class UserOut(BaseModel):
    id: str
    login: str
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class SettingsOut(BaseModel):
    id: int
    user_id: int
    rate: float


class SettingsUpdate(BaseModel):
    rate: float
