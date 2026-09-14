from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import UserOut, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("", response_model=UserOut)
def update_profile(payload: ProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.skills = payload.skills
    current_user.summary = payload.summary
    db.commit(); db.refresh(current_user)
    return current_user
