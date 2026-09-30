from ml.digital_twin.state import WellState
from ml.digital_twin.twin_engine import DigitalTwin
from ml.optimization.optimizer import Optimizer
from ml.recommendation.engine import RecommendationEngine

state=WellState(
    well_id="BGH-023",
    reservoir_temperature_c=60,
    reservoir_pressure_bar=24,
    oil_viscosity_cp=6000,
    steam_rate_tpd=180,
    steam_temperature_c=305,
    steam_pressure_bar=78,
    steam_quality=.76,
    soak_time_hours=54,
    spm=7,
    stroke_length_m=2.7,
    vfd_frequency_hz=42,
    pump_efficiency=.70,
    pump_fillage=.75,
    rod_load_lb=6500,
    oil_production_bopd=40,
    water_cut=.15,
    energy_consumption_kwh=100
)

scenario={
    "steam_rate_tpd":195,
    "steam_temperature_c":315,
    "steam_pressure_bar":78,
    "steam_quality":.76,
    "soak_time_hours":54,
    "spm":7,
    "stroke_length_m":2.7,
    "vfd_frequency_hz":42
}

twin=DigitalTwin()
result=twin.simulate(state,scenario)

print("\n=== DIGITAL TWIN ===")
for k,v in result.items():
    print(f"{k}: {v}")

optimizer=Optimizer(twin)
results=optimizer.optimize(state)

print("\n=== OPTIMIZATION OPTIONS ===")
for item in results[:5]:
    print(item)

recommendation=RecommendationEngine(optimizer).recommend(state)

print("\n=== RECOMMENDATION ===")
print(recommendation)
