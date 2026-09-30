from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.models.models import User, Well
from backend.app.services.data_service import DataService
from backend.app.services.twin_service import TwinService

router = APIRouter(prefix="/wells", tags=["Wells"])
data = DataService()
twin = TwinService(data)

@router.get("")
def list_wells(_: User = Depends(get_current_user)):
    result = []
    for wid in data.list_wells():
        state = twin.state(wid).to_dict()
        result.append({"well_id": wid, "field": "Baghewala", "status": "active", "latest_state": state})
    return result

@router.get("/{well_id}")
def get_well(well_id: str, _: User = Depends(get_current_user)):
    if well_id not in data.list_wells():
        raise HTTPException(status_code=404, detail="Well not found")
    return {"well_id": well_id, "field": "Baghewala", "status": "active", "latest_state": twin.state(well_id).to_dict()}

@router.get("/{well_id}/state")
def get_state(well_id: str, _: User = Depends(get_current_user)):
    try:
        return twin.state(well_id).to_dict()
    except KeyError:
        raise HTTPException(status_code=404, detail="Well not found")

@router.get("/{well_id}/history")
def get_history(well_id: str, limit: int = 90, _: User = Depends(get_current_user)):
    if well_id not in data.list_wells():
        raise HTTPException(status_code=404, detail="Well not found")
    return data.history(well_id, max(1, min(limit, 365)))
