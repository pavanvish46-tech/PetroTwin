from .css import simulate_css
from .srp import simulate_srp
from .production import estimate_production
from .coupling import coupled_response

class DigitalTwin:

    def simulate(self,state,scenario):
        css=simulate_css(state,scenario)

        inflow=.75*css["mobility_index"]+.18

        srp=simulate_srp(
            state,
            scenario,
            inflow
        )

        production=estimate_production(
            css["mobility_index"],
            srp["pump_fillage"],
            scenario["spm"],
            scenario["stroke_length_m"],
            css["temperature_24h"],
            css["viscosity_cp"]
        )

        return coupled_response(
            state,
            css,
            srp,
            production
        )
