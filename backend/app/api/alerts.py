from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.models.models import User
from backend.app.services.data_service import DataService
from backend.app.services.ml_service import MLService
from backend.app.services.twin_service import TwinService
from backend.app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])
data = DataService()
twin = TwinService(data)
ml = MLService(data)


@router.get("/{well_id}")
def alerts(
    well_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Return the current alert state for a well.

    Alert conditions are derived from the current Digital Twin state and the
    latest failure prediction. This endpoint is intentionally read-only:
    refreshing the dashboard must not create duplicate rows in PostgreSQL.

    The database session remains part of the contract for compatibility with
    the existing authenticated API, but the current alert feed is computed
    from live prototype state rather than persisted on every GET request.
    """
    del db  # Read-only endpoint; no database mutation is required here.

    state = twin.state(well_id).to_dict()
    risk = ml.predict("failure", well_id, {})
    generated = AlertService.build_alerts(state, risk)

    now = datetime.now(timezone.utc)
    return [
        {
            "id": f"{well_id}:{item['alert_type']}",
            "well_id": well_id,
            **item,
            "acknowledged": False,
            "created_at": now,
        }
        for item in generated
    ]
