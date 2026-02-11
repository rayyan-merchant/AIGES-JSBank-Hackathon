import numpy as np

class FairnessAgent:
    def assess(self, interest_rate, default_probability):
        g = np.random.choice(["A", "B"])
        base = interest_rate
        rates = {"A": base * (0.98 + 0.02 * np.random.rand()), "B": base * (1.02 - 0.02 * np.random.rand())}
        defaults = {"A": default_probability * (0.95 + 0.1 * np.random.rand()), "B": default_probability * (1.05 - 0.1 * np.random.rand())}
        pricing_equality = 1.0 - abs(rates["A"] - rates["B"]) / max(base, 1e-6)
        decision_disparity = abs(defaults["A"] - defaults["B"])
        fairness_index = float(np.clip(0.5 * pricing_equality + 0.5 * (1.0 - decision_disparity), 0.0, 1.0))
        score = float(fairness_index * 100.0)
        bias_flag = bool(fairness_index < 0.8)
        parity_gap = float(abs(rates["A"] - rates["B"]) / max(base, 1e-6))
        outcome_disparity = float(decision_disparity)
        return {"fairness_score": score, "bias_flag": bias_flag, "fairness_index": fairness_index, "demographic_parity_gap": parity_gap, "outcome_disparity": outcome_disparity}
