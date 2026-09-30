from fastapi import APIRouter
from sqlalchemy import text
from backend.app.db.session import engine
from backend.app.core.config import settings

router = APIRouter(tags=["System"])

@router.get("/health")
def health():
    db_status = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"
    return {"status": "ok" if db_status == "ok" else "degraded", "database": db_status, "environment": settings.environment, "version": settings.app_version}
