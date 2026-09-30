import numpy as np

def temperature_response(
    current_temp_c,
    steam_rate_tpd,
    steam_temperature_c,
    steam_quality,
    soak_time_hours,
    horizon_hours=24
):
    heat_input=(
        .075*steam_rate_tpd+
        .09*(steam_temperature_c-280)+
        1.8*steam_quality+
        .055*soak_time_hours
    )

    response=heat_input/10*(1-np.exp(-horizon_hours/24))
    cooling=.75*(horizon_hours/24)

    return float(np.clip(
        current_temp_c+response-cooling,
        40,150
    ))
