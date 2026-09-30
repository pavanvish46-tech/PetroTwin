from pathlib import Path
import json
import pandas as pd
from ml.data.processing.feature_engineering import build_features, predictor_columns
from ml.data.validation.leakage import audit_features

if __name__ == "__main__":
    df=build_features(pd.read_csv("ml/data/processed/cleaned.csv"))
    cols=predictor_columns(df)
    report=audit_features(cols)
    report.update({
        "predictor_count":len(cols),
        "lag_features":sum("_lag_" in c for c in cols),
        "rolling_features":sum("rolling_" in c for c in cols),
        "physics_features":[c for c in cols if c in {"mechanical_stress_index","mechanical_stress_ewma_7d","failure_risk_prior","steam_heat_index","pump_displacement_index"}]
    })
    Path("ml/artifacts").mkdir(parents=True,exist_ok=True)
    Path("ml/artifacts/leakage_audit.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
