import itertools
from .constraints import valid
from .objectives import score

class Optimizer:
    """Constrained scenario search over coupled CSS + SRP controls.

    This is deliberately transparent for the prototype: a dense feasible scenario
    sweep makes every recommendation reproducible and easy for an engineer to inspect.
    """
    def __init__(self,twin): self.twin=twin

    def optimize(self,state):
        base={
            "steam_rate_tpd":state.steam_rate_tpd,"steam_temperature_c":state.steam_temperature_c,
            "steam_pressure_bar":state.steam_pressure_bar,"steam_quality":state.steam_quality,
            "soak_time_hours":state.soak_time_hours,"spm":state.spm,
            "stroke_length_m":state.stroke_length_m,"vfd_frequency_hz":state.vfd_frequency_hz
        }
        grids={
            "steam_rate_tpd":sorted(set(round(v,1) for v in [base["steam_rate_tpd"]*.85,base["steam_rate_tpd"]*.925,base["steam_rate_tpd"],base["steam_rate_tpd"]*1.075,base["steam_rate_tpd"]*1.15])),
            "steam_temperature_c":sorted(set(round(v,1) for v in [base["steam_temperature_c"]-8,base["steam_temperature_c"],base["steam_temperature_c"]+8])),
            "soak_time_hours":sorted(set(round(v,1) for v in [base["soak_time_hours"]-8,base["soak_time_hours"],base["soak_time_hours"]+8])),
            "spm":sorted(set(round(v,2) for v in [base["spm"]-1,base["spm"]-.5,base["spm"],base["spm"]+.5,base["spm"]+1])),
            "stroke_length_m":sorted(set(round(v,2) for v in [base["stroke_length_m"]-.25,base["stroke_length_m"],base["stroke_length_m"]+.25]))
        }
        candidates=[]
        for vals in itertools.product(*[grids[k] for k in grids]):
            scenario=dict(base,**dict(zip(grids,vals)))
            # Couple SRP speed changes to VFD operating point.
            scenario["vfd_frequency_hz"] = round(
                min(50, max(25, base["vfd_frequency_hz"] + 2.1*(scenario["spm"]-base["spm"]))), 2
            )
            if not valid(scenario): continue
            result=self.twin.simulate(state,scenario)
            candidates.append({"score":score(result),"scenario":scenario,"result":result})
        candidates.sort(key=lambda x:x["score"],reverse=True)
        return candidates
