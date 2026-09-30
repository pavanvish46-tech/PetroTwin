# Developer 2 — FastAPI Backend for SIH 26120

This folder is designed to be copied into the **same repository as Developer 1**. It does not replace `ml/`.

## Architecture

React → FastAPI → PostgreSQL/SQLite → ML artifacts + Digital Twin → FastAPI → React

The backend loads the already-trained artifacts from:

- `ml/artifacts/production_model.joblib`
- `ml/artifacts/temperature_model.joblib`
- `ml/artifacts/failure_model.joblib`
- `ml/artifacts/*.json`

It does **not retrain models**.

## Local VS Code test

Run from the repository root (the directory containing `ml/` and `backend/`):

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload
```

Open:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/health`

## Demo users

- `admin` / `Admin@26120`
- `engineer` / `Engineer@26120`
- `operator` / `Operator@26120`

Change these before any non-demo deployment.

## Main API

```text
POST /api/v1/auth/login
GET  /api/v1/auth/me
GET  /api/v1/wells
GET  /api/v1/wells/{well_id}
GET  /api/v1/wells/{well_id}/state
GET  /api/v1/wells/{well_id}/history
POST /api/v1/predict/production
POST /api/v1/predict/temperature
POST /api/v1/predict/failure
GET  /api/v1/predict/model/status
POST /api/v1/simulation
POST /api/v1/optimization
GET  /api/v1/optimization/{well_id}/recommendation
PATCH /api/v1/optimization/recommendations/{recommendation_id}/decision
GET  /api/v1/recommendations/{well_id}
GET  /api/v1/alerts/{well_id}
```

## Database

Local default: SQLite.

For deployment, set `DATABASE_URL` to PostgreSQL. The schema is created automatically for the prototype. A small runtime compatibility guard also repairs missing `alerts` columns in an existing prototype database. For production, replace this guard with versioned Alembic migrations.

## Safety/product boundary

This is a decision-support prototype. Optimization recommendations are recorded for human approval. The API does not send commands to field equipment or automatically control steam/SRP equipment.

## Synthetic-data disclosure

The current well records come from the Developer 1 physics-informed synthetic prototype dataset. They must not be presented as actual OIL/Baghewala measurements.
