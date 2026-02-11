import numpy as np

class BankStrategyAgent:
    def __init__(self, base_rate=0.12, capital_ratio=0.12, default_threshold=0.3):
        self.base_rate = base_rate
        self.capital_ratio = capital_ratio
        self.default_threshold = default_threshold

    def offer(self, risk_heatmap, exposure, collateral_value):
        p = float(risk_heatmap["distress_probabilities"]["60d"])
        rp = float(np.clip(p * 0.05, 0.0, 0.05))
        rate_cap = 0.20
        rate = float(np.clip(self.base_rate + rp, 0.05, rate_cap))
        collateral_change = float(np.clip((self.default_threshold - p) * 0.1, -0.1, 0.1))
        tenure = 120
        grace = False
        restructure_pct = 0.0
        expected_interest = float(rate * exposure * tenure / 12.0)
        risk_exposure = float(p * exposure)
        capital_req = 0.12
        capital_ok = bool(self.capital_ratio >= capital_req)
        lgd = 0.4
        provisioning_cost = float(p * exposure * lgd * 0.1)
        dynamic_shift = float(rate - self.base_rate)
        return {
            "offer": {
                "interest_rate": rate,
                "tenure_months": tenure,
                "grace_period": grace,
                "restructure_pct": restructure_pct,
                "collateral_change": collateral_change,
            },
            "profit_expectation": expected_interest,
            "risk_exposure": risk_exposure,
            "capital_constraint_ok": capital_ok,
            "provisioning_cost": provisioning_cost,
            "dynamic_pricing_shift": dynamic_shift,
            "reasoning": "rate with risk premium and collateral adjustment",
        }
