# Aegis — Autonomous Financial Negotiation & Stability Network

Premium multi-agent simulation platform for bank–customer loan negotiation, risk intelligence, and compliance verification, with a FastAPI backend and a modern Streamlit dashboard.

## Overview

- Multi‑agent system simulates negotiation between a bank and a customer to reach an optimized loan contract while monitoring risk, compliance, and fairness.
- React + Vite UI provides a premium fintech dashboard experience with KPIs, animated charts, and a guided workflow.
- FastAPI backend exposes health and simulation endpoints.
- Built to be modular, reproducible, and easy to run locally.

## Architecture

- **Frontend**: React + Vite premium dashboard  
  - Sidebar-style navigation, KPI cards, Chart.js charts, chat-style transcript  
  - [aegis/web](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/web)
- **Backend**: FastAPI app + routes  
  - Health and simulation endpoint  
  - [main.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/api/main.py), [routes.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/api/routes.py)
- **Agents**: Negotiation, strategy, risk, compliance, fairness, digital twin, meta-RL  
  - [digital_twin.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/agents/digital_twin.py)  
  - [risk_agent.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/agents/risk_agent.py)  
  - [bank_strategy.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/agents/bank_strategy.py)  
  - [negotiation_customer.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/agents/negotiation_customer.py)  
  - [compliance_agent.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/agents/compliance_agent.py)  
  - [fairness_agent.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/agents/fairness_agent.py)  
  - [meta_rl_agent.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/agents/meta_rl_agent.py)
- **Environment**: Financial state, shock simulator  
  - [financial_env.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/environment/financial_env.py)  
  - [shock_simulator.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/environment/shock_simulator.py)
- **Demo**: Scenario runner for backend and UI integration  
  - [demo.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/demo.py)
- **Data**: Synthetic transaction dataset  
  - [sample_transactions.csv](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/data/sample_transactions.csv)

## Key Components

- **Digital Twin Agent**  
  Forecasts monthly cashflows from historical transactions and user inputs; computes default probability and liquidity stress in baseline and shocked scenarios.

- **Risk Intelligence Agent**  
  Computes distress probabilities (30/60/90 days) and drivers (cashflow slope, volatility, structural break). UI shows KPI cards, an early‑intervention progress bar, and a bar chart breakdown.

- **Bank Strategy Agent**  
  Generates bank’s counter-offers based on exposure, target profitability, and risk appetite; tunes interest rate, tenure, and restructure parameters.

- **Customer Negotiation Agent**  
  Chat‑based negotiation: parses natural requests (rate, tenure, grace, restructure, collateral) and responds with risk‑aware proposals, plus compliance and fairness insights.

- **Compliance Agent**  
  Validates contracts against policy guidelines; supports a manual form and a “Use negotiated offer” toggle that defaults to the Negotiation Final or current offer. Displays clause‑level pass/fail and suggested amendments.

- **Fairness Agent**  
  Monitors fairness index derived from negotiation outcomes and exposure ratios; simple score to discourage biased adjustments.

- **Meta RL Agent**  
  Runs a round-based negotiation loop to maximize expected reward using a Q-learning style fallback (numpy) without external RL libs.

- **FinancialEnv**  
  Maintains state: default probability, cashflow forecast, EMI ratio, bank exposure, compliance score, fairness index; provides reward signals for negotiation.

- **Shock Simulator**  
  Applies macro shocks to income and interest rates (income shock, rate hike, inflation, market contraction) to stress test outcomes.

## Features

- Professional fintech dashboard with:
  - KPI cards (Default Probability, Liquidity Stress, Avg Cashflow, Profit, Compliance, Fairness)
  - Animated charts (Cashflow area, Reward convergence line)
  - Risk Engine breakdown (30/60/90‑day probabilities, intervention bar, driver badges)
  - Chat‑based loan negotiation with trade‑off KPIs (EMI ratio, default prob., risk exposure)
  - Compliance manual form and negotiated‑offer toggle; clause badges and amendments
  - Fairness view with customer/bank insights
  - Final Contract grid and branded PDF download
  - Shock controls with animated loader and immediate impact across sections
- Backend API for health checks and demo simulation
- Reproducible local run with minimal dependencies

## Project Layout

```
Hackathon_project/
├─ aegis/
│  ├─ agents/                 # Core agents (risk, negotiation, strategy, etc.)
│  ├─ environment/            # FinancialEnv + shock simulator
│  ├─ api/                    # FastAPI app and routes
│  ├─ web/                    # React + Vite UI
│  ├─ demo.py                 # Demo runner shared by API/UI
├─ data/
│  └─ sample_transactions.csv # Synthetic dataset
├─ requirements.txt           # Python dependencies
└─ README.md                  # This document
```

