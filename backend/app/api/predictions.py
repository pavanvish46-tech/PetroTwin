from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.models.models import Prediction, User
from backend.app.schemas.common import PredictionRequest, PredictionResponse
from backend.app.services.data_service import DataService
from backend.app.services.ml_service import MLService

router = APIRouter(prefix="/predict", tags=["Predictions"])
data = DataService()
ml = MLService(data)

def run(kind, payload, db, user):
    try:
        value, lower, upper = ml.predict_with_interval(kind, payload.well_id, payload.scenario)
    except KeyError:
        raise HTTPException(status_code=404, detail="Well not found")
    meta = ml.metadata[kind]
    rec = Prediction(well_id=payload.well_id, prediction_type=kind, value=value, lower_bound=lower, upper_bound=upper, model_version=meta.get("selected_model"), input_data=payload.scenario)
    db.add(rec); db.commit()
    return PredictionResponse(well_id=payload.well_id, prediction_type=kind, value=value, lower_bound=lower, upper_bound=upper, model_version=meta.get("selected_model", "unknown"))

@router.post("/production", response_model=PredictionResponse)
def production(payload: PredictionRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return run("production", payload, db, user)

@router.post("/temperature", response_model=PredictionResponse)
def temperature(payload: PredictionRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return run("temperature", payload, db, user)

@router.post("/failure", response_model=PredictionResponse)
def failure(payload: PredictionRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return run("failure", payload, db, user)

@router.get("/model/status")
def model_status(_: User = Depends(get_current_user)):
    return ml.status()
