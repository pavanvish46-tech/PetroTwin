from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.models.models import Recommendation, User

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("/{well_id}")
def recommendations(well_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.query(Recommendation).filter(Recommendation.well_id == well_id).order_by(Recommendation.created_at.desc()).limit(20).all()
    return rows
