# SIH 26120 — PetroTwin AI

Well-to-surface Digital Twin for Cyclic Steam Stimulation (CSS) and Sucker Rod Pump (SRP) operations for heavy-oil wells.

> **Prototype / research note:** the bundled dataset is synthetic/simulated. It must not be presented as actual Baghewala/OIL field measurements. Recommendations are decision-support outputs and require engineer review; this prototype does not directly control field equipment.

## Repository structure

```text
SIH26120-PetroTwin/
├── backend/              # FastAPI API, auth, database services
├── frontend/             # React + Vite PetroTwin AI UI
├── ml/                   # Dataset pipeline, ML models, Digital Twin, optimizer
├── docs/                 # Developer runbook and model report
├── .env.example
├── .gitignore
└── requirements.txt
```

## Local setup

### 1. Python environment

Python 3.11+ is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Environment

Copy `.env.example` to `.env` and set a strong `JWT_SECRET` for any shared environment. The local defaults use SQLite.

### 3. Start backend

From the repository root:

```powershell
python -m uvicorn backend.app.main:app --reload
```

API: `http://127.0.0.1:8000`
Swagger: `http://127.0.0.1:8000/docs`

### 4. Start frontend

Open a second terminal:

```powershell
cd frontend
npm install
$env:VITE_API_BASE_URL="http://127.0.0.1:8000"
npm run dev
```

Then open the Vite URL shown in the terminal.

## Prototype demo accounts

The current local prototype seeds these accounts:

- `engineer / Engineer@26120`
- `admin / Admin@26120`
- `operator / Operator@26120`

These are **development/demo credentials only**. Change the seeding/authentication strategy before any public or production deployment.

## Core workflow

```text
Well state
   ↓
Predictions
   ↓
Digital Twin
   ↓
What-if simulation
   ↓
Constrained multi-objective optimization
   ↓
Recommendation + explanation
   ↓
Engineer approval
```

The public scenario fields such as `steam_rate`, `steam_temperature`, `soak_time`, `spm`, and `stroke_length` are normalized by the backend to the unit-bearing Digital Twin variables.

## Main API groups

- `/health`
- `/api/v1/auth/*`
- `/api/v1/wells/*`
- `/api/v1/predict/*`
- `/api/v1/simulation`
- `/api/v1/optimization`
- `/api/v1/recommendations/*`
- `/api/v1/alerts/*`

## ML artifacts

The repository intentionally includes the trained prototype `.joblib` artifacts required for local inference. Do not regenerate or retrain them just to run the API.

The currently selected prototype models are: production — HistGradientBoostingRegressor; temperature — ExtraTreesRegressor; failure — LogisticRegression. See `docs/developer1_model_report.md` for the recorded evaluation results.

## Git hygiene

Do not commit:

- `.env` files containing secrets
- SQLite runtime database files
- `node_modules/` or `dist/`
- Python caches
- Swagger exports containing bearer tokens
- editor/OS temporary files

The included Swagger markdown exports from local testing are intentionally **not** part of this repository.

## Before deployment

1. Replace demo credentials / seeding strategy.
2. Set a strong secret through the hosting platform's environment variables.
3. Set production `DATABASE_URL` and `CORS_ORIGINS`.
4. Set frontend `VITE_API_BASE_URL` to the deployed backend.
5. Keep the synthetic-data limitation visible in documentation/demo material.
6. Run the full local integration test again after any environment change.

## Consolidated correction package

The current package includes the backend schema compatibility fix, non-duplicating alerts, terminal recommendation decisions, pinned scikit-learn runtime, complete backend runtime dependencies, and the Module 1 Well Digital Twin frontend. See `docs/CONSOLIDATED_CORRECTION.md` before local regression testing.
