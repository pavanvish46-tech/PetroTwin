from pathlib import Path
import numpy as np
import pandas as pd


def generate_dataset(n_wells=30, days_per_well=180, seed=26120):
    """Generate a physics-informed synthetic CSS + SRP time series.

    The dataset is synthetic and intended for prototype/model-development use.
    State variables persist through time so lagged measurements carry predictive
    information without leaking future targets/events.
    """
    rng = np.random.default_rng(seed)
    rows = []

    for w in range(1, n_wells + 1):
        well_id = f"BGH-{w:03d}"
        depth = float(rng.normal(1150, 55))
        api = float(np.clip(rng.normal(18.0, 0.5), 17, 19))
        base_temperature = float(rng.normal(47, 0.45))
        base_pressure = float(np.clip(rng.normal(24, 3.5), 15, 35))
        base_viscosity = float(np.clip(rng.normal(11000, 1100), 8500, 13500))
        productivity = float(np.clip(rng.normal(1.0, 0.10), 0.78, 1.22))
        pump_condition = float(np.clip(rng.normal(0.82, 0.07), 0.62, 0.96))

        reservoir_temp = base_temperature
        viscosity = base_viscosity
        oil_production = float(np.clip(26 * productivity + rng.normal(0, 1.0), 18, 40))
        stress_memory = 0.0

        for d in range(days_per_well):
            date = pd.Timestamp("2025-01-01") + pd.Timedelta(days=d)
            cycle = d // 30 + 1
            day = d % 30
            phase = "injection" if day < 4 else ("soak" if day < 7 else "production")
            cycle_factor = max(0.86, 1.0 - 0.018 * (cycle - 1))

            # CSS operating decisions with persistent well-specific behavior.
            steam_rate = float(np.clip(
                178 + 16*np.sin(cycle*0.75 + w*0.17) + rng.normal(0, 5.5), 145, 215
            ))
            steam_temperature = float(np.clip(rng.normal(306 + 1.5*np.sin(w), 4.5), 292, 320))
            steam_pressure = float(np.clip(rng.normal(79, 4.0), 65, 92))
            steam_quality = float(np.clip(rng.normal(.78, .025), .70, .86))
            injection_duration = float(np.clip(rng.normal(3.2, .35), 2.3, 4.2))
            soak_time = float(np.clip(54 + 5*np.sin(w/5) + rng.normal(0, 2.8), 42, 68))

            # SRP operating point changes slowly rather than independently each day.
            spm = float(np.clip(6.8 + 0.75*np.sin(d/8 + w/4) + rng.normal(0, .28), 4.8, 9.2))
            stroke = float(np.clip(2.70 + .16*np.sin(d/11 + w/7) + rng.normal(0, .08), 2.25, 3.25))
            vfd = float(np.clip(27 + spm*2.15 + rng.normal(0, 0.8), 25, 50))

            heat_input = (
                0.070*steam_rate
                + 0.085*(steam_temperature - 280)
                + 2.0*steam_quality
                + 0.060*soak_time
            )

            # Thermal state: heating during/after CSS and gradual cooling during production.
            heating = 0.018 * heat_input * (1.0 if day < 10 else 0.35)
            cooling = 0.040 * max(reservoir_temp - base_temperature, 0) if phase == "production" else 0.008 * max(reservoir_temp-base_temperature,0)
            reservoir_temp = float(np.clip(
                reservoir_temp + heating - cooling + rng.normal(0, .20),
                45, 115
            ))

            viscosity_target = base_viscosity * np.exp(-0.030 * (reservoir_temp - base_temperature))
            viscosity = float(np.clip(
                0.88*viscosity + 0.12*viscosity_target + rng.normal(0, 70),
                650, 15000
            ))

            mobility = float(np.clip((10000/max(viscosity,1))**0.60, .65, 6.5))
            inflow = float(np.clip(
                productivity * (
                    .82*mobility + .20*(base_pressure/24) + .12*cycle_factor
                ) + rng.normal(0, .025),
                .55, 5.8
            ))

            # Pump condition slowly degrades/recoveries; high stress accelerates degradation.
            pump_condition = float(np.clip(
                pump_condition
                - 0.0010*max(stress_memory-0.7, 0)
                + 0.0015*(0.80-pump_condition)
                + rng.normal(0, .004),
                .55, .96
            ))

            pump_fillage = float(np.clip(
                .43 + .062*inflow + .038*(spm-5)
                - .020*max(spm-8,0)
                + .16*(pump_condition-.75)
                + rng.normal(0,.012),
                .42,.94
            ))

            pump_efficiency = float(np.clip(
                pump_fillage - .020*max(spm-8,0)
                - .000012*viscosity + .15*pump_condition + .06
                + rng.normal(0,.008),
                .35,.90
            ))

            # Production is driven by inflow, pump fillage, thermal state and operating point.
            production_capacity = (
                5.5
                + 6.2*inflow
                + 18.0*pump_fillage
                + 2.7*(spm*stroke/19.25)
                + .105*(reservoir_temp-50)
                - .00016*viscosity
            )
            oil_production = float(np.clip(
                .72*oil_production + .28*(production_capacity*cycle_factor) + rng.normal(0, .65),
                10, 75
            ))

            water_cut = float(np.clip(
                .10 + .0018*max(day-8,0) + .012*(cycle-1)
                + .015*max(1-pump_condition,0) + rng.normal(0,.008),
                .04,.42
            ))
            water_production = float(oil_production * water_cut / max(1-water_cut,.1))
            sor = float(steam_rate / max(oil_production,1))

            rod_load = float(np.clip(
                3400 + 510*spm + 720*stroke + 850*pump_fillage
                + .050*viscosity + 950*max(0.72-pump_condition,0)
                + rng.normal(0,180),
                3500,14000
            ))

            energy = float(np.clip(
                .78*vfd**2/10 + .85*rod_load/1000 + .32*water_production
                + 0.08*steam_rate + rng.normal(0,2.5),
                30,260
            ))

            load_ratio = rod_load/12000
            # Persistent stress is an observable precursor; target is sampled from it.
            instantaneous_stress = (
                0.85*max(load_ratio-.58,0)
                + 0.55*max(spm-7.2,0)/2
                + 0.80*max(.64-pump_fillage,0)
                + 0.30*max(viscosity-6500,0)/6500
                + 0.25*max(sor-4.5,0)/2.5
            )
            stress_memory = .78*stress_memory + .22*instantaneous_stress
            risk_logit = (
                -11.00
                + 8.00*instantaneous_stress
                + 4.00*stress_memory
                + 1.20*max(load_ratio-.82,0)
                + 1.00*max(spm-8,0)
                + 0.70*max(6500-viscosity,0)/6500
            )
            failure_probability = float(1/(1+np.exp(-risk_logit)))
            failure_probability = float(np.clip(failure_probability, .015, .30))
            failure_next_7d = int(rng.random() < failure_probability)

            # Targets represent the next 24h state, not a same-row copy.
            thermal_target = reservoir_temp + .035*heat_input - .055*max(reservoir_temp-base_temperature,0) + rng.normal(0,.35)
            temperature_24h = float(np.clip(thermal_target,45,120))
            next_viscosity = base_viscosity*np.exp(-.030*(temperature_24h-base_temperature))
            production_24h = float(np.clip(
                oil_production
                + .55*(temperature_24h-reservoir_temp)
                + .018*(pump_fillage-.65)*oil_production
                - .18*max(sor-5,0)
                + rng.normal(0,.75),
                8,80
            ))

            rows.append({
                "well_id":well_id,"date":date.date().isoformat(),"cycle_id":f"{well_id}-C{cycle:02d}",
                "cycle_number":cycle,"day_in_cycle":day,"css_phase":phase,
                "well_depth_m":depth,"api_gravity_deg":api,"reservoir_pressure_bar":base_pressure,
                "reservoir_temperature_c":reservoir_temp,"oil_viscosity_cp":viscosity,
                "steam_rate_tpd":steam_rate,"steam_temperature_c":steam_temperature,
                "steam_pressure_bar":steam_pressure,"steam_quality":steam_quality,
                "injection_duration_days":injection_duration,"soak_time_hours":soak_time,
                "production_duration_days":max(day-7,0),"spm":spm,"stroke_length_m":stroke,
                "vfd_frequency_hz":vfd,"pump_efficiency":pump_efficiency,"pump_fillage":pump_fillage,
                "rod_load_lb":rod_load,"oil_production_bopd":oil_production,
                "water_production_bwpd":water_production,"water_cut":water_cut,
                "energy_consumption_kwh":energy,"steam_oil_ratio":sor,
                "mobility_index":mobility,"inflow_index":inflow,"pump_load_ratio":load_ratio,
                "rod_failure":int(failure_next_7d and rng.random()<.46),
                "pump_unsetting":int(failure_next_7d and rng.random()<.24),
                "rod_floating":int(pump_fillage<.58),
                "maintenance_event":int(failure_next_7d or rng.random()<.008),
                "failure_next_7d":failure_next_7d,
                "temperature_24h_target_c":temperature_24h,
                "production_next_24h_target_bopd":production_24h,
                "is_synthetic":True
            })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    output = Path("ml/data/synthetic")
    output.mkdir(parents=True, exist_ok=True)
    df = generate_dataset()
    path = output/"master_synthetic.csv"
    df.to_csv(path,index=False)
    print(f"Generated {len(df):,} rows")
    print(f"Wells: {df.well_id.nunique()}")
    print(f"CSS cycles: {df.cycle_id.nunique()}")
    print(f"Failure rate: {df.failure_next_7d.mean():.3%}")
    print(f"Saved: {path}")