## Installation

```bash
pip install -r requirements.txt
```
Frontend setup:
```bash
cd aegis/web
npm install
```

## Run Locally

- Backend (FastAPI):
```bash
uvicorn aegis.api.main:app --reload --port 8000
```
- Frontend (React + Vite):
```bash
cd aegis/web
npm run dev
```

Open the UI at:
```
http://localhost:5173/
```

## UI Guide

- **Dashboard**: Overview KPIs and charts. Run Simulation once to populate data.
- **Digital Twin**: Default probability, liquidity stress, average cashflow, and forecast chart.
- **Risk Engine**: KPIs for 30/60/90‑day distress, intervention progress bar, bar chart breakdown, and driver badges (trend/volatility/break).
- **Negotiation**: Chatbot for customer terms (rate, tenure, grace, restructure, collateral). Shows compliance score, fairness index, and trade‑off KPIs (EMI ratio, default prob., risk exposure). Use “Accept Current Offer” to set the Final Contract (demo).
- **Shock Simulator**: Controls to apply macro shocks; re-run to see effects.
- **Compliance**: Manual form with clause‑level results. Toggle “Use negotiated offer (Final or current offer)” to view evaluated terms in a grid and policy guidelines.
- **Fairness**: Fairness index view.
- **Final Contract**: Optimized contract shown in a grid with compliance score. “Generate PDF” opens a demo alert; server-side PDF generation can be added.

Use the upload control to provide your transaction CSV (date, amount). If no file is uploaded, the sample dataset is used.

## API Reference

