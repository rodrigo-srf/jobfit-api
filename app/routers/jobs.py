from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Job, User
from app.schemas import JobCreate, JobOut, MatchAnalysis
from app.services.matching import analyze_match, calculate_match_score

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _get_owned_job(job_id: int, db: Session, current_user: User) -> Job:
    job = db.query(Job).filter(Job.id == job_id, Job.owner_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("", response_model=JobOut, status_code=201)
def create_job(
    payload: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.salary_min is not None and payload.salary_max is not None and payload.salary_min > payload.salary_max:
        raise HTTPException(status_code=422, detail="salary_min cannot be greater than salary_max")

    text = f"{payload.title} {payload.description} {payload.requirements}"
    job = Job(
        **payload.model_dump(),
        owner_id=current_user.id,
        match_score=calculate_match_score(current_user.skills, text),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Job)
        .filter(Job.owner_id == current_user.id)
        .order_by(Job.match_score.desc(), Job.created_at.desc())
        .all()
    )


@router.get("/{job_id}", response_model=JobOut)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_owned_job(job_id, db, current_user)


@router.get("/{job_id}/analysis", response_model=MatchAnalysis)
def get_job_analysis(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = _get_owned_job(job_id, db, current_user)
    return analyze_match(
        current_user.skills,
        f"{job.title} {job.description} {job.requirements}",
    )


@router.post("/{job_id}/rescore", response_model=JobOut)
def rescore_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = _get_owned_job(job_id, db, current_user)
    job.match_score = calculate_match_score(
        current_user.skills,
        f"{job.title} {job.description} {job.requirements}",
    )
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=204)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = _get_owned_job(job_id, db, current_user)
    db.delete(job)
    db.commit()
