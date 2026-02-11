# Environment Design – Aegis Autonomous Financial Negotiation Engine

Good.
You’re thinking correctly — but you can’t just “do both” loosely. That creates theoretical inconsistency.

Hard truth:

If you mix competitive and cooperative without structure, your reward function collapses and learning becomes unstable.

So we formalize this properly.

You are going to build **a dual-mode environment**.

---

# 🔥 Update to `environment_design.md`

Add this section at the top:

---

# 0. Negotiation Mode Framework

The environment supports two distinct negotiation paradigms:

1. Competitive Mode (Zero-Sum Dominant)
2. Cooperative Mode (Joint Utility Optimization)

Mode must be configurable at runtime via:

```
negotiation_mode = "competitive" | "cooperative"
```

---

# 1️⃣ Competitive Mode (Adversarial RL)

## Concept

* Bank maximizes profit.
* Customer minimizes EMI + default risk.
* Utilities conflict.
* Nash-style equilibrium behavior.

Each agent has separate reward functions.

---

## 1.1 Bank Reward (Competitive)

```
R_bank = 
    + w_profit * normalized_profit
    - w_default * P_default
    - w_regulatory * Regulatory_risk
    - w_fairness * Fairness_index
```

---

## 1.2 Customer Reward (Competitive)

```
R_customer = 
    + w_survival * (1 - P_default)
    - w_emi * EMI_ratio
    - w_distress * liquidity_risk
```

Where:

```
liquidity_risk = 1 - liquidity_ratio
```

---

## Learning Setup

* Independent Q-learning or policy gradients.
* Each agent updates using its own reward.
* No shared gradients.

This models true bargaining tension.

---

# 2️⃣ Cooperative Mode (Joint Optimization)

## Concept

Both agents optimize a shared system utility.

This simulates:

* Regulatory mediation
* AI-assisted fair restructuring
* Institutional stability optimization

---

## 2.1 Shared Reward Function

```
R_joint =

+ w_profit * normalized_profit
+ w_survival * (1 - P_default)
- w_default * P_default
- w_regulatory * Regulatory_risk
- w_fairness * Fairness_index
- w_instability * EMI_ratio
```

Single reward used by both agents.

---

## Learning Setup

* Shared policy update.
* Centralized critic (if using actor-critic).
* Agents act sequentially but optimize same utility.

This produces socially optimal contracts.

---

# 3️⃣ Hybrid Evaluation Mechanism (Important for Demo)

You will run:

Scenario 1: Competitive Mode
Scenario 2: Cooperative Mode

Then show:

* Final default probability
* Final EMI ratio
* Bank profit
* Fairness index

And compare.

This visual comparison will blow judges away.

---

# 4️⃣ Structural Additions to State

Add:

```
negotiation_mode_encoded = 0 (competitive) or 1 (cooperative)
```

So RL policy can condition on mode.

---

# 5️⃣ Training Strategy

Since you’re on Kaggle GPU and short on time:

You will NOT train two fully separate models.

Instead:

* Use same environment
* Switch reward function
* Run shorter training episodes
* Show reward convergence curves for both modes

That’s enough for demo credibility.

---

# ⚠️ Critical Stability Rule

In competitive mode:

Clamp reward magnitudes so neither agent dominates learning signal.

Normalize rewards to [-1, 1].

Otherwise learning oscillates.

---

# 🔥 What This Gives You

Judges see:

* Game theory
* Multi-agent RL
* Economic modeling
* Policy experimentation
* Institutional optimization





## 1. Objective

Design a multi-agent reinforcement learning environment where:

* A Bank Agent and a Customer Agent negotiate loan restructuring.
* The system optimizes:

  * Bank profit
  * Customer survival probability
  * Default risk
  * Regulatory compliance
  * Fairness constraints

The environment must simulate realistic financial dynamics under macroeconomic stress.

---

# 2. Core Entities

### 2.1 Customer

Represents borrower financial profile.

Attributes:

* monthly_income
* monthly_expenses
* current_loan_amount
* interest_rate
* tenure_remaining_months
* credit_score
* liquidity_buffer
* default_probability
* employment_stability_index
* macro_sensitivity_factor

---

### 2.2 Bank

Represents lending institution.

Attributes:

* risk_tolerance
* capital_reserve
* target_profit_margin
* regulatory_capital_threshold
* fairness_penalty_weight

