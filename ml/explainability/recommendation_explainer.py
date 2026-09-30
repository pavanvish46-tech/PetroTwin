def explain_recommendation(current,scenario,result):
    changes=[]

    for key in [
        "steam_rate_tpd",
        "soak_time_hours",
        "spm",
        "stroke_length_m"
    ]:
        if key in current and key in scenario:
            delta=scenario[key]-current[key]
            if abs(delta)>1e-9:
                changes.append({
                    "parameter":key,
                    "change":delta
                })

    return {
        "parameter_changes":changes,
        "expected_production":result["production"],
        "expected_sor":result["sor"],
        "expected_failure_risk":result["failure_risk"],
        "human_approval_required":True
    }
