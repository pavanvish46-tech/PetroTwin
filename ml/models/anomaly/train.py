from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

FEATURES=[
    "rod_load_lb",
    "pump_fillage",
    "oil_production_bopd",
    "reservoir_temperature_c",
    "spm",
    "vfd_frequency_hz"
]

def train(input_csv="ml/data/processed/cleaned.csv",
          artifact="ml/artifacts/anomaly_model.joblib"):

    df=pd.read_csv(input_csv)
    cols=[c for c in FEATURES if c in df.columns]

    model=Pipeline([
        ("imputer",SimpleImputer(strategy="median")),
        ("model",IsolationForest(
            n_estimators=300,
            contamination=.03,
            random_state=26123
        ))
    ])

    model.fit(df[cols])

    Path(artifact).parent.mkdir(parents=True,exist_ok=True)
    joblib.dump(model,artifact)

    Path(artifact).with_suffix(".json").write_text(
        __import__("json").dumps({"features":cols},indent=2)
    )

    print("Anomaly model trained")
    return cols

if __name__=="__main__":
    train()
