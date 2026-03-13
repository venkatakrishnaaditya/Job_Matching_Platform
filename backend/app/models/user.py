from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Literal


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Literal["CANDIDATE", "RECRUITER"]


class UserCreate(UserBase):
    password: str
    company: Optional[str] = None


class UserInDB(UserBase):
    id: Optional[str] = None
    isActive: bool = True
    createdAt: datetime = datetime.utcnow()
    updatedAt: datetime = datetime.utcnow()
