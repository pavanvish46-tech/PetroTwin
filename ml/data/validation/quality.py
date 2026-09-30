import pandas as pd

REQUIRED_COLUMNS = [
    "well_id","date","cycle_id","steam_rate_tpd",
    "steam_temperature_c","soak_time_hours","spm",
    "stroke_length_m","oil_production_bopd",
    "failure_next_7d","temperature_24h_target_c",
    "production_next_24h_target_bopd","is_synthetic"
]

RANGES = {
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

def validate_schema(df):
    missing=[c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    return True

def range_violations(df):
    result={}
    for col,(lo,hi) in RANGES.items():
        if col in df.columns:
            result[col]=int(((df[col]<lo)|(df[col]>hi)).sum())
    return result

def quality_report(df):
    return {
        "rows":int(len(df)),
        "columns":int(len(df.columns)),
        "duplicate_rows":int(df.duplicated().sum()),
        "missing_cells":int(df.isna().sum().sum()),
        "wells":int(df.well_id.nunique()),
        "date_min":str(df.date.min()),
        "date_max":str(df.date.max()),
        "failure_rate":float(df.failure_next_7d.mean()),
        "range_violations":range_violations(df)
    }
