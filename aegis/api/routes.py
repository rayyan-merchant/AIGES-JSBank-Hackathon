from fastapi import APIRouter, Response, UploadFile, File, Form
import requests
from pydantic import BaseModel
import numpy as np
from ..demo import run_demo_scenario
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import os

KEY = os.getenv("GROQ_API_KEY")

router = APIRouter()

class SimulationRequest(BaseModel):
    income: float | None = None
    debt: float | None = None
    emi: float | None = None
    run_rounds: int | None = 7
    apply_shock: bool | None = False

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/run_simulation")
def run_simulation(req: SimulationRequest):
    from ..agents.digital_twin import DigitalTwinAgent
    from ..agents.risk_agent import RiskIntelligenceAgent
    from ..agents.bank_strategy import BankStrategyAgent
    from ..agents.negotiation_customer import CustomerNegotiationAgent
    from ..agents.compliance_agent import ComplianceAgent
    from ..agents.fairness_agent import FairnessAgent
    from ..agents.meta_rl_agent import MetaRLAgent
    from ..environment.financial_env import FinancialEnv
    from ..environment.shock_simulator import apply_shocks
    from ..database.logger import init_db, new_run, log_metric, log_contract
    import os
    income = float(req.income or 5000.0)
    debt = float(req.debt or 20000.0)
    emi = float(req.emi or 800.0)
    rounds = int(req.run_rounds or 7)
    init_db()
    run_id = new_run(income, debt, emi, rounds)
    dt = DigitalTwinAgent(use_torch=False)
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads", "sample_transactions.csv"))
    twin = dt.build(csv_path, income, debt, emi)
    rate_mult = 1.0
    if bool(req.apply_shock):
        s_income, rate_mult = apply_shocks(np.array(twin["cashflow_forecast"], dtype=float), {
            "income_shock_pct": 0.15,
            "rate_hike_pct": 0.02,
            "inflation_pct": 0.03,
            "market_contraction_pct": 0.05,
        })
        forecast = s_income.tolist()
        twin["cashflow_forecast"] = forecast
        p_default, liquidity_stress = dt.default_probability(income, debt * rate_mult, emi * rate_mult, forecast)
        twin["default_probability"] = p_default
        twin["liquidity_stress_score"] = liquidity_stress
        twin["risk_trajectory_curve"] = dt._risk_trajectory(income, emi * rate_mult, forecast)
        twin["survival_curve"] = [float(1.0 - p) for p in twin["risk_trajectory_curve"]]
    env = FinancialEnv()
    env.reset({
        "default_probability": twin["default_probability"],
        "cashflow_forecast": twin["cashflow_forecast"],
        "emi_ratio": (emi * rate_mult) / max(income, 1e-6),
        "bank_exposure": debt * rate_mult,
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
    sim = rl.negotiate(env, bank, customer, risk, fairness, compliance, initial, rounds=rounds)
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

class PdfRequest(BaseModel):
    interest_rate: float
    tenure_months: int
    grace_period: bool
    restructure_pct: float
    collateral_change: float | None = 0.0
    compliance_score: float | None = 0.0
    before_default_probability: float | None = 0.0
    after_default_probability: float | None = 0.0
    before_profit: float | None = 0.0
    after_profit: float | None = 0.0

@router.post("/generate_pdf")
def generate_pdf(req: PdfRequest):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 60

    c.setTitle("Aegis Final Contract")
    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, y, "Aegis — Final Contract Summary")
    y -= 30

    c.setFont("Helvetica", 11)
    c.drawString(40, y, "Contract Terms")
    y -= 16
    c.setFont("Helvetica", 10)
    terms = [
        ("Interest Rate", f"{req.interest_rate*100:.2f}%"),
        ("Tenure (months)", f"{req.tenure_months}"),
        ("Grace Period", "Yes" if req.grace_period else "No"),
        ("Restructure %", f"{req.restructure_pct*100:.2f}%"),
        ("Collateral Change", f"{(req.collateral_change or 0):+.2f}"),
    ]
    for label, val in terms:
        c.drawString(50, y, f"- {label}: {val}")
        y -= 14

    y -= 6
    c.setFont("Helvetica", 11)
    c.drawString(40, y, "Compliance")
    y -= 16
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"- Compliance Score: {req.compliance_score or 0:.2f}")
    y -= 20

    c.setFont("Helvetica", 11)
    c.drawString(40, y, "Before / After Comparison")
    y -= 16
    c.setFont("Helvetica", 10)
    rows = [
        ("Default Probability", f"{(req.before_default_probability or 0):.2f}", f"{(req.after_default_probability or 0):.2f}"),
        ("Profit", f"{(req.before_profit or 0):.2f}", f"{(req.after_profit or 0):.2f}"),
        ("EMI (approx)", "800", "800"),
    ]
    col_x = [50, 220, 360]
    c.setFont("Helvetica-Bold", 10)
    c.drawString(col_x[0], y, "Metric")
    c.drawString(col_x[1], y, "Before")
    c.drawString(col_x[2], y, "After")
    y -= 14
    c.setFont("Helvetica", 10)
    for name, before, after in rows:
        c.drawString(col_x[0], y, name)
        c.drawString(col_x[1], y, str(before))
        c.drawString(col_x[2], y, str(after))
        y -= 14

    y -= 20
    c.setFont("Helvetica", 9)
    c.drawString(40, y, "Generated by Aegis (demo). This summary is for illustration and does not constitute legal advice.")

    c.showPage()
    c.save()
    pdf_bytes = buf.getvalue()
    buf.close()
    return Response(content=pdf_bytes, media_type="application/pdf", headers={
        "Content-Disposition": "attachment; filename=Aegis_Final_Contract.pdf"
    })

