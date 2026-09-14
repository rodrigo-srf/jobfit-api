from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Job, User
from app.schemas import JobCreate, JobOut
from app.services.matching import calculate_match_score

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("", response_model=JobOut, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    text = f"{payload.title} {payload.description} {payload.requirements}"
    job = Job(**payload.model_dump(), owner_id=current_user.id, match_score=calculate_match_score(current_user.skills, text))
    db.add(job); db.commit(); db.refresh(job)
    return job

@router.get("", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Job).filter(Job.owner_id == current_user.id).order_by(Job.match_score.desc(), Job.created_at.desc()).all()

@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == job_id, Job.owner_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/{job_id}/rescore", response_model=JobOut)
def rescore_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == job_id, Job.owner_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.match_score = calculate_match_score(current_user.skills, f"{job.title} {job.description} {job.requirements}")
    db.commit(); db.refresh(job)
    return job

@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == job_id, Job.owner_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job); db.commit()
