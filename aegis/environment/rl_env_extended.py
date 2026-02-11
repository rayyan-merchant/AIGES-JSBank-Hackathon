import numpy as np

class RLEnvironment:
    def __init__(self, state_dim=8, action_dim=4, seed=42):
        self.state_dim = int(state_dim)
        self.action_dim = int(action_dim)
        self.rng = np.random.default_rng(seed)
        self.state = np.zeros(self.state_dim, dtype=float)
        self.t = 0

    def reset(self):
        self.state = self.rng.normal(0.0, 0.1, size=self.state_dim)
        self.t = 0
        return self.state.copy()

    def step(self, action):
        a = np.asarray(action, dtype=float)
        if a.shape == ():
            a = np.array([a])
        noise = self.rng.normal(0.0, 0.05, size=self.state_dim)
        self.state = 0.9 * self.state + 0.1 * np.pad(a, (0, max(0, self.state_dim - a.size)))[:self.state_dim] + noise
        reward = self.compute_reward(self.state, a)
        self.t += 1
        done = self.t >= 64
        info = {"t": self.t}
        return self.state.copy(), float(reward), bool(done), info

    def compute_reward(self, state, action):
        s = np.asarray(state, dtype=float)
        a = np.asarray(action, dtype=float)
        return -np.linalg.norm(s) - 0.01 * np.linalg.norm(a)
