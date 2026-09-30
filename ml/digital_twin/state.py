from dataclasses import dataclass,asdict

@dataclass
class WellState:
    well_id:str
    reservoir_temperature_c:float
    reservoir_pressure_bar:float
    oil_viscosity_cp:float
    steam_rate_tpd:float
    steam_temperature_c:float
    steam_pressure_bar:float
    steam_quality:float
    soak_time_hours:float
    spm:float
    stroke_length_m:float
    vfd_frequency_hz:float
    pump_efficiency:float
    pump_fillage:float
    rod_load_lb:float
    oil_production_bopd:float
    water_cut:float
    energy_consumption_kwh:float

    def to_dict(self):
        return asdict(self)
