def scenario_from_state(state):
    return {
        "steam_rate_tpd":state.steam_rate_tpd,
        "steam_temperature_c":state.steam_temperature_c,
        "steam_pressure_bar":state.steam_pressure_bar,
        "steam_quality":state.steam_quality,
        "soak_time_hours":state.soak_time_hours,
        "spm":state.spm,
        "stroke_length_m":state.stroke_length_m,
        "vfd_frequency_hz":state.vfd_frequency_hz
    }
