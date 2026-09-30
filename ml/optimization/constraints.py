LIMITS={
    "steam_rate_tpd":(100,250),
    "steam_temperature_c":(280,330),
    "steam_pressure_bar":(50,110),
    "steam_quality":(.60,.90),
    "soak_time_hours":(24,96),
    "spm":(4,10),
    "stroke_length_m":(2,3.5),
    "vfd_frequency_hz":(20,55)
}

def valid(scenario):
    return all(
        low <= scenario[key] <= high
        for key,(low,high) in LIMITS.items()
        if key in scenario
    )
