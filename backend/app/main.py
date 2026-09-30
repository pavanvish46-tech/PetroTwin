from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings, cors_list
from backend.app.db.session import Base, engine
from backend.app.db.schema import ensure_runtime_schema
from backend.app.api import auth, wells, predictions, simulation, optimization, recommendations, alerts, health
from backend.app.services.seed_service import seed_database

Base.metadata.create_all(bind=engine)
ensure_runtime_schema(engine)
seed_database()

app = FastAPI(title=settings.app_name, version=settings.app_version, description="SIH 26120 prototype backend for the CSS + SRP Digital Twin.")
app.add_middleware(CORSMiddleware, allow_origins=cors_list(), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(wells.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")
app.include_router(simulation.router, prefix="/api/v1")
app.include_router(optimization.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"name": settings.app_name, "version": settings.app_version, "docs": "/docs"}
