# SIH 26120 — Consolidated Backend + Frontend Correction Package

This package consolidates the verified prototype fixes into one repository. It is intended for **local VS Code regression testing first**; do not push or deploy until the local checks pass.

## Included corrections

### Backend
- Added `backend/app/db/schema.py` runtime compatibility guard.
- Wired the schema guard into `backend/app/main.py` after `Base.metadata.create_all()`.
- Repairs missing columns in an existing `alerts` table without deleting existing rows. This addresses the Neon prototype issue where `well_id` / `alert_type` and related fields were missing.
- Added PostgreSQL driver (`psycopg[binary]`) to backend and root requirements.
- Pinned `scikit-learn==1.8.0` to match the trained Joblib artifact environment.
- Added the integrated NumPy/Pandas/SciPy/Joblib ML runtime dependencies to backend requirements.
- Changed the alerts GET path to upsert current generated alerts rather than inserting duplicates on every refresh.
- Made approved/rejected recommendation decisions terminal at the API layer; the backend now returns HTTP 409 if a terminal recommendation is changed.

### Frontend
- Merged the Module 1 **Well Digital Twin** page into the consolidated frontend.
- Digital Twin now loads live `/state` and `/history` data and shows:
  - Reservoir state
  - CSS / steam state
  - SRP / mechanical state
  - Surface / production state
  - CSS cycle flow
  - causal engineering chain
  - recent production history
  - well cross-section visualization
  - existing what-if simulation controls
- Kept the existing authentication, API contract, optimization and approval workflow.
- Moved `@vitejs/plugin-react` and `vite` to `devDependencies`.

## Local verification sequence

From the repository root:

```powershell
# Backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload
```

Then verify:

```text
GET  /health
POST /api/v1/auth/login
GET  /api/v1/wells
GET  /api/v1/wells/BGH-023/state
GET  /api/v1/wells/BGH-023/history
GET  /api/v1/alerts/BGH-023
POST /api/v1/simulation
POST /api/v1/optimization
PATCH /api/v1/optimization/recommendations/{id}/decision
```

Frontend:

```powershell
cd frontend
npm install
npm run build
npm run dev
```

## Important prototype boundary

The current dataset is synthetic and the optimization output is decision support. No endpoint sends commands to field equipment. Human approval remains required.

For production, replace the runtime schema guard with versioned Alembic migrations and replace demo credentials/secrets.