---

### 2.3 Environment

Contains:

* macro_shock_factor
* inflation_rate
* interest_rate_environment
* unemployment_index

---

# 3. State Representation (Mathematical Definition)

State vector S at time t:

S_t = [

1. P_default_t
2. Cashflow_projection_t
3. EMI_to_income_ratio_t
4. Bank_expected_profit_t
5. Regulatory_risk_score_t
6. Fairness_index_t
7. Liquidity_buffer_ratio_t
8. Macro_shock_factor_t
9. Credit_score_normalized
10. Employment_stability_index

]

All values must be normalized between 0 and 1.

---

# 4. Derived Calculations

## 4.1 EMI Calculation

EMI formula:

EMI = (P * r * (1 + r)^n) / ((1 + r)^n - 1)

Where:

* P = principal
* r = monthly interest rate
* n = remaining months

---

## 4.2 EMI-to-Income Ratio

EMI_ratio = EMI / monthly_income

---

## 4.3 Liquidity Buffer Ratio

Liquidity_ratio = liquidity_buffer / (monthly_expenses * 3)

Clipped between 0 and 1.

---

## 4.4 Default Probability Model

Simplified logistic model:

P_default = sigmoid(
w1 * EMI_ratio

* w2 * liquidity_ratio
* w3 * credit_score_normalized

- w4 * macro_shock_factor
- w5 * unemployment_index
  )

Weights must be configurable.

---

## 4.5 Bank Expected Profit

Expected_profit =
(Total_interest_revenue * (1 - P_default))

* (Loan_principal * P_default)

---

## 4.6 Regulatory Risk Score

Regulatory_risk = 1 if:

* interest_rate > legal_cap
* capital_reserve < regulatory_capital_threshold

Else:
Regulatory_risk = 0

---

## 4.7 Fairness Index

Fairness_index = | interest_rate - peer_group_avg_rate |

Normalized 0–1.

Peer group defined by:

* Similar credit score bucket
* Similar income bracket

---

# 5. Action Space

## 5.1 Customer Agent Actions

Discrete:

1. request_interest_reduction
2. request_tenure_extension
3. request_grace_period
4. accept_offer
5. reject_offer

---

## 5.2 Bank Agent Actions

Discrete:

1. increase_rate_small
2. decrease_rate_small
3. extend_tenure
4. reduce_tenure
5. add_collateral_requirement
6. reject_request
7. finalize_offer

---

# 6. Transition Dynamics

After each action:

1. Recalculate EMI
2. Update EMI_ratio
3. Update P_default
4. Update expected_profit
5. Update regulatory_risk
6. Update fairness_index
7. Update state vector

---

# 7. Negotiation Protocol

* Max rounds: 6
* Alternating turns
* If both accept → terminate
* If reject twice → terminate
* If convergence in interest and tenure → finalize

Convergence condition:

|rate_bank - rate_customer| < epsilon

---

# 8. Reward Function

Multi-objective reward:

R_t =

* w_profit * normalized_profit
* w_survival * (1 - P_default)

- w_default * P_default
- w_regulatory * Regulatory_risk
- w_fairness * Fairness_index
- w_instability * EMI_ratio

Weights must be configurable via config file.

---

# 9. Episode Termination Conditions

* Agreement reached
* Default probability > 0.8
* Regulatory violation triggered
* Max rounds exceeded

---

# 10. Shock Simulation

Macro shock injection:

macro_shock_factor += shock_intensity

Shock impacts:

* Reduce monthly_income
* Increase unemployment_index
* Increase default probability

Shock slider range: 0.0 – 1.0

---

# 11. Constraints

Hard constraints:

* interest_rate >= 0
* interest_rate <= legal_cap
* tenure <= max_tenure_limit
* EMI_ratio <= 0.7 (otherwise high distress)
* Bank capital_reserve >= 0

---

# 12. Learning Framework

Multi-agent RL:

* Shared environment
* Independent policies
* Reward shared but weighted differently

Bank weights prioritize profit.
Customer weights prioritize survival.

---

# 13. Required Configurable Parameters

All weights
Legal interest cap
Max tenure
Shock intensity
Peer group definition buckets
Default model weights

---

# 14. Logging Requirements

Each step must log:

* Round number
* Action taken
* Updated state vector
* Reward
* Termination flag

---

