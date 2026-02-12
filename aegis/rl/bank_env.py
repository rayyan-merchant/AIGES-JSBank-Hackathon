
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
import os
import pickle
import logging

logger = logging.getLogger(__name__)

class BankLendingEnv(gym.Env):
    
    metadata = {'render_modes': ['human']}
    
    def __init__(self, customer_data=None, config=None, seed=42):
        super().__init__()
        
        self.seed_val = seed
        self.rng = np.random.default_rng(seed)
        
        self.config = config or {}
        self.LGD = self.config.get('lgd', 0.6)
        self.RISK_LAMBDA = self.config.get('risk_lambda', 0.1)
        self.MAX_MONTHS = self.config.get('max_months', 36)
        self.INITIAL_CAPITAL = self.config.get('initial_capital', 1_000_000)
        self.REWARD_SCALE = self.config.get('reward_scale', 10000)
        
        if customer_data is not None:
            self.customer_pool = customer_data
        else:
            self.customer_pool = self._generate_synthetic_pool(1000)
        
        self.n_customers = len(self.customer_pool)
        
        self.n_customer_features = 5
        
        self.state_dim = 11
        self.observation_space = spaces.Box(low=-1.0, high=1.0, shape=(self.state_dim,), dtype=np.float32)
        
        self.action_space = spaces.Box(
            low=np.array([-0.05, 0.5, 0.0], dtype=np.float32),
            high=np.array([0.05, 1.5, 1.0], dtype=np.float32),
            dtype=np.float32
        )
        
        self.bank_capital = self.INITIAL_CAPITAL
        self.risk_budget = 1.0
        self.macro_factor = 1.0
        
        self.current_customer = None
        self.current_step = 0
        self.outstanding_loan = 0
        self.interest_rate = 0
        self.pd_score = 0
        self.total_profit = 0
        self.n_defaults = 0
        self.n_approved = 0
        self.episode_log = []
        
    def _generate_synthetic_pool(self, n):
        
        rng = self.rng
        pool = pd.DataFrame({
            'pd_score': rng.beta(2, 10, n),
            'income': rng.lognormal(11, 0.8, n),
            'credit_amount': rng.lognormal(12, 0.5, n),
            'annuity': rng.lognormal(9, 0.5, n),
            'ext_source': rng.beta(5, 3, n),
            'loan_amount': rng.lognormal(11.5, 0.6, n),
            'base_interest': rng.uniform(0.05, 0.15, n),
            'duration': rng.integers(12, 48, n)
        })
        return pool
    
    def _normalize(self, val, low, high):
        
        return np.clip(2 * (val - low) / (high - low + 1e-8) - 1, -1, 1)
    
    def _get_state(self):
        
        c = self.current_customer
        
        state = np.array([
            self._normalize(self.pd_score, 0, 1),
            self._normalize(self.outstanding_loan, 0, 500000),
            self._normalize(self.interest_rate, 0, 0.3),
            self._normalize(c['income'], 0, 500000),
            self._normalize(c['credit_amount'], 0, 1000000),
            self._normalize(c['annuity'], 0, 50000),
            self._normalize(c['ext_source'], 0, 1),
            self._normalize(c.get('duration', 24), 0, 48),
            self._normalize(self.bank_capital, 0, 2 * self.INITIAL_CAPITAL),
            self._normalize(self.risk_budget, 0, 1),
            self._normalize(self.macro_factor, 0.5, 1.5)
        ], dtype=np.float32)
        
        return state
    
    def reset(self, seed=None, options=None):
        
        super().reset(seed=seed)
        
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        
        idx = self.rng.integers(0, self.n_customers)
        self.current_customer = self.customer_pool.iloc[idx].to_dict()
        
        self.current_step = 0
        self.outstanding_loan = self.current_customer['loan_amount']
        self.interest_rate = self.current_customer['base_interest']
        self.pd_score = self.current_customer['pd_score']
        self.total_profit = 0
        self.n_defaults = 0
        self.n_approved = 0
        self.episode_log = []
        
        self.macro_factor = 1.0 + self.rng.normal(0, 0.05)
        
        self.risk_budget = 1.0
        
        return self._get_state(), {}
    
    def compute_reward(self, action_approve):
        
        if not action_approve:
            return -0.01
        
        interest_income = self.outstanding_loan * self.interest_rate / 12
        
        expected_loss = self.pd_score * self.LGD * self.outstanding_loan
        
        expected_profit = (1 - self.pd_score) * interest_income - self.pd_score * expected_loss
        
        capital_consumption = self.pd_score * self.outstanding_loan * 0.08
        risk_penalty = self.RISK_LAMBDA * capital_consumption
        
        raw_reward = expected_profit - risk_penalty
        
        scaled_reward = raw_reward / self.REWARD_SCALE
        clipped_reward = np.clip(scaled_reward, -10, 10)
        
        return float(clipped_reward)
    
    def update_bank_state(self, action_approve):
        
        if action_approve:
            self.n_approved += 1
            capital_charge = self.pd_score * self.outstanding_loan * 0.08
            self.bank_capital -= capital_charge
            self.risk_budget -= self.pd_score * 0.005
            self.risk_budget = max(0, self.risk_budget)
            
            monthly_pd = self.pd_score / 12.0
            
            if self.rng.random() < monthly_pd:
                loss = self.LGD * self.outstanding_loan
                self.bank_capital -= loss
                self.n_defaults += 1
                self.outstanding_loan *= (1 - self.LGD)
                return True
            else:
                monthly_payment = self.outstanding_loan * self.interest_rate / 12
                remaining_months = max(1, (self.MAX_MONTHS - self.current_step))
                principal_payment = self.outstanding_loan / remaining_months
                self.bank_capital += monthly_payment + principal_payment
                self.outstanding_loan -= principal_payment
                self.outstanding_loan = max(0, self.outstanding_loan)
        
        return False
    
    def step(self, action):
        
        self.current_step += 1
        
        int_rate_adj = float(action[0])
        loan_multiplier = float(action[1])
        approve = float(action[2]) > 0.5
        
        self.interest_rate = np.clip(self.interest_rate + int_rate_adj, 0.01, 0.25)
        self.outstanding_loan *= loan_multiplier
        
        pd_adj = 0.02 * int_rate_adj / 0.05
        macro_adj = (1 - self.macro_factor) * 0.05
        self.pd_score = np.clip(self.pd_score + pd_adj + macro_adj, 0.001, 0.99)
        
        reward = self.compute_reward(approve)
        
        defaulted = self.update_bank_state(approve)
        
        self.macro_factor += self.rng.normal(0, 0.02)
        self.macro_factor = np.clip(self.macro_factor, 0.7, 1.3)
        
        terminated = False
        truncated = False
        
        if defaulted:
            reward -= 2.0
        
        if self.outstanding_loan <= 0:
            reward += 0.5
            idx = self.rng.integers(0, self.n_customers)
            self.current_customer = self.customer_pool.iloc[idx].to_dict()
            self.outstanding_loan = self.current_customer['loan_amount']
            self.interest_rate = self.current_customer['base_interest']
            self.pd_score = self.current_customer['pd_score']
        
        if self.current_step >= self.MAX_MONTHS:
            truncated = True
        elif self.bank_capital <= 0:
            terminated = True
            reward = -10.0
        
        self.episode_log.append({
            'step': self.current_step,
            'action_approve': approve,
            'interest_rate': self.interest_rate,
            'loan_outstanding': self.outstanding_loan,
            'pd_score': self.pd_score,
            'reward': reward,
            'bank_capital': self.bank_capital,
            'macro': self.macro_factor,
            'defaulted': defaulted
        })
        
        info = {
            'profit': self.total_profit,
            'defaulted': defaulted,
            'bank_capital': self.bank_capital,
            'n_defaults': self.n_defaults,
            'n_approved': self.n_approved
        }
        self.total_profit += reward
        
        return self._get_state(), reward, terminated, truncated, info
    
    def render(self, mode='human'):
        if self.episode_log:
            last = self.episode_log[-1]
            print(f"Step {last['step']}: Approve={last['action_approve']}, "
                  f"Rate={last['interest_rate']:.4f}, Loan={last['loan_outstanding']:.0f}, "
                  f"PD={last['pd_score']:.4f}, Reward={last['reward']:.4f}, "
                  f"Capital={last['bank_capital']:.0f}")


if __name__ == "__main__":
    env = BankLendingEnv(seed=42)
    obs, info = env.reset()
    print(f"Initial state shape: {obs.shape}")
    print(f"Initial state: {obs}")
    
    total_reward = 0
    for i in range(10):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        env.render()
        if terminated or truncated:
            break
    
    print(f"\nTotal reward: {total_reward:.4f}")
    print("Environment test passed!")
