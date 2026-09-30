FUTURE_OR_EVENT_FIELDS = {
    "failure_next_7d",
    "temperature_24h_target_c",
    "production_next_24h_target_bopd",
    "rod_failure",
    "pump_unsetting",
    "rod_floating",
    "maintenance_event"
}

def audit_features(columns):
    leaked=sorted(set(columns) & FUTURE_OR_EVENT_FIELDS)
    return {
        "leakage_detected":bool(leaked),
        "leaked_columns":leaked
    }
