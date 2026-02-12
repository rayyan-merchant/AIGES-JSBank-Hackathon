
import sys
from unittest.mock import MagicMock
sys.modules["cv2"] = MagicMock()

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import EvalCallback
from src.rl.bank_env import BankLendingEnv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_DIR = 'models'

def train():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    
    logger.info("Creating environment...")
    env = BankLendingEnv(seed=42)
    
    logger.info("Initializing PPO agent...")
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        seed=42,
        gamma=0.99,
        learning_rate=3e-4,
        batch_size=256,
        n_steps=2048,
        n_epochs=10
    )
    
    logger.info("Training for 200k timesteps...")
    model.learn(total_timesteps=200_000)
    
    save_path = os.path.join(MODEL_DIR, 'ppo_lending_agent')
    model.save(save_path)
    logger.info(f"Agent saved to {save_path}.zip")
    
    print("PPO Training Complete!")

if __name__ == "__main__":
    train()
