from pathlib import Path
import numpy as np
import pandas as pd

BOUNDS = {
    "steam_rate_tpd":(0,1000),
    "steam_temperature_c":(150,400),
    "steam_pressure_bar":(0,250),
    "steam_quality":(0,1),
    "soak_time_hours":(0,240),
    "spm":(0,30),
    "stroke_length_m":(0,10),
    "pump_efficiency":(0,1),
    "pump_fillage":(0,1),
    "water_cut":(0,1)
}

def clean_dataset(input_csv, output_csv):
    df=pd.read_csv(input_csv)
    df=df.drop_duplicates()
    df["date"]=pd.to_datetime(df["date"],errors="coerce")
    df=df.dropna(subset=["well_id","date"])

    numeric=[c for c in df.columns if c not in
             {"well_id","date","cycle_id","css_phase"}]

    for col in numeric:
        df[col]=pd.to_numeric(df[col],errors="coerce")

    # Invalid physical values become NaN; they are not silently clipped.
    for col,(lo,hi) in BOUNDS.items():
        if col in df:
            df.loc[(df[col]<lo)|(df[col]>hi),col]=np.nan

    df=df.sort_values(["well_id","date"]).reset_index(drop=True)

    # Recompute safe derived fields from cleaned base variables.
    if {"steam_rate_tpd","oil_production_bopd"} <= set(df.columns):
        df["steam_oil_ratio"]=np.where(
            df["oil_production_bopd"]>0,
            df["steam_rate_tpd"]/df["oil_production_bopd"],
            np.nan
        )

    if "rod_load_lb" in df:
        df["pump_load_ratio"]=df["rod_load_lb"]/12000

    Path(output_csv).parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(output_csv,index=False)
    return df
