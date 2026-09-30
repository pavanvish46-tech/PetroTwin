def coupled_response(state,css,srp,production):
    sor=state.steam_rate_tpd/max(production,1)

    vfd = state.vfd_frequency_hz
    # scenario VFD is passed through the SRP/twin coupling when available.
    if isinstance(srp,dict) and "vfd_frequency_hz" in srp:
        vfd=srp["vfd_frequency_hz"]
    energy=max(.9*(vfd**2)/10 + .8*srp["rod_load_lb"]/1000, 0)

    risk=min(
        1,
        max(
            0,
            .10*(srp["rod_load_lb"]/12000)+
            .20*max(8-srp["pump_fillage"]*10,0)/10
        )
    )

    return {
        "production":float(production),
        "temperature_24h":css["temperature_24h"],
        "viscosity_cp":css["viscosity_cp"],
        "sor":float(sor),
        "energy":float(energy),
        "failure_risk":float(risk),
        **srp
    }
