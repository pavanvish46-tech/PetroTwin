from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from ml.data.processing.feature_engineering import build_features
from backend.app.core.config import settings
from backend.app.services.data_service import DataService

class MLService:
    def __init__(self, data_service: DataService):
        self.data = data_service
        self.artifact_dir = Path(settings.artifact_dir)
        self.models = {}
        self.metadata = {}
        for name in ("production", "temperature", "failure"):
            model_path = self.artifact_dir / f"{name}_model.joblib"
            meta_path = self.artifact_dir / f"{name}_model.json"
            self.models[name] = joblib.load(model_path)
            self.metadata[name] = json.loads(meta_path.read_text())

    def status(self):
        return {
            name: {
                "selected_model": self.metadata[name].get("selected_model"),
                "target": self.metadata[name].get("target"),
                "feature_count": len(self.metadata[name].get("features", [])),
                "test_scores": self.metadata[name].get("test_scores", {}).get(self.metadata[name].get("selected_model"), {}),
            }
            for name in self.models
        }

    def _row(self, well_id: str, scenario: dict):
        df = build_features(self.data.df.copy())
        rows = df[df["well_id"] == well_id].sort_values("date")
        if rows.empty:
            raise KeyError(well_id)
        row = rows.iloc[-1].copy()
        for key, value in scenario.items():
            if key in row.index:
                row[key] = value
        # Recompute current-time derived controls affected by a scenario.
        if {"rod_load_lb", "spm", "pump_fillage", "oil_viscosity_cp", "steam_oil_ratio"}.issubset(row.index):
            row["rod_load_ratio"] = float(row["rod_load_lb"]) / 12000
            row["mechanical_stress_index"] = (
                .85 * max(float(row["rod_load_lb"]) / 12000 - .58, 0)
                + .55 * max(float(row["spm"]) - 7.2, 0) / 2
                + .80 * max(.64 - float(row["pump_fillage"]), 0)
                + .30 * max(float(row["oil_viscosity_cp"]) - 6500, 0) / 6500
                + .25 * max(float(row["steam_oil_ratio"]) - 4.5, 0) / 2.5
            )
        if {"steam_rate_tpd", "steam_temperature_c"}.issubset(row.index):
            row["steam_heat_index"] = float(row["steam_rate_tpd"]) * (float(row["steam_temperature_c"]) - 100)
        if {"spm", "stroke_length_m"}.issubset(row.index):
            row["pump_displacement_index"] = float(row["spm"]) * float(row["stroke_length_m"])
        if {"steam_rate_tpd", "injection_duration_days", "oil_production_bopd"}.issubset(row.index):
            row["steam_intensity_per_bbl"] = (float(row["steam_rate_tpd"]) * float(row["injection_duration_days"])) / max(float(row["oil_production_bopd"]), 1)
        return pd.DataFrame([row])

    def predict(self, kind: str, well_id: str, scenario: dict):
        frame = self._row(well_id, scenario)
        features = self.metadata[kind]["features"]
        x = frame.reindex(columns=features)
        model = self.models[kind]
        if kind == "failure":
            value = float(model.predict_proba(x)[:, 1][0])
        else:
            value = float(model.predict(x)[0])
        return value

    def predict_with_interval(self, kind: str, well_id: str, scenario: dict):
        value = self.predict(kind, well_id, scenario)
        # Prototype uncertainty bands: empirical error from the stored test report.
        selected = self.metadata[kind].get("selected_model")
        scores = self.metadata[kind].get("test_scores", {}).get(selected, {})
        if kind == "production":
            err = float(scores.get("RMSE", 0.0))
            return value, max(0.0, value - 1.96 * err), value + 1.96 * err
        if kind == "temperature":
            err = float(scores.get("RMSE", 0.0))
            return value, value - 1.96 * err, value + 1.96 * err
        return value, None, None
