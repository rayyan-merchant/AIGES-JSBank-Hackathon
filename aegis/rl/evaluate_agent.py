
import sys
from unittest.mock import MagicMock
sys.modules["cv2"] = MagicMock()

import os
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from stable_baselines3 import PPO
from src.rl.bank_env import BankLendingEnv

MODEL_DIR = 'models'
RESULTS_DIR = 'outputs'
N_EVAL = 1000

def rule_based_strategy(obs, env):
    
    pd_score = env.pd_score
    if pd_score < 0.15:
        return np.array([0.0, 1.0, 1.0], dtype=np.float32)
    else:
        return np.array([0.02, 0.8, 0.0], dtype=np.float32)

def pd_threshold_strategy(obs, env):
    
    pd_score = env.pd_score
    threshold = 0.10
    if pd_score < threshold:
        rate_adj = 0.01 * pd_score / threshold
        return np.array([rate_adj, 1.0, 1.0], dtype=np.float32)
    else:
        return np.array([0.05, 0.5, 0.0], dtype=np.float32)

def evaluate_strategy(strategy_fn, env, n_episodes, use_model=False, model=None):
    
    total_profit = 0
    total_defaults = 0
    total_approved = 0
    total_episodes = 0
    capital_history = []
    
    for ep in range(n_episodes):
        obs, info = env.reset(seed=ep)
        ep_reward = 0
        ep_defaults = 0
        ep_approved = 0
        
        for step in range(env.MAX_MONTHS):
            if use_model:
                action, _ = model.predict(obs, deterministic=True)
            else:
                action = strategy_fn(obs, env)
            
            obs, reward, terminated, truncated, info = env.step(action)
            ep_reward += reward
            
            if action[2] > 0.5:
                ep_approved += 1
            if info.get('defaulted', False):
                ep_defaults += 1
            
            if terminated or truncated:
                break
        
        total_profit += ep_reward
        total_defaults += ep_defaults
        total_approved += ep_approved
        total_episodes += 1
        capital_history.append(env.bank_capital)
    
    avg_profit = total_profit / total_episodes
    default_rate = total_defaults / max(1, total_approved)
    risk_adj_return = avg_profit / (1 + default_rate)
    
    return {
        'total_profit': total_profit,
        'avg_profit': avg_profit,
        'default_rate': default_rate,
        'total_defaults': total_defaults,
        'total_approved': total_approved,
        'risk_adjusted_return': risk_adj_return,
        'avg_final_capital': np.mean(capital_history)
    }

def main():
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    
    env = BankLendingEnv(seed=42)
    
    ppo_path = os.path.join(MODEL_DIR, 'ppo_lending_agent.zip')
    ppo_model = None
    if os.path.exists(ppo_path):
        ppo_model = PPO.load(ppo_path)
        print("PPO model loaded.")
    else:
        print(f"Warning: PPO model not found at {ppo_path}. Skipping PPO evaluation.")
    
    results = {}
    
    print("\nEvaluating Rule-Based Strategy...")
    results['rule_based'] = evaluate_strategy(rule_based_strategy, env, N_EVAL)
    print(f"  Profit: {results['rule_based']['total_profit']:.2f}")
    print(f"  Default Rate: {results['rule_based']['default_rate']:.4f}")
    
    print("\nEvaluating PD-Threshold Strategy...")
    results['pd_threshold'] = evaluate_strategy(pd_threshold_strategy, env, N_EVAL)
    print(f"  Profit: {results['pd_threshold']['total_profit']:.2f}")
    print(f"  Default Rate: {results['pd_threshold']['default_rate']:.4f}")
    
    if ppo_model:
        print("\nEvaluating PPO Agent...")
        results['ppo_agent'] = evaluate_strategy(None, env, N_EVAL, use_model=True, model=ppo_model)
        print(f"  Profit: {results['ppo_agent']['total_profit']:.2f}")
        print(f"  Default Rate: {results['ppo_agent']['default_rate']:.4f}")
    
    rows = []
    for name, metrics in results.items():
        row = {'strategy': name}
        row.update(metrics)
        rows.append(row)
    
    df = pd.DataFrame(rows)
    out_path = os.path.join(RESULTS_DIR, 'evaluation_results.csv')
    df.to_csv(out_path, index=False)
    print(f"\nResults saved to {out_path}")
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()