- GET `/health`  
  Response: `{ "status": "ok" }`  
  [routes.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/api/routes.py#L14-L16)

- POST `/run_simulation`  
  Body (optional fields):  
  ```
  {
    "income": number,
    "debt": number,
    "emi": number,
    "run_rounds": number,
    "apply_shock": boolean
  }
  ```
  Returns a demo scenario payload (agents/env simulated).  
  [routes.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/api/routes.py#L18-L20)

## Data Model (Session State in UI)

- twin: cashflow_forecast[], default_probability, liquidity_stress_score
- env: financial environment state (emi_ratio, bank_exposure, fairness_index, default_probability)
- sim: transcript[], reward_curve[], final_contract{}
- final: { interest_rate, tenure_months, grace_period, restructure_pct }
- comp: { compliance_score, ... }

## Troubleshooting

- Frontend fails to start  
  Run: `npm install` in `aegis/web`; ensure Node 18+ is installed.

- Sidebar selection doesn’t change section  
  Click “Run Simulation” once to populate session state; sections depend on data availability.

- Charts not rendering  
  Ensure `react-chartjs-2` and `chart.js` are installed; then restart `npm run dev`.

## Notes

- RL uses a numpy-based Q-learning style fallback to avoid heavyweight dependencies.
- Risk section offers a detailed, user-friendly breakdown beyond a heatmap.
- Negotiation is conversational with compliance/fairness checks and trade‑off KPIs.
- Compliance can default to the negotiated contract and provide clause‑level feedback.
- Final contract PDF generation can be added server-side or via a client library.
- Shock simulator is deterministic and designed for quick experimentation.

## Experimental Features (Present, Not Active)

- These modules are implemented in the repository to reflect planned functionality, but they are not used by the running system.
- Optional flag: setting AEGIS_EXPERIMENTAL=1 will initialize experimental components and show an “Experimental features available” badge on the Dashboard without altering outputs or flows.
- Modules:
  - RL Environment class design: [rl_env_extended.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/environment/rl_env_extended.py)
  - Financial math (APR, EMI, NPV, IRR): [financial_math.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/math/financial_math.py)
  - Environment design dataclasses: [design.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/environment/design.py)
  - Context scaffold: [experimental.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/context/experimental.py)
  - Architecture and agents schema: [agents_schema.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/architecture/agents_schema.py)

## License

MIT (or adapt as needed for your project).

## Branding Guidelines

- Logo
  - Use a clean wordmark with optional square mark for favicon.
  - Maintain clear space equal to the height of the “A” around the logo.
  - Avoid stretching, skewing, or applying effects; keep solid fill.
- Colors
  - Primary: #0A1F44 (Deep Navy)
  - Accent: #2E6BFF (Electric Blue)
  - Success: #00C48C
  - Warning: #FFB020
  - Danger: #FF5C5C
  - Background: #F5F7FA
  - Text: #0F172A; Muted: #475569
- Typography
  - Primary: Inter or SF Pro; fallback: Segoe UI, Roboto, system-ui.
  - Headings: Semi-bold; Body: Regular; Numbers: Tabular lining when available.
  - Keep sizes consistent with Streamlit defaults; avoid very light weights.
- Iconography
  - Use simple, outline icons (Bootstrap/Lucide) with 2px strokes.
  - Consistent sizing: 16–20px for UI controls, 24–32px for KPIs.
- Components
  - Cards: 16px radius, soft shadow, 1px border rgba(2,6,23,.08).
  - Buttons: Solid accent background, 12px radius, subtle hover lift.
  - Chips/Tags: Pill shape, light accent backgrounds for statuses.
- Tone and Content
  - Institutional, concise, neutral; avoid casual copy.
  - Prefer sentence case; limit exclamation marks.

## Deployment Guide

- Prerequisites
  - Python 3.11+ and pip
  - Node 18+ for frontend build/dev; no GPU requirements
  - Recommended: Reverse proxy (Nginx) for TLS and routing
- Environment
  - Set `PORT=8000` for FastAPI; UI dev server runs on `5173` by default
  - Keep secrets out of source; use environment variables or a secrets manager
- FastAPI (Service)
  - Start: `uvicorn aegis.api.main:app --host 0.0.0.0 --port 8000`
  - Production: run behind Nginx with `proxy_pass http://127.0.0.1:8000`
- Frontend (React + Vite)
  - Development: `npm run dev` in `aegis/web` (port 5173)
  - Build static: `npm run build` then serve `aegis/web/dist` via any static server
- Reverse Proxy (Nginx sketch)
  - API: `location /api/ { proxy_pass http://127.0.0.1:8000; }`
  - UI (dev):  `location / { proxy_pass http://127.0.0.1:5173; }`
  - UI (prod): serve built static from `aegis/web/dist`; example:
    ```
    location / {
      root /var/www/aegis-web/dist;
      try_files $uri /index.html;
    }
    ```
  - TLS: terminate at Nginx; enforce HSTS; set appropriate timeouts
- Windows Services (option)
  - Use NSSM or Windows Task Scheduler to run the API and UI at boot.
- Monitoring and Logs
  - Use Uvicorn access logs; frontend dev server logs for UI
  - Health check: `GET /health` returns `{ "status": "ok" }`
- Hardening
  - Validate uploaded CSVs; restrict size and columns
  - Avoid printing sensitive configuration; sanitize logs
  - Keep dependencies up to date; pin in `requirements.txt`

## Plain-English Guide: What Each Part Does

- Dashboard  
  Think of this as the “home page”. It shows key numbers (risk, cashflow, fairness, compliance) and simple charts. After you press “Run Simulation”, these fill with your results.

- Digital Twin  
  This is your “financial echo”. It looks at your monthly money in/out and estimates how steady your cash might be in the near future. From this it suggests:
  - Default Probability: chance you might struggle to make payments
  - Liquidity Stress: how tight your monthly cash feels compared to your EMI
  - Cashflow Forecast: a simple curve of expected future cash

- Risk Engine  
  A clear risk dashboard. It shows 30/60/90‑day distress KPIs, an “early intervention” bar that tells how much room you have to stabilize, a bar chart for quick comparison, and badges explaining what’s driving risk (trend, volatility, breaks).

- Negotiation  
  A conversational chatbot where the customer proposes terms (interest rate, months to repay, grace, restructure %, collateral). The assistant replies with a risk‑aware offer, shows compliance and fairness, and explains trade‑offs like EMI ratio, estimated default probability, and risk exposure. The goal is a deal that:
  - The customer can afford
  - The bank finds acceptable
  - Stays within rules and fairness
  Click “Accept Current Offer” to finalize the contract.

- Shock Simulator  
  “What if” tool. Try scenarios like:
  - Income drops (job change or fewer hours)
  - Interest rates rise
  - Inflation makes costs higher
  - Market contracts  
  Then press “Run Simulation” to see how the risk and negotiation change.

- Compliance  
  A rule checker with two modes: Use the negotiated offer (Final or current) or fill the manual form. It gives a score, clause‑level pass/fail badges, suggested amendments, and displays the evaluated contract in a clean grid.

- Fairness  
  A balance meter. It looks at whether the deal tilts too much toward one side. The fairness index encourages outcomes that treat both sides reasonably.

- Final Contract  
  The optimized terms shown in a clean grid with a compliance score. “Generate PDF” produces a branded, concise PDF and opens the browser’s save dialog so you can pick where to store it.

- Data Input (CSV)  
  The system reads a simple file with two columns: `date` and `amount`.  
  - `date`: the day a payment happened  
  - `amount`: money in (positive) or money out (negative)  
  It groups entries by month to make the cashflow curve. You also provide three numbers: monthly income, current debt, and current EMI.

- How Decisions Are Made (without the math)  
  The platform looks for a middle ground:
  - It wants the customer’s monthly payments to be reasonable
  - It wants the bank’s risk to stay controlled and the offer to be fair
  - It rejects offers that break basic rules  
  Behind the scenes, it scores each step and chooses better moves over time. You don’t need to know the formulas — just read the KPIs and charts to understand what changed.

## Technical Math Reference
### Symbols and Notation
- EMI: monthly installment payment
- income: monthly income
- forecast: monthly cashflow estimate f_t
- slope: linear trend of forecast
- vol: standard deviation of forecast
- break: structural break metric from diffs
- p30/p60/p90: distress probabilities at 30/60/90 days
- exposure: bank’s outstanding loan exposure
- rp: risk premium added to base rate
- rate: annual interest rate; tenure_months: repayment months
- grace_period: boolean; restructure_pct: principal restructure share
- collateral: net collateral change fraction
- emi_ratio: EMI relative to income/cashflow
- default_probability: estimated failure likelihood
- compliance_score: policy adherence score
- fairness_index: fairness metric between parties

- Digital Twin math
  - Liquidity stress: (EMI − mean(forecast)) / income; clipped at ≥0
  - Default probability: 1 / (1 + exp(−3 · (EMI/income + 0.5 · stress − 0.6)))
  - Code: [digital_twin.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/agents/digital_twin.py#L55-L60)

- Risk Intelligence math
  - Cashflow slope: linear fit slope of forecast (polyfit degree 1)
  - Volatility: standard deviation of forecast
  - Structural break: max(|diffs|) / (std(diffs) + 1e−6)
  - Base distress probability: clip(0.5 − 0.8 · slope/mean + 0.3 · vol/mean, 0, 1)
  - Horizons: p30 = base; p60 = clip(p30 + 0.1 · break, 0, 1); p90 = clip(p60 + 0.1 · break, 0, 1)
  - Code: [risk_agent.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/agents/risk_agent.py#L3-L23)

- Bank Strategy math
  - Risk premium: rp = clip(p60 · 0.05, 0, 0.05)
  - Rate: clip(base_rate + rp, 0.05, 0.25)
  - Collateral change: clip((default_threshold − p60) · 0.1, −0.1, 0.1)
  - Expected interest: rate · exposure · tenure/12
  - Risk exposure: p60 · exposure
  - Code: [bank_strategy.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/agents/bank_strategy.py#L3-L30)

- Customer Negotiation math
  - Utility: u = −EMI − 0.5 · interest_rate · tenure/12 + 2 · survival_prob
  - Survival_prob approximated from default_probability (1 − p_default) with small positive adjustment
  - Code: [negotiation_customer.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/agents/negotiation_customer.py#L5-L28)

- Environment transitions
  - EMI ratio: emi_ratio ← max(0, emi_ratio + rate_delta · 0.5 − tenure_delta · 0.005); grace reduces by 5%
  - Bank exposure: exposure ← max(0, exposure + collateral_adjust · (−0.8) + rate_delta · 0.4)
  - Reward: dot product of components and weights (bank_profit, customer_survival, default_probability, compliance_violation, fairness_deviation)
  - Code: [financial_env.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/environment/financial_env.py#L32-L55), [reward_engine.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/environment/reward_engine.py#L1-L18)

- Compliance scoring
  - Heuristic mode: score = 60 + 10 · (# of present fields among apr, grace, collateral, tenure)
  - Embedding mode (if available): score ≈ 70 + 5 · mean(similarity); violations from unmatched rules
  - Code: [compliance_agent.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/agents/compliance_agent.py#L26-L59)

- Fairness index
  - Pricing equality: 1 − |rate_A − rate_B| / base_rate
  - Decision disparity: |default_A − default_B|
  - Fairness index: clip(0.5 · pricing_equality + 0.5 · (1 − decision_disparity), 0, 1)
  - Code: [fairness_agent.py](file:///c:/Users/hp%20z%20book/Desktop/Hackathon_project/aegis/agents/fairness_agent.py#L3-L14)
