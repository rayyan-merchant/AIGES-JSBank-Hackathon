# 📘 financial_math_spec.md

## 0. Objective

Define the exact mathematical formulations governing:

* Loan mechanics
* Risk modeling
* Financial state transitions
* Profit computation
* Fairness evaluation
* Reward functions
* Competitive vs Cooperative optimization

This document is the single source of truth for environment logic.

---

# 1️⃣ Core Financial Variables

## Retail Customer Variables

```
income_monthly
expense_monthly
existing_debt
credit_limit
credit_used
loan_amount
interest_rate_annual
tenure_months
```

Derived:

```
r_monthly = interest_rate_annual / 12
```

---

## SME Variables

```
monthly_revenue
operating_cost
debt_obligation
revenue_volatility
inventory_turnover
loan_amount
interest_rate_annual
tenure_months
```

---

# 2️⃣ EMI Formula (Exact)

Monthly EMI is calculated as:

[
EMI = P \cdot r \cdot (1+r)^n ,/, ((1+r)^n - 1)
]

Where:

```
P = loan_amount
r = monthly_interest_rate
n = tenure_months
```

Edge case:

If r = 0:

```
EMI = P / n
```

---

# 3️⃣ Financial Health Metrics

## 3.1 Debt-to-Income Ratio (DTI)

```
DTI = (existing_debt + EMI) / income_monthly
```

---

## 3.2 Liquidity Ratio

```
liquidity_ratio = (income_monthly - expense_monthly - EMI) / income_monthly
```

Interpretation:

> < 0 → immediate stress
> 0–0.2 → risky
>
> > 0.3 → healthy

---

## 3.3 Credit Utilization

```
credit_utilization = credit_used / credit_limit
```

---

## 3.4 Revenue Coverage Ratio (SME)

```
revenue_coverage = (monthly_revenue - operating_cost - EMI) / monthly_revenue
```

---

# 4️⃣ Default Probability Model

Two options supported:

---

## Option A: Logistic Regression Model

Pretrained on Kaggle dataset.

Input vector:

```
[DTI,
 liquidity_ratio,
 credit_utilization,
 revenue_volatility (if SME),
 inventory_turnover (if SME)]
```

Output:

```
P_default = model.predict_proba(X)
```

---

## Option B: Analytical Nonlinear Model

If ML model unavailable:

```
risk_score =
    3.0 * DTI
  + 2.0 * credit_utilization
  - 2.5 * liquidity_ratio
  + 1.5 * revenue_volatility

P_default = sigmoid(risk_score)
```

Where:

```
sigmoid(x) = 1 / (1 + exp(-x))
```

Clamp output:

```
P_default = min(max(P_default, 0.01), 0.99)
```

---

# 5️⃣ Bank Profit Function

## 5.1 Total Interest Earned

```
total_payment = EMI * tenure_months
total_interest = total_payment - loan_amount
```

---

## 5.2 Expected Profit

Adjusted for default risk:

```
expected_profit = total_interest * (1 - P_default)
```

Optional Loss Given Default:

```
LGD = 0.5
expected_profit =
    total_interest * (1 - P_default)
  - (loan_amount * LGD * P_default)
```

---

# 6️⃣ Regulatory Risk

Penalty if:

```
DTI > 0.5
OR
P_default > 0.4
```

Regulatory penalty:

```
regulatory_penalty = max(0, DTI - 0.5) * 2
```

---

# 7️⃣ Fairness Index

Define baseline rate:

```
risk_adjusted_rate =
    base_rate + risk_premium * P_default
```

Where:

```
base_rate = 0.08
risk_premium = 0.15
```

Fairness metric:

```
fairness_gap = interest_rate_annual - risk_adjusted_rate
```

If fairness_gap > threshold (e.g., 5%):

Apply penalty.

---

# 8️⃣ State Transition Dynamics

After negotiation action modifies:

* interest_rate
* tenure

We recompute:

```
EMI
DTI
liquidity_ratio
P_default
expected_profit
```

No stochastic transitions for hackathon.

Deterministic transitions for stability.

---

# 9️⃣ Negotiation Action Space

## Discrete Actions (Recommended)

Interest rate adjustments:

```
[-2%, -1%, 0%, +1%, +2%]
```

Tenure adjustments:

```
[-12 months, 0, +12 months]
```

Combined action space = 15 discrete combinations.

---

# 🔟 Reward Functions

---

## 🔴 Competitive Mode

### Bank Reward

```
R_bank =
    + 1.0 * normalized(expected_profit)
    - 1.5 * P_default
    - 0.5 * regulatory_penalty
    - 0.5 * fairness_penalty
```

---

### Customer Reward

```
R_customer =
    + 1.2 * (1 - P_default)
    - 1.0 * DTI
    - 1.0 * (1 - liquidity_ratio)
```

---

## 🟢 Cooperative Mode

Shared reward:

```
R_joint =
    + 1.0 * normalized(expected_profit)
    + 1.0 * (1 - P_default)
    - 1.0 * regulatory_penalty
    - 0.5 * fairness_penalty
```

Both agents optimize same reward.

---

# 11️⃣ Normalization

To stabilize RL:

```
normalized_profit =
    expected_profit / loan_amount
```

Clamp rewards:

```
reward = clip(reward, -5, 5)
```

---

# 12️⃣ Episode Termination Conditions

Episode ends when:

* 5 negotiation rounds completed
  OR
* P_default < 0.15
  OR
* regulatory_penalty > threshold

---

# 13️⃣ Metrics to Log (For Demo)

Log per episode:

```
final_interest_rate
final_tenure
final_EMI
P_default
expected_profit
fairness_gap
reward_bank
reward_customer
reward_joint
```

Plot:

* Reward curve
* Default probability over rounds
* Profit over rounds
* Competitive vs Cooperative comparison

---

# 14️⃣ Deterministic Assumption

For hackathon simplicity:

* No random macro shocks
* No stochastic volatility
* Deterministic environment ensures stable convergence

---

# 🔥 Final Design Philosophy

The system must:

* Produce economically plausible contracts
* Show different outcomes in competitive vs cooperative mode
* Demonstrate measurable trade-offs
* Converge toward stable negotiation equilibrium

This is sufficient to demonstrate:

* Multi-agent RL
* Economic modeling
* Institutional optimization
* Ethical AI consideration
