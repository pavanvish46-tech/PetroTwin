import numpy as np

def viscosity_from_temperature(base_viscosity_cp,temperature_c,reference_c=47):
    return float(np.clip(
        base_viscosity_cp*np.exp(-.027*(temperature_c-reference_c)),
        400,20000
    ))

def mobility_index(viscosity_cp):
    return float(np.clip(
        (10000/max(viscosity_cp,1))**.55,
        .5,8
    ))