@router.post("/upload_csv")
async def upload_csv(
    file: UploadFile = File(...),
    income: float = Form(5000.0),
    debt: float = Form(20000.0),
    emi: float = Form(800.0),
):
    from ..agents.digital_twin import DigitalTwinAgent
    from ..agents.risk_agent import RiskIntelligenceAgent
    from ..agents.bank_strategy import BankStrategyAgent
    from ..agents.negotiation_customer import CustomerNegotiationAgent
    from ..agents.compliance_agent import ComplianceAgent
    from ..agents.fairness_agent import FairnessAgent
    from ..agents.meta_rl_agent import MetaRLAgent
    from ..environment.financial_env import FinancialEnv
    from ..database.logger import init_db, new_run, log_metric, log_contract

    tmp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, file.filename)
    with open(tmp_path, "wb") as f:
        f.write(await file.read())

    init_db()
    run_id = new_run(income, debt, emi, 7)
    dt = DigitalTwinAgent(use_torch=False)
    twin = dt.build(tmp_path, income, debt, emi)

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

class NegotiateRequest(BaseModel):
    interest_rate: float
    tenure_months: int
    grace_period: bool
    restructure_pct: float
    collateral_change: float | None = 0.0
    default_probability: float
    emi_ratio: float
    bank_exposure: float | None = 20000.0

@router.post("/negotiate_step")
def negotiate_step(req: NegotiateRequest):
    from ..agents.negotiation_customer import CustomerNegotiationAgent
    agent = CustomerNegotiationAgent()
    state = {
        "default_probability": req.default_probability,
        "emi_ratio": req.emi_ratio,
        "bank_exposure": req.bank_exposure or 20000.0,
    }
    bank_offer = {
        "interest_rate": req.interest_rate,
        "tenure_months": req.tenure_months,
        "grace_period": req.grace_period,
        "restructure_pct": req.restructure_pct,
        "collateral_change": req.collateral_change or 0.0,
    }
    out = agent.counter_offer(bank_offer, state)
    co = out["counter_offer"]
    msg = (
        f"Counter-offer: rate {(co['interest_rate']*100):.2f}%, tenure {co['tenure_months']} months, "
        f"{'with' if co['grace_period'] else 'no'} grace, restructure {(co['restructure_pct']*100):.1f}%, "
        f"collateral change {(co.get('collateral_change',0)*100):+.1f}%."
    )
    return {
        "counter_offer": co,
        "utility_score": out["utility_score"],
        "message": msg,
        "reasoning": out.get("reasoning", "customer utility maximization"),
    }

