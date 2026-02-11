import numpy as np

def compute_reward(components, weights):
    w = np.array([
        weights.get("bank_profit", 0.25),
        weights.get("customer_survival", 0.25),
        -weights.get("default_probability", 0.2),
        -weights.get("compliance_violation", 0.15),
        -weights.get("fairness_deviation", 0.15),
    ])
    c = np.array([
        components.get("bank_profit", 0.0),
        components.get("customer_survival", 0.0),
        components.get("default_probability", 0.0),
        components.get("compliance_violation", 0.0),
        components.get("fairness_deviation", 0.0),
    ])
    return float(np.dot(w, c)), {"weights": w.tolist(), "components": c.tolist()}
