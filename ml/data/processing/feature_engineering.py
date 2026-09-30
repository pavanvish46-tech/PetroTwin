import numpy as np
import pandas as pd

FORBIDDEN = {
    "failure_next_7d", "temperature_24h_target_c", "production_next_24h_target_bopd",
    "rod_failure", "pump_unsetting", "rod_floating", "maintenance_event", "is_synthetic"
}
NON_FEATURE_ID = {"date","well_id","cycle_id","css_phase"}


def build_features(df):
    x=df.copy()
    x["date"]=pd.to_datetime(x["date"])
    x=x.sort_values(["well_id","date"]).reset_index(drop=True)

    x["day_of_year"]=x["date"].dt.dayofyear
    x["month"]=x["date"].dt.month
    x["cycle_age_ratio"]=x["day_in_cycle"]/30

    # All temporal features use only observations strictly before the current row.
    lag_cols = [
        "oil_production_bopd","reservoir_temperature_c","oil_viscosity_cp",
        "rod_load_lb","pump_fillage","pump_efficiency","steam_oil_ratio",
        "water_cut","energy_consumption_kwh"
    ]
    for col in lag_cols:
        if col in x.columns:
            for lag in (1,3,7):
                x[f"{col}_lag_{lag}d"] = x.groupby("well_id")[col].shift(lag)

    for col in ["oil_production_bopd","reservoir_temperature_c","steam_oil_ratio"]:
        if col in x.columns:
            shifted=x.groupby("well_id")[col].shift(1)
            for window in (3,7):
                x[f"{col}_rolling_mean_{window}d"] = shifted.groupby(x["well_id"]).transform(
                    lambda s: s.rolling(window,min_periods=1).mean()
                )
                if col == "oil_production_bopd" and window == 7:
                    x[f"{col}_rolling_std_{window}d"] = shifted.groupby(x["well_id"]).transform(
                        lambda s: s.rolling(window,min_periods=2).std()
                    )

    if "oil_production_bopd_lag_1d" in x:
        x["production_decline_rate"]=(
            x["oil_production_bopd_lag_1d"]-x["oil_production_bopd_lag_7d"]
        )/x["oil_production_bopd_lag_7d"].clip(lower=1)
    if "reservoir_temperature_c_lag_1d" in x:
        x["temperature_change_24h"] = (
            x["reservoir_temperature_c_lag_1d"]-x["reservoir_temperature_c_lag_3d"]
        )/2
    if "rod_load_lb_lag_1d" in x:
        x["rod_load_change_24h"] = x["rod_load_lb"] - x["rod_load_lb_lag_1d"]

    if "oil_viscosity_cp" in x:
        x["viscosity_log"]=np.log1p(x["oil_viscosity_cp"].clip(lower=0))
    if {"steam_rate_tpd","steam_temperature_c"} <= set(x.columns):
        x["steam_heat_index"]=x["steam_rate_tpd"]*(x["steam_temperature_c"]-100)
    if {"spm","stroke_length_m"} <= set(x.columns):
        x["pump_displacement_index"]=x["spm"]*x["stroke_length_m"]
    if "rod_load_lb" in x.columns:
        x["rod_load_ratio"]=x["rod_load_lb"]/12000

    # Physics-informed, leakage-safe precursor features for failure prediction.
    if {"rod_load_lb","spm","pump_fillage","oil_viscosity_cp","steam_oil_ratio"} <= set(x.columns):
        x["mechanical_stress_index"] = (
            .85*np.maximum(x["rod_load_lb"]/12000-.58,0)
            + .55*np.maximum(x["spm"]-7.2,0)/2
            + .80*np.maximum(.64-x["pump_fillage"],0)
            + .30*np.maximum(x["oil_viscosity_cp"]-6500,0)/6500
            + .25*np.maximum(x["steam_oil_ratio"]-4.5,0)/2.5
        )
        x["high_load_flag"]=(x["rod_load_lb"]>=10500).astype(int)
        x["low_fillage_flag"]=(x["pump_fillage"]<=.58).astype(int)
        x["high_sor_flag"]=(x["steam_oil_ratio"]>=5.0).astype(int)
        shifted=x.groupby("well_id")["mechanical_stress_index"].shift(1)
        x["mechanical_stress_lag_1d"]=shifted
        x["mechanical_stress_ewma_7d"]=shifted.groupby(x["well_id"]).transform(
            lambda s: s.ewm(alpha=.22,adjust=False,min_periods=1).mean()
        )
        x["failure_risk_prior"] = 1/(1+np.exp(-(
            -11.00 + 8.00*x["mechanical_stress_index"]
            + 4.00*x["mechanical_stress_ewma_7d"]
            + 1.20*np.maximum(x["rod_load_ratio"]-.82,0)
            + 1.00*np.maximum(x["spm"]-8,0)
            + .70*np.maximum(6500-x["oil_viscosity_cp"],0)/6500
        )))
    if {"steam_rate_tpd","injection_duration_days","oil_production_bopd"} <= set(x.columns):
        x["steam_intensity_per_bbl"]=(x["steam_rate_tpd"]*x["injection_duration_days"])/x["oil_production_bopd"].clip(lower=1)

    return x


def predictor_columns(df):
    return [c for c in df.columns if c not in FORBIDDEN and c not in NON_FEATURE_ID]
