import numpy as np

def estimate_production(
    mobility,
    pump_fillage,
    spm,
    stroke,
    temperature_c,
    viscosity_cp,
    cycle_factor=1
):
    inflow=.75*mobility+.18+.10*cycle_factor

    production=(
        15+
        5.8*inflow+
        17.5*pump_fillage+
        3*(spm*stroke/19.25)+
        .10*(temperature_c-55)-
        .00022*viscosity_cp
    )

    return float(np.clip(production*cycle_factor,5,100))
