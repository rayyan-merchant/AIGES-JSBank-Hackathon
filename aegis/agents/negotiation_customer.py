import numpy as np

class CustomerNegotiationAgent:
    def __init__(self, survival_threshold=0.8):
        self.survival_threshold = survival_threshold

    def utility(self, emi, interest_rate, tenure_months, survival_prob):
        total_interest_factor = interest_rate * tenure_months / 12.0
        u = -emi - 0.5 * total_interest_factor + 2.0 * survival_prob
        return float(u)

    def counter_offer(self, bank_offer, state):
        rate = float(bank_offer.get("interest_rate", 0.12))
        tenure = int(bank_offer.get("tenure_months", 120))
        grace = bool(bank_offer.get("grace_period", False))
        restructure = float(bank_offer.get("restructure_pct", 0.0))
        survival = float(1.0 - state.get("default_probability", 0.2))
        emi_ratio = float(state.get("emi_ratio", 0.3))
        proposed = {
            "interest_rate": max(0.0, rate - 0.01),
            "tenure_months": min(360, tenure + 12),
            "grace_period": True if not grace else grace,
            "restructure_pct": min(0.2, restructure + 0.05),
        }
        new_emi = max(0.0, emi_ratio * (proposed["interest_rate"] / max(rate, 1e-6)) * (tenure / max(proposed["tenure_months"], 1)))
        survival_adj = float(np.clip(survival + 0.05, 0.0, 1.0))
        u = self.utility(new_emi, proposed["interest_rate"], proposed["tenure_months"], survival_adj)
        return {"counter_offer": proposed, "utility_score": u, "reasoning": "reduce rate, extend tenure, add grace"}
