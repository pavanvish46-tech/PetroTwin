from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.models.models import SimulationRun, User
from backend.app.schemas.common import SimulationRequest
from backend.app.services.data_service import DataService
from backend.app.services.twin_service import TwinService

router = APIRouter(prefix="/simulation", tags=["Digital Twin"])
twin = TwinService(DataService())

@router.post("")
def simulate(payload: SimulationRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        result = twin.simulation(payload.well_id, payload.scenario)
    except KeyError:
        raise HTTPException(status_code=404, detail="Well not found")
    run = SimulationRun(well_id=payload.well_id, scenario=payload.scenario, result=result, created_by=user.id)
    db.add(run); db.commit(); db.refresh(run)
    return {"simulation_id": run.id, "well_id": payload.well_id, "scenario": payload.scenario, "result": result}
