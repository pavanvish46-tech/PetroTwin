from .thermal import temperature_response
from .reservoir import viscosity_from_temperature,mobility_index

def simulate_css(state,scenario,horizon_hours=24):
    temperature=temperature_response(
        state.reservoir_temperature_c,
        scenario["steam_rate_tpd"],
        scenario["steam_temperature_c"],
        scenario["steam_quality"],
        scenario["soak_time_hours"],
        horizon_hours
    )

    viscosity=viscosity_from_temperature(
        state.oil_viscosity_cp,
        temperature
    )

    mobility=mobility_index(viscosity)

    return {
        "temperature_24h":temperature,
        "viscosity_cp":viscosity,
        "mobility_index":mobility
    }
