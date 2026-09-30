import numpy as np

def simulate_srp(state,scenario,inflow_index):
    spm=scenario["spm"]
    stroke=scenario["stroke_length_m"]

    fillage=np.clip(
        .42+.065*inflow_index+
        .045*(spm-5)-
        .018*max(spm-8,0),
        .4,.95
    )

    rod_load=np.clip(
        3600+
        520*spm+
        750*stroke+
        900*fillage+
        .055*state.oil_viscosity_cp,
        3500,14000
    )

    efficiency=np.clip(
        fillage-
        .018*max(spm-8,0)-
        .000018*state.oil_viscosity_cp+
        .16,
        .30,.90
    )

    return {
        "pump_fillage":float(fillage),
        "rod_load_lb":float(rod_load),
        "pump_efficiency":float(efficiency),
        "vfd_frequency_hz":float(scenario.get("vfd_frequency_hz", state.vfd_frequency_hz))
    }
