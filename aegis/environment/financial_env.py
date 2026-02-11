import numpy as np
from .reward_engine import compute_reward

class FinancialEnv:
    def __init__(self, weights=None):
        self.weights = weights or {
            "bank_profit": 0.25,
            "customer_survival": 0.25,
            "default_probability": 0.2,
            "compliance_violation": 0.15,
            "fairness_deviation": 0.15,
        }
        self.state = {
            "default_probability": 0.0,
            "cashflow_forecast": np.zeros(12).tolist(),
            "emi_ratio": 0.0,
            "bank_exposure": 0.0,
            "compliance_score": 100.0,
            "fairness_index": 1.0,
        }
        self.transcript = []

    def reset(self, initial_state=None):
        if initial_state:
            self.state.update(initial_state)
        self.transcript = []
        return self.state

    def observe(self):
        return self.state

    def step(self, action, metrics):
        rate_delta = action.get("rate_delta", 0.0)
        tenure_delta = action.get("tenure_delta", 0)
        grace_toggle = action.get("grace_toggle", False)
        collateral_adjust = action.get("collateral_adjust", 0.0)
        emi_ratio = max(0.0, self.state["emi_ratio"] + rate_delta * 0.5 - tenure_delta * 0.005)
        if grace_toggle:
            emi_ratio *= 0.95
        bank_exposure = max(0.0, self.state["bank_exposure"] + collateral_adjust * -0.8 + rate_delta * 0.4)
        self.state["emi_ratio"] = emi_ratio
        self.state["bank_exposure"] = bank_exposure
        self.state["default_probability"] = float(metrics.get("default_probability", self.state["default_probability"]))
        self.state["compliance_score"] = float(metrics.get("compliance_score", self.state["compliance_score"]))
        self.state["fairness_index"] = float(metrics.get("fairness_index", self.state["fairness_index"]))
        reward_components = {
            "bank_profit": max(0.0, rate_delta * 10 + bank_exposure * 0.1),
            "customer_survival": float(metrics.get("customer_survival", 1.0 - self.state["default_probability"])),
            "default_probability": float(self.state["default_probability"]),
            "compliance_violation": max(0.0, 100.0 - self.state["compliance_score"]) / 100.0,
            "fairness_deviation": max(0.0, abs(1.0 - self.state["fairness_index"])),
        }
        reward, details = compute_reward(reward_components, self.weights)
        self.transcript.append({"action": action, "reward": reward, "details": details})
        return self.state, reward, details
