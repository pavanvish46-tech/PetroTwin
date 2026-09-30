from ml.digital_twin.state import WellState
from ml.digital_twin.twin_engine import DigitalTwin

def test_twin():
    state=WellState(
        "TEST",60,24,6000,180,305,78,.76,54,
        7,2.7,42,.70,.75,6500,40,.15,100
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

    result=DigitalTwin().simulate(state,scenario)

    assert result["production"]>0
    assert 0<=result["failure_risk"]<=1
