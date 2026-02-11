import numpy as np

class RiskIntelligenceAgent:
    def analyze(self, cashflow_forecast):
        x = np.array(cashflow_forecast, dtype=float)
        if len(x) < 3:
            x = np.pad(x, (0, max(0, 3 - len(x))), constant_values=np.mean(x) if len(x) else 0.0)
        slope = float(np.polyfit(np.arange(len(x)), x, 1)[0])
        vol = float(np.std(x))
        diffs = np.diff(x)
        brk = float(np.max(np.abs(diffs)) / (np.std(diffs) + 1e-6))
        base_p = lambda h: float(np.clip(0.5 - 0.8 * slope / (np.mean(x) + 1e-6) + 0.3 * vol / (np.mean(x) + 1e-6), 0.0, 1.0))
        p30 = base_p(30)
        p60 = float(np.clip(p30 + 0.1 * brk, 0.0, 1.0))
        p90 = float(np.clip(p60 + 0.1 * brk, 0.0, 1.0))
        heatmap = {
            "distress_probabilities": {"30d": p30, "60d": p60, "90d": p90},
            "cashflow_slope": slope,
            "payment_volatility": vol,
            "structural_break": brk,
        }
        intervention_window = float(np.clip(1.0 - p30, 0.0, 1.0))
        neg_seq = float(np.mean(diffs < 0)) if len(diffs) else 0.0
        delay_trend = float(np.clip(neg_seq, 0.0, 1.0))
        dep_growth = float(np.clip((-slope) / (abs(np.mean(x)) + 1e-6) + vol / (abs(np.mean(x)) + 1e-6), 0.0, 1.0))
        return {
            "risk_heatmap": heatmap,
            "early_intervention_score": intervention_window,
            "payment_delay_trend": delay_trend,
            "credit_dependency_growth": dep_growth,
        }
