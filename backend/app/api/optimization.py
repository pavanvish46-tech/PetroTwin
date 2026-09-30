from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.models.models import OptimizationRun, Recommendation, User
from backend.app.schemas.common import OptimizationRequest, DecisionRequest
from backend.app.services.data_service import DataService
from backend.app.services.twin_service import TwinService

router = APIRouter(prefix="/optimization", tags=["Optimization"])
twin = TwinService(DataService())

@router.post("")
def optimize(payload: OptimizationRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        result = twin.optimization(payload.well_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Well not found")
    if result.get("status") != "ok":
        raise HTTPException(status_code=422, detail="No feasible optimization solution")
    run = OptimizationRun(well_id=payload.well_id, strategies=result["strategies"], selected_strategy=result.get("selected"), created_by=user.id)
    db.add(run); db.flush()
    selected = next(x for x in result["strategies"] if x["name"] == result["selected"])
    rec = Recommendation(well_id=payload.well_id, strategy_name=selected["name"], scenario=selected["scenario"], result=selected["result"], explanation=result.get("explanation", {}), created_by=user.id)
    db.add(rec); db.commit(); db.refresh(rec)
    return {"optimization_id": run.id, "recommendation_id": rec.id, **result}

@router.get("/{well_id}/recommendation")
def latest_recommendation(well_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rec = db.query(Recommendation).filter(Recommendation.well_id == well_id).order_by(Recommendation.created_at.desc()).first()
    if not rec:
        raise HTTPException(status_code=404, detail="No recommendation found")
    return rec

@router.patch("/recommendations/{recommendation_id}/decision")
def decision(recommendation_id: int, payload: DecisionRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rec = db.get(Recommendation, recommendation_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    if rec.status in {"approved", "rejected"}:
        raise HTTPException(status_code=409, detail=f"Recommendation is already {rec.status} and cannot be changed")
    rec.status = payload.status
    rec.decision_note = payload.decision_note
    db.commit(); db.refresh(rec)
    return {"id": rec.id, "status": rec.status, "decision_note": rec.decision_note, "human_approval_required": True}
