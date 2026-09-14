from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    skills = Column(Text, default="")
    summary = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    jobs = relationship("Job", back_populates="owner", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="owner", cascade="all, delete-orphan")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text, default="")
    location = Column(String(255), default="Remote")
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    status = Column(String(50), default="saved")
    match_score = Column(Float, default=0.0)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship("User", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stage = Column(String(50), default="applied")
    notes = Column(Text, default="")
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    job = relationship("Job", back_populates="applications")
    owner = relationship("User", back_populates="applications")
