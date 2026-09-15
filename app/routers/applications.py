from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Application, Job, User
from app.schemas import ApplicationCreate, ApplicationOut, ApplicationUpdate

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationOut, status_code=201)
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == payload.job_id, Job.owner_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing = (
        db.query(Application)
        .filter(Application.job_id == payload.job_id, Application.owner_id == current_user.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Application already exists")

    application = Application(
        job_id=payload.job_id,
        owner_id=current_user.id,
        stage=payload.stage,
        notes=payload.notes,
    )
    job.status = payload.stage
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("", response_model=list[ApplicationOut])
def list_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Application)
        .filter(Application.owner_id == current_user.id)
        .order_by(Application.updated_at.desc())
        .all()
    )


@router.patch("/{application_id}", response_model=ApplicationOut)
def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = (
        db.query(Application)
        .filter(Application.id == application_id, Application.owner_id == current_user.id)
        .first()
    )
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if payload.stage is not None:
        application.stage = payload.stage
        job = db.query(Job).filter(Job.id == application.job_id, Job.owner_id == current_user.id).first()
        if job:
            job.status = payload.stage

    if payload.notes is not None:
        application.notes = payload.notes

    application.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    db.refresh(application)
    return application
