class AlertService:
    @staticmethod
    def build_alerts(state: dict, failure_risk: float):
        alerts = []
        if failure_risk >= 0.60:
            alerts.append({"severity": "critical", "alert_type": "failure_risk", "message": "High predicted 7-day failure risk.", "value": failure_risk})
        elif failure_risk >= 0.35:
            alerts.append({"severity": "warning", "alert_type": "failure_risk", "message": "Elevated predicted 7-day failure risk.", "value": failure_risk})
        if state.get("rod_load_lb", 0) >= 10500:
            alerts.append({"severity": "warning", "alert_type": "rod_load", "message": "Rod load is above the prototype warning threshold.", "value": state["rod_load_lb"]})
        if state.get("pump_fillage", 1) <= 0.58:
            alerts.append({"severity": "warning", "alert_type": "pump_fillage", "message": "Pump fillage is below the prototype warning threshold.", "value": state["pump_fillage"]})
        return alerts
