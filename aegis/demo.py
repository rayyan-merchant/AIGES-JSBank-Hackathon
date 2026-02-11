import os
import numpy as np
from .agents.digital_twin import DigitalTwinAgent
from .agents.risk_agent import RiskIntelligenceAgent
from .agents.bank_strategy import BankStrategyAgent
from .agents.negotiation_customer import CustomerNegotiationAgent
from .agents.compliance_agent import ComplianceAgent
from .agents.fairness_agent import FairnessAgent
from .agents.meta_rl_agent import MetaRLAgent
from .environment.financial_env import FinancialEnv
from .environment.rl_env_extended import RLEnvironment as ExperimentalRLEnvironment
from .math.financial_math import apr as experimental_apr
from .database.logger import init_db, new_run, log_metric, log_contract

def run_demo_scenario():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    csv_path = os.path.abspath(os.path.join(data_dir, "sample_transactions.csv"))
    income = 5000.0
    debt = 20000.0
    emi = 800.0
    experimental = bool(os.environ.get("AEGIS_EXPERIMENTAL") == "1")
    init_db()
    run_id = new_run(income, debt, emi, 7)
    dt = DigitalTwinAgent(use_torch=False)
    twin = dt.build(csv_path, income, debt, emi)
    if experimental:
        _exp_env = ExperimentalRLEnvironment()
        _exp_env.reset()
        _exp_apr = experimental_apr(0.12, 12)
    env = FinancialEnv()
    env.reset({
        "default_probability": twin["default_probability"],
        "cashflow_forecast": twin["cashflow_forecast"],
        "emi_ratio": emi / max(income, 1e-6),
        "bank_exposure": debt,
        "compliance_score": 100.0,
        "fairness_index": 1.0,
    })
    risk = RiskIntelligenceAgent()
    bank = BankStrategyAgent()
    customer = CustomerNegotiationAgent()
    compliance = ComplianceAgent()
    fairness = FairnessAgent()
    initial = {"interest_rate": 0.12, "tenure_months": 120, "grace_period": False, "restructure_pct": 0.0}
    rl = MetaRLAgent(use_sb3=False)
    sim = rl.negotiate(env, bank, customer, risk, fairness, compliance, initial, rounds=7)
    final = sim["final_contract"]
    comp = compliance.validate(final)
    risk_out = risk.analyze(twin["cashflow_forecast"])
    fair_out = fairness.assess(final["interest_rate"], env.state["default_probability"])
    default_accuracy = float(1.0 - abs(twin["default_probability"] - risk_out["distress_probabilities"]["90d"]) if "distress_probabilities" in risk_out else 0.0)
    reward_curve = sim["reward_curve"]
    reward_improvement = float(reward_curve[-1] - reward_curve[0]) if reward_curve else 0.0
    total_rules = len(compliance.rules) if hasattr(compliance, "rules") else 5
    violations = len(comp.get("violations", []))
    compliance_precision = float((total_rules - violations) / max(total_rules, 1))
    initial_profit = float(initial["interest_rate"] * debt * initial["tenure_months"] / 12.0)
    final_profit = float(final["interest_rate"] * debt * final["tenure_months"] / 12.0)
    profit_delta = float(final_profit - initial_profit)
    survival_delta = float((1.0 - env.state["default_probability"]) - (1.0 - twin["default_probability"]))
    log_metric(run_id, "default_prediction_accuracy", default_accuracy)
    log_metric(run_id, "reward_improvement", reward_improvement)
    log_metric(run_id, "compliance_detection_precision", compliance_precision)
    log_metric(run_id, "profit_delta", profit_delta)
    log_metric(run_id, "survival_probability_delta", survival_delta)
    log_contract(run_id, final, comp["compliance_score"], final_profit, 1.0 - env.state["default_probability"])
    return {
        "experimental_enabled": experimental,
        "digital_twin": twin,
        "risk": risk_out,
        "initial_offer": bank.offer(risk_out["risk_heatmap"], env.state["bank_exposure"], 0.0),
        "customer_counter": customer.counter_offer({"interest_rate": 0.12, "tenure_months": 120, "grace_period": False, "restructure_pct": 0.0}, env.state),
        "rl_convergence": sim["reward_curve"],
        "transcript": sim["transcript"],
        "final_contract": final,
        "compliance": comp,
        "fairness": fair_out,
        "metrics": {
            "default_prediction_accuracy": default_accuracy,
            "reward_improvement": reward_improvement,
            "compliance_detection_precision": compliance_precision,
            "profit_delta": profit_delta,
            "survival_probability_delta": survival_delta,
        },
    }
