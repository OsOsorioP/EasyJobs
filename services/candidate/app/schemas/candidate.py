import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class CandidateCreate(BaseModel):
    recruiter_id: uuid.UUID
    name: str
    email: EmailStr
    phone: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None

class CandidateUpdate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None

class CandidatePatch(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None

class CandidateRead(BaseModel):
    id: uuid.UUID
    recruiter_id: uuid.UUID
    name: str
    email: str
    phone: Optional[str]
    summary: Optional[str]
    skills: Optional[str]
    experience: Optional[str]
    last_indexed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}