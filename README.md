
# 🏦 AIGES — Agentic AI Risk & Lending Engine

### Autonomous Credit Decisioning with Reinforcement Learning(PPO), LightGBM & Basel III Optimization

AIGES is an intelligent banking simulation system that combines **credit risk modeling (LightGBM)**, **reinforcement learning (PPO)**, **Basel III capital constraints**, and **LLM-powered explainability** to optimize lending decisions.

Instead of static PD thresholds, AIGES learns a **dynamic approval strategy** that maximizes profit while controlling default risk and regulatory capital.

---

## 🔍 What Makes It Different

Traditional credit systems:

* Approve/reject based on fixed PD cutoffs
* Optimize short-term approval metrics
* Ignore capital efficiency
* Provide limited interpretability

AIGES:

* Predicts default probability using Gradient Boosting
* Optimizes lending strategy using RL (PPO)
* Enforces Basel III capital constraints
* Generates human-readable AI explanations
* Simulates regulator-bank-customer interactions

---

## 📊 Data & Modeling

### Retail Portfolio

* Based on Home Credit Default Risk dataset on Kaggle 
* Cleaned & engineered structured financial features

### SME Portfolio (Synthetic)

* 1,000 SMEs generated
* 36 months simulated financial history
* Seasonality + macro cycles + noise
* Logistic PD calibration

**Final Annual Default Rate: 5.60%** (target 5–15%)

---

## 📈 Risk Models (LightGBM)

Two Probability-of-Default models:

* Retail PD Model
* SME PD Model

Both trained using **LightGBM gradient boosting**, serialized and integrated into the decision engine.

---

## 🤖 Reinforcement Learning (PPO Policy Agent)

We trained a **Proximal Policy Optimization (PPO)** agent to:

* Maximize portfolio profit
* Minimize default risk
* Respect Basel III capital requirements

**Training:** 200,000 timesteps
**Reward Convergence:** ~0.60

### 📊 Performance Comparison

| Strategy      | Total Profit | Risk-Adjusted Return | Default Rate |
| ------------- | ------------ | -------------------- | ------------ |
| **PPO Agent** | **$718.15**  | **0.717**            | **0.12%**    |
| Rule-Based    | $70.87       | 0.070                | 0.59%        |
| PD Threshold  | -$11.29      | -0.011               | 0.55%        |

### Key Result

The RL agent achieved:

* **10× higher profit**
* **~80% lower default rate**
* Strong positive risk-adjusted return

This demonstrates that policy learning outperforms static credit rules.

---

## 🏛 Regulatory Integration (Basel III)

The system calculates:

* Risk-Weighted Assets (RWA)
* Capital requirements
* Regulatory penalties

Example:

* PD: 12%
* Capital Required: $960
* Risk Weight: 12%
* Final Decision: Approve

The RL policy optimizes approvals while preserving capital adequacy.

---

## 🧠 Explainability Layer

Each decision includes:

* Risk summary
* Risk level
* Key risk factors
* Financial impact
* Regulatory view
* Final recommendation

Combines quantitative risk signals with LLM-generated narratives for transparency.

---

## 👥 Multi-Agent Simulation

AIGES models a realistic ecosystem:

* **CustomerAgent** → Requests loan
* **BankAgent** → Uses PD + PPO strategy
* **RegulatorAgent** → Enforces capital rules

This creates a closed-loop intelligent financial system.

---

## 🛠 Tech Stack

* Python
* LightGBM (Credit Risk Modeling)
* Stable-Baselines3 PPO
* Pandas / NumPy
* Basel III Capital Framework
* LLM-based Explainability

---

## 🎯 Impact

AIGES demonstrates how AI can evolve banking from rule-based credit scoring to:

✔ Autonomous strategy learning
✔ Capital-aware optimization
✔ Regulatory-aligned AI decisions
✔ Interpretable financial intelligence

This is a prototype of a **next-generation autonomous bank risk engine**.

---

### 👥 Project Contributors  

<div align="center">
  <a href="https://www.linkedin.com/in/rayyanmerchant2004/" target="_blank">
    <img src="https://img.shields.io/badge/Rayyan%20Merchant-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white" alt="Rayyan Merchant"/>
  </a>
  <a href="https://www.linkedin.com/in/riya-bhart-339036287/" target="_blank">
    <img src="https://img.shields.io/badge/Riya%20Bhart-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white" alt="Riya Bhart"/>
  </a>
  <a href="https://www.linkedin.com/in/rija-ali-731095296" target="_blank">
    <img src="https://img.shields.io/badge/Syeda%20Rija%20Ali-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white" alt="Syeda Rija Ali"/>
  </a>
  <a href="https://www.linkedin.com/in/muhammad-abbas-6a9374295/" target="_blank">
    <img src="https://img.shields.io/badge/Muhammad%20Abbas%20-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white" alt="Muhammad Abbas"/>
  </a>
</div>