class LLMNegotiateRequest(BaseModel):
    messages: list[dict]
    default_probability: float
    emi_ratio: float
    bank_exposure: float | None = 20000.0
    last_offer: dict | None = None

@router.post("/negotiate_llm")
def negotiate_llm(req: LLMNegotiateRequest):
    text = None
    try:
        m = [{"role": "system", "content": "You are a loan negotiation assistant. Respond ONLY as JSON with keys: summary (string), terms (object with interest_rate [decimal 0-1], tenure_months [int], grace_period [bool], restructure_pct [decimal 0-1], collateral_change [decimal -1 to 1]), reasoning (array of short strings), tags (array of short strings). The summary should be one or two sentences. Terms must be numeric as specified."}]
        m += [{"role": x.get("role","user"), "content": x.get("content","")} for x in req.messages][-10:]
        m.append({"role": "system", "content": f"default_probability={req.default_probability:.3f}, emi_ratio={req.emi_ratio:.3f}, bank_exposure={req.bank_exposure or 20000.0:.2f}"})
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.1-8b-instant", "messages": m, "temperature": 0.2}
        r = requests.post(url, json=payload, headers=headers, timeout=20)
        if r.ok:
            js = r.json()
            text = (js.get("choices") or [{}])[0].get("message", {}).get("content", None)
    except Exception:
        text = None
    structured = None
    if text:
        try:
            import json
            structured = json.loads(text)
        except Exception:
            structured = None
    if structured and isinstance(structured, dict):
        t = structured.get("terms") or {}
        co = {
            "interest_rate": float(t.get("interest_rate", 0.12)),
            "tenure_months": int(t.get("tenure_months", 120)),
            "grace_period": bool(t.get("grace_period", False)),
            "restructure_pct": float(t.get("restructure_pct", 0.0)),
            "collateral_change": float(t.get("collateral_change", 0.0)),
        }
        msg = structured.get("summary") or f"Counter-offer: rate {(co['interest_rate']*100):.2f}%, tenure {co['tenure_months']} months."
        tags = structured.get("tags") or []
        reasoning = structured.get("reasoning") or []
        return {"message": msg, "counter_offer": co, "tags": tags, "reasoning": reasoning}
    if not text:
        import random
        phrases = ["Considering affordability and stability", "Balancing risk and return", "Optimizing for survival and profit", "Adjusted for exposure and distress"]
        rate = max(0.05, min(0.25, (req.last_offer or {}).get("interest_rate", 0.12) - 0.005 + random.uniform(-0.003, 0.003)))
        tenure = max(12, min(360, (req.last_offer or {}).get("tenure_months", 120) + random.choice([-12, 0, 12])))
        grace = True if not (req.last_offer or {}).get("grace_period", False) else (req.last_offer or {}).get("grace_period", False)
        restructure = max(0.0, min(0.3, (req.last_offer or {}).get("restructure_pct", 0.0) + random.choice([0.0, 0.02, 0.03])))
        collateral = max(-0.5, min(0.5, (req.last_offer or {}).get("collateral_change", 0.0) + random.choice([-0.02, 0.0, 0.02])))
        text = f"{random.choice(phrases)}: counter-offer rate {(rate*100):.2f}%, tenure {tenure} months, {'with' if grace else 'no'} grace, restructure {(restructure*100):.1f}%, collateral change {(collateral*100):+.1f}%."
    co = {
        "interest_rate": float(rate if 'rate' in locals() else (req.last_offer or {}).get("interest_rate", 0.12)),
        "tenure_months": int(tenure if 'tenure' in locals() else (req.last_offer or {}).get("tenure_months", 120)),
        "grace_period": bool(grace if 'grace' in locals() else (req.last_offer or {}).get("grace_period", False)),
        "restructure_pct": float(restructure if 'restructure' in locals() else (req.last_offer or {}).get("restructure_pct", 0.0)),
        "collateral_change": float(collateral if 'collateral' in locals() else (req.last_offer or {}).get("collateral_change", 0.0)),
    }
    return {"message": text, "counter_offer": co, "tags": ["Risk Adjusted", "Affordability"], "reasoning": ["Improves survival", "Maintains return"]}
