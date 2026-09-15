from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Application, Job, User
from app.schemas import StatsOut

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=StatsOut)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    jobs = db.query(Job).filter(Job.owner_id == current_user.id)
    applications = db.query(Application).filter(Application.owner_id == current_user.id)

    average = (
        db.query(func.avg(Job.match_score))
        .filter(Job.owner_id == current_user.id)
        .scalar()
        or 0.0
    )

    return StatsOut(
        jobs=jobs.count(),
        applications=applications.count(),
        interviews=applications.filter(Application.stage.in_(["interview", "technical"])).count(),
        offers=applications.filter(Application.stage == "offer").count(),
        average_match_score=round(float(average), 2),
    )
