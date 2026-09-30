from pathlib import Path
import pandas as pd
from backend.app.core.config import settings

class DataService:
    def __init__(self):
        self.path = Path(settings.data_path)
        self._df = None

    @property
    def df(self):
        if self._df is None:
            if not self.path.exists():
                raise FileNotFoundError(f"Synthetic dataset not found: {self.path}")
            self._df = pd.read_csv(self.path)
            self._df["date"] = pd.to_datetime(self._df["date"])
        return self._df

    def list_wells(self):
        return sorted(self.df["well_id"].unique().tolist())

    def latest(self, well_id: str):
        rows = self.df[self.df["well_id"] == well_id]
        if rows.empty:
            raise KeyError(well_id)
        return rows.sort_values("date").iloc[-1].to_dict()

    def history(self, well_id: str, limit: int = 90):
        rows = self.df[self.df["well_id"] == well_id].sort_values("date").tail(limit).copy()
        return rows.to_dict(orient="records")
