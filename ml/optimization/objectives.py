def score(result,weights=None):
    weights=weights or {
        "production":1.0,
        "sor":.35,
        "energy":.15,
        "failure_risk":.75
    }

    return (
        weights["production"]*result["production"]
        -weights["sor"]*result["sor"]
        -weights["energy"]*result["energy"]
        -weights["failure_risk"]*100*result["failure_risk"]
    )
