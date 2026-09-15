from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileUpdate(BaseModel):
    skills: str = Field(min_length=1, max_length=2000)
    summary: str = Field(default="", max_length=2000)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    full_name: str
    skills: str
    summary: str


class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    company: str = Field(min_length=2, max_length=180)
    description: str = Field(min_length=2, max_length=8000)
    requirements: str = Field(default="", max_length=5000)
    location: str = Field(default="Remote", max_length=180)
    salary_min: float | None = Field(default=None, ge=0)
    salary_max: float | None = Field(default=None, ge=0)


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


class MatchAnalysis(BaseModel):
    score: float
    matched_skills: list[str]
    missing_skills: list[str]
    profile_skills: list[str]
    required_skills: list[str]


class ApplicationCreate(BaseModel):
    job_id: int
    stage: str = Field(default="applied", max_length=50)
    notes: str = Field(default="", max_length=4000)


class ApplicationUpdate(BaseModel):
    stage: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=4000)


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    job_id: int
    stage: str
    notes: str
    applied_at: datetime
    updated_at: datetime
