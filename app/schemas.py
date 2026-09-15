from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

ApplicationStage = Literal["applied", "screening", "interview", "technical", "offer", "rejected"]


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
    stage: ApplicationStage = "applied"
    notes: str = Field(default="", max_length=4000)


class ApplicationUpdate(BaseModel):
    stage: ApplicationStage | None = None
    notes: str | None = Field(default=None, max_length=4000)


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    job_id: int
    stage: str
    notes: str
    applied_at: datetime
    updated_at: datetime


class StatsOut(BaseModel):
    jobs: int
    applications: int
    interviews: int
    offers: int
    average_match_score: float
