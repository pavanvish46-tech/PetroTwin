def _distance(a,b,keys):
    return sum(abs(float(a["result"][k])-float(b["result"][k])) for k in keys)

def label_strategies(results):
    if not results: return []
    # Maximum Production: highest predicted production, then lower risk.
    maximum_production=max(results,key=lambda x:(x["result"]["production"],-x["result"]["failure_risk"]))
    # Use normalized composite so units do not dominate.
    def eff_key(x):
        r=x["result"]
        # Efficiency explicitly rewards lower steam intensity/resource use.
        steam=x["scenario"].get("steam_rate_tpd", 180.0)
        return (
            0.38*(r["sor"]/5.0)
            + 0.27*(steam/200.0)
            + 0.20*(r["energy"]/180.0)
            + 0.15*r["failure_risk"]
        )
    efficiency=min(results,key=eff_key)
    # Balanced: closest to the knee of production, efficiency and risk extremes.
    pmax=maximum_production["result"]["production"]; pmin=min(x["result"]["production"] for x in results)
    emax=max(eff_key(x) for x in results); emin=min(eff_key(x) for x in results)
    def bal_key(x):
        r=x["result"]
        pn=(r["production"]-pmin)/max(pmax-pmin,1e-6)
        en=(emax-eff_key(x))/max(emax-emin,1e-6)
        rn=1-r["failure_risk"]
        return abs(pn-.72)+abs(en-.72)+.5*abs(rn-.72)
    balanced=min(results,key=bal_key)
    # Guarantee visible diversity where possible.
    chosen=[maximum_production,balanced,efficiency]
    unique=[]
    seen=set()
    for item in chosen:
        key=tuple(sorted(item["scenario"].items()))
        if key not in seen:
            unique.append(item); seen.add(key)
    for item in results:
        if len(unique)>=3: break
        key=tuple(sorted(item["scenario"].items()))
        if key not in seen:
            unique.append(item); seen.add(key)
    names=["Maximum Production","Balanced","Maximum Efficiency"]
    return [{"name":names[i],**item} for i,item in enumerate(unique[:3])]
