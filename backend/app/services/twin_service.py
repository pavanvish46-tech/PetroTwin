from ml.digital_twin.state import WellState
from ml.digital_twin.twin_engine import DigitalTwin
from ml.simulation.simulator import Simulator
from ml.optimization.optimizer import Optimizer
from ml.recommendation.engine import RecommendationEngine
from backend.app.services.data_service import DataService


class TwinService:
    """Backend adapter for the CSS + SRP Digital Twin.

    The API intentionally exposes short, engineer-friendly scenario names such as
    ``steam_rate`` and ``stroke_length``. The ML/Digital Twin layer uses explicit
    unit-bearing names such as ``steam_rate_tpd`` and ``stroke_length_m``.
    Normalize the API payload here so both layers use the same physical variables.
    """

    SCENARIO_ALIASES = {
        "steam_rate": "steam_rate_tpd",
        "steam_temperature": "steam_temperature_c",
        "steam_pressure": "steam_pressure_bar",
        "soak_time": "soak_time_hours",
        "stroke_length": "stroke_length_m",
        "vfd_frequency": "vfd_frequency_hz",
    }

    def __init__(self, data_service: DataService):
        self.data = data_service
        self.twin = DigitalTwin()
        self.simulator = Simulator(self.twin)
        self.optimizer = Optimizer(self.twin)
        self.recommender = RecommendationEngine(self.optimizer)

    def state(self, well_id: str) -> WellState:
        r = self.data.latest(well_id)
        return WellState(
            well_id=well_id,
            reservoir_temperature_c=float(r["reservoir_temperature_c"]),
            reservoir_pressure_bar=float(r["reservoir_pressure_bar"]),
            oil_viscosity_cp=float(r["oil_viscosity_cp"]),
            steam_rate_tpd=float(r["steam_rate_tpd"]),
            steam_temperature_c=float(r["steam_temperature_c"]),
            steam_pressure_bar=float(r["steam_pressure_bar"]),
            steam_quality=float(r["steam_quality"]),
            soak_time_hours=float(r["soak_time_hours"]),
            spm=float(r["spm"]),
            stroke_length_m=float(r["stroke_length_m"]),
            vfd_frequency_hz=float(r["vfd_frequency_hz"]),
            pump_efficiency=float(r["pump_efficiency"]),
            pump_fillage=float(r["pump_fillage"]),
            rod_load_lb=float(r["rod_load_lb"]),
            oil_production_bopd=float(r["oil_production_bopd"]),
            water_cut=float(r["water_cut"]),
            energy_consumption_kwh=float(r["energy_consumption_kwh"]),
        )

    @classmethod
    def normalize_scenario(cls, scenario: dict) -> dict:
        """Translate public API control names to Digital Twin field names.

        Internal names remain supported, so optimizer-generated scenarios continue
        to work without modification.
        """
        normalized = {}
        for key, value in scenario.items():
            normalized[cls.SCENARIO_ALIASES.get(key, key)] = value
        return normalized

    def simulation(self, well_id: str, scenario: dict):
        state = self.state(well_id)
        normalized = self.normalize_scenario(scenario)
        merged = state.to_dict()
        merged.update(normalized)
        merged.pop("well_id", None)
        return self.simulator.run(state, merged)

    def optimization(self, well_id: str):
        return self.recommender.recommend(self.state(well_id))
