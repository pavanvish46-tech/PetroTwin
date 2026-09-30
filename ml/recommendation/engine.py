from ml.optimization.strategies import label_strategies
from ml.explainability.recommendation_explainer import explain_recommendation

class RecommendationEngine:

    def __init__(self,optimizer):
        self.optimizer=optimizer

    def recommend(self,state):
        raw=self.optimizer.optimize(state)
        strategies=label_strategies(raw)

        if not strategies:
            return {"status":"no_feasible_solution"}

        selected=strategies[1]

        current={
            "steam_rate_tpd":state.steam_rate_tpd,
            "soak_time_hours":state.soak_time_hours,
            "spm":state.spm,
            "stroke_length_m":state.stroke_length_m
        }

        explanation=explain_recommendation(
            current,
            selected["scenario"],
            selected["result"]
        )

        return {
            "status":"ok",
            "strategies":strategies,
            "selected":"Balanced",
            "explanation":explanation
        }
