import numpy as np
from ..environment.financial_env import FinancialEnv

class MetaRLAgent:
    def __init__(self, use_sb3=True):
        self.use_sb3 = use_sb3
        self.sb3 = None
        if use_sb3:
            try:
                import stable_baselines3 as sb3
                self.sb3 = sb3
            except Exception:
                self.use_sb3 = False
        self.q = {}
        self.epsilon = 0.2
        self.gamma = 0.9
        self.alpha = 0.5

    def _s(self, state):
        dp = int(np.clip(state["default_probability"] * 10, 0, 10))
        emi = int(np.clip(state["emi_ratio"] * 100, 0, 100))
        return (dp, emi)

    def _actions(self):
        return [
            {"rate_delta": -0.01, "tenure_delta": 12, "grace_toggle": True, "collateral_adjust": -0.02},
            {"rate_delta": 0.0, "tenure_delta": 6, "grace_toggle": False, "collateral_adjust": 0.0},
            {"rate_delta": 0.01, "tenure_delta": -6, "grace_toggle": False, "collateral_adjust": 0.02},
        ]

    def _pick_action(self, s):
        acts = self._actions()
        if np.random.rand() < self.epsilon:
            return acts[np.random.randint(len(acts))]
        vals = [self.q.get((s, i), 0.0) for i in range(len(acts))]
        return acts[int(np.argmax(vals))]

    def negotiate(self, env, bank_agent, customer_agent, risk_agent, fairness_agent, compliance_agent, initial_offer, rounds=7):
        history = []
        contract = dict(initial_offer)
        for t in range(rounds):
            state = env.observe()
            risk = risk_agent.analyze(state["cashflow_forecast"])
            bank = bank_agent.offer(risk["risk_heatmap"], state["bank_exposure"], 0.0)
            cust = customer_agent.counter_offer(bank["offer"], state)
            rate = cust["counter_offer"]["interest_rate"]
            fairness = fairness_agent.assess(rate, state["default_probability"])
            metrics = {
                "compliance_score": 100.0,
                "fairness_index": fairness["fairness_index"],
                "customer_survival": 1.0 - state["default_probability"],
            }
            s = self._s(state)
            a = self._pick_action(s)
            next_state, reward, details = env.step(a, metrics)
            dp_new = float(1.0 / (1.0 + np.exp(-3.0 * (next_state["emi_ratio"] - 0.6))))
            env.state["default_probability"] = dp_new
            s2 = self._s(next_state)
            acts = self._actions()
            qmax = max(self.q.get((s2, i), 0.0) for i in range(len(acts)))
            idx = acts.index(a)
            self.q[(s, idx)] = (1 - self.alpha) * self.q.get((s, idx), 0.0) + self.alpha * (reward + self.gamma * qmax)
            contract.update(cust["counter_offer"])
            comp = compliance_agent.validate(contract)
            metrics["compliance_score"] = comp["compliance_score"]
            history.append({"round": t + 1, "reward": reward, "bank_offer": bank["offer"], "customer_counter": cust["counter_offer"]})
        convergence = [h["reward"] for h in history]
        return {"final_contract": contract, "reward_curve": convergence, "transcript": history}
