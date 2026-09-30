# Developer 1 Runbook — SIH 26120

## Setup
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Full ML pipeline
Run from the repository root:
```powershell
python -m ml.pipelines.01_generate_data
python -m ml.pipelines.02_validate_data
python -m ml.pipelines.03_clean_data
python -m ml.pipelines.04_train_all
python -m ml.pipelines.05_audit_features
```

## Demo
```powershell
python -m ml.demo_dev1
```

## Tests
```powershell
python -m pytest -q
```

## Expected current test metrics
- Production R² ≈ 0.69
- Temperature R² ≈ 0.88
- Failure ROC-AUC ≈ 0.71 and PR-AUC ≈ 0.32

Small metric changes can occur when the dataset seed or model settings are changed.

## Important data statement
The dataset is synthetic. Use the wording:

> Physics-informed synthetic prototype dataset calibrated using publicly available field and SRP information.

Do not claim the generated rows are actual Baghewala field telemetry.

## Integration contract
Developer 2 should consume the saved artifacts under `ml/artifacts/` and preserve the stored feature lists in the JSON metadata. Developer 3 should consume backend APIs rather than importing ML internals directly.
