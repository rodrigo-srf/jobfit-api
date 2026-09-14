from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ProfileUpdate(BaseModel):
    skills: str
    summary: str = ""

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    full_name: str
    skills: str
    summary: str

class JobCreate(BaseModel):
    title: str
    company: str
    description: str
    requirements: str = ""
    location: str = "Remote"
    salary_min: float | None = None
    salary_max: float | None = None

class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    company: str
    description: str
    requirements: str
    location: str
    salary_min: float | None
    salary_max: float | None
    status: str
    match_score: float
    created_at: datetime

class ApplicationCreate(BaseModel):
    job_id: int
    stage: str = "applied"
    notes: str = ""

class ApplicationUpdate(BaseModel):
    stage: str | None = None
    notes: str | None = None

class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    job_id: int
    stage: str
    notes: str
    applied_at: datetime
    updated_at: datetime
