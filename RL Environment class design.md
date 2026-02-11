# RL ENVIRONMENT CLASS DESIGN

Now we formalize the environment.

---

# 1️⃣ STATE SPACE

State vector ( S_t ):

```
[
 revenue_t,
 cash_t,
 debt_ratio,
 volatility,
 trend,
 risk_score,
 macro_state,
 months_since_loan_start,
 industry_embedding
]
```

All normalized to [-1,1] or [0,1].

---

# 2️⃣ ACTION SPACE

Discrete:

```
0 = do_nothing
1 = restructure_loan
2 = reduce_interest
3 = increase_interest
4 = extend_duration
5 = offer_discount
6 = aggressive_collection
```

---

# 3️⃣ TRANSITION FUNCTION

Environment uses:

```
Revenue_{t+1} formula
Cash update equation
PD recalculation
```

Actions modify:

* interest rate
* duration
* payment burden
* probability weights

Example:

If restructure_loan:

```
r_i = r_i - 0.02
Duration += 6
```

---

# 4️⃣ REWARD FUNCTION

Goal: maximize profit, minimize default.

Monthly reward:

[
R_t =
InterestIncome_t

* DefaultLoss_t
* InterventionCost_t
  ]

---

## 4.1 Interest Income

[
InterestIncome =
OutstandingLoan \times r_i / 12
]

---

## 4.2 Default Loss

If default:

[
Loss = LGD \times OutstandingLoan
]

LGD ≈ 0.6

---

## 4.3 Reward Scaling

To stabilize PPO:

[
R'_t = \frac{R_t}{10000}
]

Clip:

[
R'_t \in [-10, 10]
]

---

# 5️⃣ TERMINATION CONDITIONS

Episode ends if:

* Default occurs
* Loan fully repaid
* Month = T

---

# 6️⃣ ENV CLASS STRUCTURE (PYTHON DESIGN)

```
class SMEEnvironment(gym.Env):

    def __init__(self, sme_dataset):
        self.dataset = sme_dataset
        self.current_state = None
        self.current_step = 0

    def reset(self):
        self.sample_new_sme()
        self.current_step = 0
        return self.state

    def step(self, action):
        self.apply_action(action)
        self.update_revenue()
        self.update_cash()
        self.compute_pd()
        reward = self.compute_reward()
        done = self.check_termination()
        return self.state, reward, done, info
```

Multi-agent version:

```
BankAgent
SMEAgent
NegotiationLoop
```

